"""Property-based tests for semantic parser service.

This module uses hypothesis to verify that semantic parsing properties hold across
many random inputs, ensuring parse result structure integrity.

Requirements: 3.3
"""

import pytest
import json
from unittest.mock import Mock, patch

from hypothesis import given, strategies as st
from hypothesis import settings

from app.semantic_parser import SemanticParserService, SemanticParserError
from app.models import ParsedData, MoodData, InspirationData, TodoData


# Custom strategies for generating API responses
@st.composite
def api_mood_response_strategy(draw):
    """Generate valid mood data for API responses."""
    has_mood = draw(st.booleans())
    if not has_mood:
        return None
    
    return {
        "type": draw(st.one_of(st.none(), st.text(min_size=1, max_size=20))),
        "intensity": draw(st.one_of(st.none(), st.integers(min_value=1, max_value=10))),
        "keywords": draw(st.lists(st.text(min_size=1, max_size=15), min_size=0, max_size=5))
    }


@st.composite
def api_inspiration_response_strategy(draw):
    """Generate valid inspiration data for API responses."""
    core_idea = draw(st.text(min_size=1, max_size=20))
    tags = draw(st.lists(st.text(min_size=1, max_size=10), min_size=0, max_size=5))
    category = draw(st.sampled_from(["工作", "生活", "学习", "创意"]))
    
    return {
        "core_idea": core_idea,
        "tags": tags,
        "category": category
    }


@st.composite
def api_todo_response_strategy(draw):
    """Generate valid todo data for API responses."""
    task = draw(st.text(min_size=1, max_size=50))
    time = draw(st.one_of(st.none(), st.text(min_size=1, max_size=20)))
    location = draw(st.one_of(st.none(), st.text(min_size=1, max_size=20)))
    
    return {
        "task": task,
        "time": time,
        "location": location
    }


@st.composite
def api_parsed_response_strategy(draw):
    """Generate valid parsed data for API responses."""
    mood = draw(api_mood_response_strategy())
    inspirations = draw(st.lists(api_inspiration_response_strategy(), min_size=0, max_size=3))
    todos = draw(st.lists(api_todo_response_strategy(), min_size=0, max_size=3))
    
    return {
        "mood": mood,
        "inspirations": inspirations,
        "todos": todos
    }


class TestSemanticParserServiceProperties:
    """Property-based tests for SemanticParserService.
    
    **Validates: Requirements 3.3**
    """
    
    @given(
        text=st.text(min_size=1, max_size=200),
        api_response=api_parsed_response_strategy()
    )
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_property_4_parse_result_structure_integrity(self, text, api_response):
        """
        Property 4: 解析结果结构完整性
        
        For any successful semantic parsing result, the returned JSON should contain
        mood, inspirations, and todos fields, even if some fields are null or empty arrays.
        
        **Validates: Requirements 3.3**
        """
        # Create service instance
        service = SemanticParserService(api_key="test-api-key")
        
        try:
            # Mock the API response
            # Note: httpx Response.json() is NOT async, so use regular Mock
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(api_response, ensure_ascii=False)
                        }
                    }
                ]
            }
            
            # Patch the HTTP client's post method (which IS async)
            async def mock_post(*args, **kwargs):
                return mock_response
            
            with patch.object(service.client, 'post', side_effect=mock_post):
                # Call parse method
                result = await service.parse(text)
                
                # Property 1: Result should be a ParsedData instance
                assert isinstance(result, ParsedData), \
                    "Parse result should be a ParsedData instance"
                
                # Property 2: Result should have mood field (even if None)
                assert hasattr(result, 'mood'), \
                    "Parse result should have 'mood' field"
                
                # Property 3: Result should have inspirations field (even if empty list)
                assert hasattr(result, 'inspirations'), \
                    "Parse result should have 'inspirations' field"
                assert isinstance(result.inspirations, list), \
                    "Inspirations should be a list"
                
                # Property 4: Result should have todos field (even if empty list)
                assert hasattr(result, 'todos'), \
                    "Parse result should have 'todos' field"
                assert isinstance(result.todos, list), \
                    "Todos should be a list"
                
                # Property 5: If mood exists in API response, it should be in result
                if api_response["mood"] is not None:
                    # Mood might be None if validation fails, but field should exist
                    assert result.mood is None or isinstance(result.mood, MoodData), \
                        "Mood should be None or MoodData instance"
                else:
                    assert result.mood is None, \
                        "Mood should be None when not in API response"
                
                # Property 6: Inspirations count should match valid entries
                # (Some might be filtered out due to validation errors)
                assert len(result.inspirations) <= len(api_response["inspirations"]), \
                    "Result inspirations count should not exceed API response count"
                
                for inspiration in result.inspirations:
                    assert isinstance(inspiration, InspirationData), \
                        "Each inspiration should be an InspirationData instance"
                
                # Property 7: Todos count should match valid entries
                # (Some might be filtered out due to validation errors)
                assert len(result.todos) <= len(api_response["todos"]), \
                    "Result todos count should not exceed API response count"
                
                for todo in result.todos:
                    assert isinstance(todo, TodoData), \
                        "Each todo should be a TodoData instance"
                    assert todo.status == "pending", \
                        "New todos should have status 'pending'"
        
        finally:
            # Clean up
            await service.close()
    
    @given(
        text=st.text(min_size=1, max_size=200),
        has_mood=st.booleans(),
        has_inspirations=st.booleans(),
        has_todos=st.booleans()
    )
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_property_4_parse_result_structure_with_missing_dimensions(
        self, text, has_mood, has_inspirations, has_todos
    ):
        """
        Property 4: 解析结果结构完整性 - Missing Dimensions
        
        For any parsing result, even when some dimensions are missing from the API
        response, the result should still contain all three fields (mood, inspirations, todos).
        
        **Validates: Requirements 3.3**
        """
        # Create service instance
        service = SemanticParserService(api_key="test-api-key")
        
        try:
            # Build API response based on flags
            api_response = {}
            
            if has_mood:
                api_response["mood"] = {
                    "type": "开心",
                    "intensity": 8,
                    "keywords": ["愉快", "放松"]
                }
            else:
                api_response["mood"] = None
            
            if has_inspirations:
                api_response["inspirations"] = [
                    {
                        "core_idea": "新想法",
                        "tags": ["创新"],
                        "category": "工作"
                    }
                ]
            else:
                api_response["inspirations"] = []
            
            if has_todos:
                api_response["todos"] = [
                    {
                        "task": "完成任务",
                        "time": "明天",
                        "location": "办公室"
                    }
                ]
            else:
                api_response["todos"] = []
            
            # Mock the API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(api_response, ensure_ascii=False)
                        }
                    }
                ]
            }
            
            # Patch the HTTP client's post method (which IS async)
            async def mock_post(*args, **kwargs):
                return mock_response
            
            with patch.object(service.client, 'post', side_effect=mock_post):
                # Call parse method
                result = await service.parse(text)
                
                # Property 1: Result should always have all three fields
                assert hasattr(result, 'mood'), \
                    "Parse result should always have 'mood' field"
                assert hasattr(result, 'inspirations'), \
                    "Parse result should always have 'inspirations' field"
                assert hasattr(result, 'todos'), \
                    "Parse result should always have 'todos' field"
                
                # Property 2: Field types should be correct
                assert result.mood is None or isinstance(result.mood, MoodData), \
                    "Mood should be None or MoodData instance"
                assert isinstance(result.inspirations, list), \
                    "Inspirations should be a list"
                assert isinstance(result.todos, list), \
                    "Todos should be a list"
                
                # Property 3: Empty dimensions should be represented correctly
                if not has_mood:
                    assert result.mood is None, \
                        "Mood should be None when not present in API response"
                
                if not has_inspirations:
                    assert result.inspirations == [], \
                        "Inspirations should be empty list when not present in API response"
                
                if not has_todos:
                    assert result.todos == [], \
                        "Todos should be empty list when not present in API response"
        
        finally:
            # Clean up
            await service.close()
    
    @given(
        text=st.text(min_size=1, max_size=200)
    )
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_property_4_parse_result_structure_with_empty_response(self, text):
        """
        Property 4: 解析结果结构完整性 - Empty Response
        
        For any text that results in an empty parsing response (no mood, no inspirations,
        no todos), the result should still contain all three fields with appropriate
        null/empty values.
        
        **Validates: Requirements 3.3**
        """
        # Create service instance
        service = SemanticParserService(api_key="test-api-key")
        
        try:
            # Build completely empty API response
            api_response = {
                "mood": None,
                "inspirations": [],
                "todos": []
            }
            
            # Mock the API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(api_response, ensure_ascii=False)
                        }
                    }
                ]
            }
            
            # Patch the HTTP client's post method (which IS async)
            async def mock_post(*args, **kwargs):
                return mock_response
            
            with patch.object(service.client, 'post', side_effect=mock_post):
                # Call parse method
                result = await service.parse(text)
                
                # Property 1: Result should be a valid ParsedData instance
                assert isinstance(result, ParsedData), \
                    "Parse result should be a ParsedData instance even with empty response"
                
                # Property 2: All three fields should exist
                assert hasattr(result, 'mood'), \
                    "Parse result should have 'mood' field even when empty"
                assert hasattr(result, 'inspirations'), \
                    "Parse result should have 'inspirations' field even when empty"
                assert hasattr(result, 'todos'), \
                    "Parse result should have 'todos' field even when empty"
                
                # Property 3: Empty values should be represented correctly
                assert result.mood is None, \
                    "Mood should be None for empty response"
                assert result.inspirations == [], \
                    "Inspirations should be empty list for empty response"
                assert result.todos == [], \
                    "Todos should be empty list for empty response"
        
        finally:
            # Clean up
            await service.close()
    
    @given(
        text=st.text(min_size=1, max_size=200),
        api_response=api_parsed_response_strategy()
    )
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_property_4_parse_result_structure_with_markdown_json(
        self, text, api_response
    ):
        """
        Property 4: 解析结果结构完整性 - Markdown JSON Response
        
        For any API response that wraps JSON in markdown code blocks (```json...```),
        the parser should still extract the JSON and return a properly structured result.
        
        **Validates: Requirements 3.3**
        """
        # Create service instance
        service = SemanticParserService(api_key="test-api-key")
        
        try:
            # Wrap the JSON response in markdown code blocks
            json_content = json.dumps(api_response, ensure_ascii=False)
            markdown_content = f"```json\n{json_content}\n```"
            
            # Mock the API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": markdown_content
                        }
                    }
                ]
            }
            
            # Patch the HTTP client's post method (which IS async)
            async def mock_post(*args, **kwargs):
                return mock_response
            
            with patch.object(service.client, 'post', side_effect=mock_post):
                # Call parse method
                result = await service.parse(text)
                
                # Property 1: Result should be a valid ParsedData instance
                assert isinstance(result, ParsedData), \
                    "Parse result should be a ParsedData instance even with markdown-wrapped JSON"
                
                # Property 2: All three fields should exist
                assert hasattr(result, 'mood'), \
                    "Parse result should have 'mood' field"
                assert hasattr(result, 'inspirations'), \
                    "Parse result should have 'inspirations' field"
                assert hasattr(result, 'todos'), \
                    "Parse result should have 'todos' field"
                
                # Property 3: Field types should be correct
                assert result.mood is None or isinstance(result.mood, MoodData), \
                    "Mood should be None or MoodData instance"
                assert isinstance(result.inspirations, list), \
                    "Inspirations should be a list"
                assert isinstance(result.todos, list), \
                    "Todos should be a list"
        
        finally:
            # Clean up
            await service.close()
    
    @given(
        text=st.text(min_size=1, max_size=200),
        num_inspirations=st.integers(min_value=0, max_value=5),
        num_todos=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_property_4_parse_result_structure_with_multiple_items(
        self, text, num_inspirations, num_todos
    ):
        """
        Property 4: 解析结果结构完整性 - Multiple Items
        
        For any parsing result with multiple inspirations and todos, the result
        should maintain proper structure with all items preserved as lists.
        
        **Validates: Requirements 3.3**
        """
        # Create service instance
        service = SemanticParserService(api_key="test-api-key")
        
        try:
            # Build API response with multiple items
            api_response = {
                "mood": {
                    "type": "平静",
                    "intensity": 5,
                    "keywords": ["放松"]
                },
                "inspirations": [
                    {
                        "core_idea": f"想法{i}",
                        "tags": [f"标签{i}"],
                        "category": "生活"
                    }
                    for i in range(num_inspirations)
                ],
                "todos": [
                    {
                        "task": f"任务{i}",
                        "time": f"时间{i}",
                        "location": f"地点{i}"
                    }
                    for i in range(num_todos)
                ]
            }
            
            # Mock the API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(api_response, ensure_ascii=False)
                        }
                    }
                ]
            }
            
            # Patch the HTTP client's post method (which IS async)
            async def mock_post(*args, **kwargs):
                return mock_response
            
            with patch.object(service.client, 'post', side_effect=mock_post):
                # Call parse method
                result = await service.parse(text)
                
                # Property 1: Result should have all three fields
                assert hasattr(result, 'mood'), \
                    "Parse result should have 'mood' field"
                assert hasattr(result, 'inspirations'), \
                    "Parse result should have 'inspirations' field"
                assert hasattr(result, 'todos'), \
                    "Parse result should have 'todos' field"
                
                # Property 2: Lists should contain correct number of items
                assert len(result.inspirations) == num_inspirations, \
                    f"Should have {num_inspirations} inspirations"
                assert len(result.todos) == num_todos, \
                    f"Should have {num_todos} todos"
                
                # Property 3: All items should be properly typed
                for inspiration in result.inspirations:
                    assert isinstance(inspiration, InspirationData), \
                        "Each inspiration should be an InspirationData instance"
                
                for todo in result.todos:
                    assert isinstance(todo, TodoData), \
                        "Each todo should be a TodoData instance"
                
                # Property 4: Mood should be present
                assert isinstance(result.mood, MoodData), \
                    "Mood should be a MoodData instance"
        
        finally:
            # Clean up
            await service.close()

    @given(
        text=st.text(min_size=1, max_size=200),
        include_mood=st.booleans(),
        include_inspirations=st.booleans(),
        include_todos=st.booleans()
    )
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_property_5_missing_dimension_handling(
        self, text, include_mood, include_inspirations, include_todos
    ):
        """
        Property 5: 缺失维度处理
        
        For any text that does not contain specific dimension information,
        the parsing result should return null for mood or empty arrays for
        inspirations and todos.
        
        **Validates: Requirements 3.4**
        """
        # Create service instance
        service = SemanticParserService(api_key="test-api-key")
        
        try:
            # Build API response with selective dimensions
            api_response = {}
            
            # Only include dimensions based on flags
            if include_mood:
                api_response["mood"] = {
                    "type": "开心",
                    "intensity": 7,
                    "keywords": ["愉快"]
                }
            else:
                # Explicitly set to None to simulate missing dimension
                api_response["mood"] = None
            
            if include_inspirations:
                api_response["inspirations"] = [
                    {
                        "core_idea": "测试想法",
                        "tags": ["测试"],
                        "category": "学习"
                    }
                ]
            else:
                # Empty array for missing dimension
                api_response["inspirations"] = []
            
            if include_todos:
                api_response["todos"] = [
                    {
                        "task": "测试任务",
                        "time": "今天",
                        "location": None
                    }
                ]
            else:
                # Empty array for missing dimension
                api_response["todos"] = []
            
            # Mock the API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(api_response, ensure_ascii=False)
                        }
                    }
                ]
            }
            
            # Patch the HTTP client's post method
            async def mock_post(*args, **kwargs):
                return mock_response
            
            with patch.object(service.client, 'post', side_effect=mock_post):
                # Call parse method
                result = await service.parse(text)
                
                # Property 1: Missing mood should return None
                if not include_mood:
                    assert result.mood is None, \
                        "When text does not contain mood information, mood should be None"
                else:
                    assert result.mood is not None, \
                        "When text contains mood information, mood should not be None"
                    assert isinstance(result.mood, MoodData), \
                        "Mood should be a MoodData instance when present"
                
                # Property 2: Missing inspirations should return empty array
                if not include_inspirations:
                    assert result.inspirations == [], \
                        "When text does not contain inspiration information, inspirations should be empty array"
                    assert isinstance(result.inspirations, list), \
                        "Inspirations should always be a list"
                else:
                    assert len(result.inspirations) > 0, \
                        "When text contains inspiration information, inspirations should not be empty"
                    for inspiration in result.inspirations:
                        assert isinstance(inspiration, InspirationData), \
                            "Each inspiration should be an InspirationData instance"
                
                # Property 3: Missing todos should return empty array
                if not include_todos:
                    assert result.todos == [], \
                        "When text does not contain todo information, todos should be empty array"
                    assert isinstance(result.todos, list), \
                        "Todos should always be a list"
                else:
                    assert len(result.todos) > 0, \
                        "When text contains todo information, todos should not be empty"
                    for todo in result.todos:
                        assert isinstance(todo, TodoData), \
                            "Each todo should be a TodoData instance"
                
                # Property 4: Result structure should always be complete
                assert hasattr(result, 'mood'), \
                    "Result should always have mood field"
                assert hasattr(result, 'inspirations'), \
                    "Result should always have inspirations field"
                assert hasattr(result, 'todos'), \
                    "Result should always have todos field"
        
        finally:
            # Clean up
            await service.close()
    
    @given(text=st.text(min_size=1, max_size=200))
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_property_5_all_dimensions_missing(self, text):
        """
        Property 5: 缺失维度处理 - All Dimensions Missing
        
        For any text where all dimensions are missing, the result should have
        null mood and empty arrays for inspirations and todos.
        
        **Validates: Requirements 3.4**
        """
        # Create service instance
        service = SemanticParserService(api_key="test-api-key")
        
        try:
            # Build API response with all dimensions missing
            api_response = {
                "mood": None,
                "inspirations": [],
                "todos": []
            }
            
            # Mock the API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(api_response, ensure_ascii=False)
                        }
                    }
                ]
            }
            
            # Patch the HTTP client's post method
            async def mock_post(*args, **kwargs):
                return mock_response
            
            with patch.object(service.client, 'post', side_effect=mock_post):
                # Call parse method
                result = await service.parse(text)
                
                # Property 1: All dimensions should be properly represented as missing
                assert result.mood is None, \
                    "Mood should be None when all dimensions are missing"
                assert result.inspirations == [], \
                    "Inspirations should be empty array when all dimensions are missing"
                assert result.todos == [], \
                    "Todos should be empty array when all dimensions are missing"
                
                # Property 2: Result should still be a valid ParsedData instance
                assert isinstance(result, ParsedData), \
                    "Result should be a valid ParsedData instance even with all dimensions missing"
        
        finally:
            # Clean up
            await service.close()
    
    @given(
        text=st.text(min_size=1, max_size=200),
        dimension=st.sampled_from(["mood", "inspirations", "todos"])
    )
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_property_5_single_dimension_missing(self, text, dimension):
        """
        Property 5: 缺失维度处理 - Single Dimension Missing
        
        For any text where only one dimension is missing, that dimension should
        return null (for mood) or empty array (for inspirations/todos), while
        other dimensions should be present.
        
        **Validates: Requirements 3.4**
        """
        # Create service instance
        service = SemanticParserService(api_key="test-api-key")
        
        try:
            # Build API response with one dimension missing
            api_response = {
                "mood": {
                    "type": "平静",
                    "intensity": 5,
                    "keywords": ["放松"]
                },
                "inspirations": [
                    {
                        "core_idea": "想法",
                        "tags": ["标签"],
                        "category": "生活"
                    }
                ],
                "todos": [
                    {
                        "task": "任务",
                        "time": "明天",
                        "location": "家"
                    }
                ]
            }
            
            # Remove the selected dimension
            if dimension == "mood":
                api_response["mood"] = None
            elif dimension == "inspirations":
                api_response["inspirations"] = []
            elif dimension == "todos":
                api_response["todos"] = []
            
            # Mock the API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(api_response, ensure_ascii=False)
                        }
                    }
                ]
            }
            
            # Patch the HTTP client's post method
            async def mock_post(*args, **kwargs):
                return mock_response
            
            with patch.object(service.client, 'post', side_effect=mock_post):
                # Call parse method
                result = await service.parse(text)
                
                # Property 1: Missing dimension should be properly represented
                if dimension == "mood":
                    assert result.mood is None, \
                        "Mood should be None when missing"
                    assert len(result.inspirations) > 0, \
                        "Inspirations should be present when not missing"
                    assert len(result.todos) > 0, \
                        "Todos should be present when not missing"
                elif dimension == "inspirations":
                    assert result.mood is not None, \
                        "Mood should be present when not missing"
                    assert result.inspirations == [], \
                        "Inspirations should be empty array when missing"
                    assert len(result.todos) > 0, \
                        "Todos should be present when not missing"
                elif dimension == "todos":
                    assert result.mood is not None, \
                        "Mood should be present when not missing"
                    assert len(result.inspirations) > 0, \
                        "Inspirations should be present when not missing"
                    assert result.todos == [], \
                        "Todos should be empty array when missing"
                
                # Property 2: All fields should exist regardless
                assert hasattr(result, 'mood'), \
                    "Result should always have mood field"
                assert hasattr(result, 'inspirations'), \
                    "Result should always have inspirations field"
                assert hasattr(result, 'todos'), \
                    "Result should always have todos field"
        
        finally:
            # Clean up
            await service.close()
