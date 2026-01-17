"""Unit tests for data models.

This module tests the Pydantic data models to ensure proper validation,
serialization, and constraint enforcement.

Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 6.4
"""

import pytest
from pydantic import ValidationError

from app.models import (
    MoodData,
    InspirationData,
    TodoData,
    ParsedData,
    RecordData,
    ProcessResponse
)


class TestMoodData:
    """Tests for MoodData model.
    
    Requirements: 4.1, 4.2, 4.3
    """
    
    def test_mood_data_valid(self):
        """Test creating valid MoodData."""
        mood = MoodData(
            type="开心",
            intensity=8,
            keywords=["愉快", "放松"]
        )
        assert mood.type == "开心"
        assert mood.intensity == 8
        assert mood.keywords == ["愉快", "放松"]
    
    def test_mood_data_optional_fields(self):
        """Test MoodData with optional fields as None."""
        mood = MoodData()
        assert mood.type is None
        assert mood.intensity is None
        assert mood.keywords == []
    
    def test_mood_data_intensity_min_boundary(self):
        """Test MoodData intensity minimum boundary (1)."""
        mood = MoodData(type="平静", intensity=1)
        assert mood.intensity == 1
    
    def test_mood_data_intensity_max_boundary(self):
        """Test MoodData intensity maximum boundary (10)."""
        mood = MoodData(type="兴奋", intensity=10)
        assert mood.intensity == 10
    
    def test_mood_data_intensity_below_min(self):
        """Test MoodData rejects intensity below 1."""
        with pytest.raises(ValidationError) as exc_info:
            MoodData(type="平静", intensity=0)
        assert "greater than or equal to 1" in str(exc_info.value)
    
    def test_mood_data_intensity_above_max(self):
        """Test MoodData rejects intensity above 10."""
        with pytest.raises(ValidationError) as exc_info:
            MoodData(type="兴奋", intensity=11)
        assert "less than or equal to 10" in str(exc_info.value)
    
    def test_mood_data_empty_keywords(self):
        """Test MoodData with empty keywords list."""
        mood = MoodData(type="中性", intensity=5, keywords=[])
        assert mood.keywords == []


class TestInspirationData:
    """Tests for InspirationData model.
    
    Requirements: 5.1, 5.2, 5.3
    """
    
    def test_inspiration_data_valid(self):
        """Test creating valid InspirationData."""
        inspiration = InspirationData(
            core_idea="新的项目想法",
            tags=["创新", "技术"],
            category="工作"
        )
        assert inspiration.core_idea == "新的项目想法"
        assert inspiration.tags == ["创新", "技术"]
        assert inspiration.category == "工作"
    
    def test_inspiration_data_core_idea_max_length(self):
        """Test InspirationData core_idea at max length (20 characters)."""
        # Exactly 20 characters
        core_idea = "12345678901234567890"
        inspiration = InspirationData(
            core_idea=core_idea,
            tags=["测试"],
            category="学习"
        )
        assert len(inspiration.core_idea) == 20
    
    def test_inspiration_data_core_idea_exceeds_max_length(self):
        """Test InspirationData rejects core_idea exceeding 20 characters."""
        # 21 characters
        core_idea = "123456789012345678901"
        with pytest.raises(ValidationError) as exc_info:
            InspirationData(
                core_idea=core_idea,
                tags=["测试"],
                category="学习"
            )
        assert "at most 20 characters" in str(exc_info.value)
    
    def test_inspiration_data_tags_max_count(self):
        """Test InspirationData with maximum 5 tags."""
        inspiration = InspirationData(
            core_idea="想法",
            tags=["标签1", "标签2", "标签3", "标签4", "标签5"],
            category="创意"
        )
        assert len(inspiration.tags) == 5
    
    def test_inspiration_data_tags_exceeds_max_count(self):
        """Test InspirationData rejects more than 5 tags."""
        with pytest.raises(ValidationError) as exc_info:
            InspirationData(
                core_idea="想法",
                tags=["标签1", "标签2", "标签3", "标签4", "标签5", "标签6"],
                category="创意"
            )
        assert "at most 5 items" in str(exc_info.value)
    
    def test_inspiration_data_empty_tags(self):
        """Test InspirationData with empty tags list."""
        inspiration = InspirationData(
            core_idea="简单想法",
            tags=[],
            category="生活"
        )
        assert inspiration.tags == []
    
    def test_inspiration_data_category_work(self):
        """Test InspirationData with category '工作'."""
        inspiration = InspirationData(
            core_idea="工作想法",
            category="工作"
        )
        assert inspiration.category == "工作"
    
    def test_inspiration_data_category_life(self):
        """Test InspirationData with category '生活'."""
        inspiration = InspirationData(
            core_idea="生活想法",
            category="生活"
        )
        assert inspiration.category == "生活"
    
    def test_inspiration_data_category_study(self):
        """Test InspirationData with category '学习'."""
        inspiration = InspirationData(
            core_idea="学习想法",
            category="学习"
        )
        assert inspiration.category == "学习"
    
    def test_inspiration_data_category_creative(self):
        """Test InspirationData with category '创意'."""
        inspiration = InspirationData(
            core_idea="创意想法",
            category="创意"
        )
        assert inspiration.category == "创意"
    
    def test_inspiration_data_invalid_category(self):
        """Test InspirationData rejects invalid category."""
        with pytest.raises(ValidationError) as exc_info:
            InspirationData(
                core_idea="想法",
                category="无效分类"
            )
        assert "Input should be" in str(exc_info.value)


class TestTodoData:
    """Tests for TodoData model.
    
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    
    def test_todo_data_valid(self):
        """Test creating valid TodoData."""
        todo = TodoData(
            task="完成报告",
            time="明天下午",
            location="办公室",
            status="pending"
        )
        assert todo.task == "完成报告"
        assert todo.time == "明天下午"
        assert todo.location == "办公室"
        assert todo.status == "pending"
    
    def test_todo_data_default_status(self):
        """Test TodoData defaults status to 'pending'."""
        todo = TodoData(task="买菜")
        assert todo.status == "pending"
    
    def test_todo_data_optional_time(self):
        """Test TodoData with optional time as None."""
        todo = TodoData(task="整理房间", location="家里")
        assert todo.time is None
        assert todo.location == "家里"
    
    def test_todo_data_optional_location(self):
        """Test TodoData with optional location as None."""
        todo = TodoData(task="打电话", time="今晚")
        assert todo.location is None
        assert todo.time == "今晚"
    
    def test_todo_data_minimal(self):
        """Test TodoData with only required task field."""
        todo = TodoData(task="记得喝水")
        assert todo.task == "记得喝水"
        assert todo.time is None
        assert todo.location is None
        assert todo.status == "pending"
    
    def test_todo_data_missing_task(self):
        """Test TodoData requires task field."""
        with pytest.raises(ValidationError) as exc_info:
            TodoData()
        assert "Field required" in str(exc_info.value)
    
    def test_todo_data_custom_status(self):
        """Test TodoData with custom status."""
        todo = TodoData(task="已完成任务", status="completed")
        assert todo.status == "completed"


class TestParsedData:
    """Tests for ParsedData model."""
    
    def test_parsed_data_complete(self):
        """Test ParsedData with all fields populated."""
        parsed = ParsedData(
            mood=MoodData(type="开心", intensity=8),
            inspirations=[
                InspirationData(core_idea="想法1", category="工作")
            ],
            todos=[
                TodoData(task="任务1")
            ]
        )
        assert parsed.mood is not None
        assert len(parsed.inspirations) == 1
        assert len(parsed.todos) == 1
    
    def test_parsed_data_empty(self):
        """Test ParsedData with all fields empty."""
        parsed = ParsedData()
        assert parsed.mood is None
        assert parsed.inspirations == []
        assert parsed.todos == []
    
    def test_parsed_data_only_mood(self):
        """Test ParsedData with only mood."""
        parsed = ParsedData(
            mood=MoodData(type="平静", intensity=5)
        )
        assert parsed.mood is not None
        assert parsed.inspirations == []
        assert parsed.todos == []
    
    def test_parsed_data_multiple_inspirations(self):
        """Test ParsedData with multiple inspirations."""
        parsed = ParsedData(
            inspirations=[
                InspirationData(core_idea="想法1", category="工作"),
                InspirationData(core_idea="想法2", category="生活"),
                InspirationData(core_idea="想法3", category="学习")
            ]
        )
        assert len(parsed.inspirations) == 3
    
    def test_parsed_data_multiple_todos(self):
        """Test ParsedData with multiple todos."""
        parsed = ParsedData(
            todos=[
                TodoData(task="任务1"),
                TodoData(task="任务2"),
                TodoData(task="任务3")
            ]
        )
        assert len(parsed.todos) == 3


class TestRecordData:
    """Tests for RecordData model."""
    
    def test_record_data_audio_input(self):
        """Test RecordData with audio input type."""
        record = RecordData(
            record_id="test-id-123",
            timestamp="2024-01-01T12:00:00Z",
            input_type="audio",
            original_text="转写后的文本",
            parsed_data=ParsedData()
        )
        assert record.input_type == "audio"
        assert record.original_text == "转写后的文本"
    
    def test_record_data_text_input(self):
        """Test RecordData with text input type."""
        record = RecordData(
            record_id="test-id-456",
            timestamp="2024-01-01T12:00:00Z",
            input_type="text",
            original_text="用户输入的文本",
            parsed_data=ParsedData()
        )
        assert record.input_type == "text"
        assert record.original_text == "用户输入的文本"
    
    def test_record_data_invalid_input_type(self):
        """Test RecordData rejects invalid input type."""
        with pytest.raises(ValidationError) as exc_info:
            RecordData(
                record_id="test-id",
                timestamp="2024-01-01T12:00:00Z",
                input_type="invalid",
                original_text="文本",
                parsed_data=ParsedData()
            )
        assert "Input should be" in str(exc_info.value)
    
    def test_record_data_with_parsed_data(self):
        """Test RecordData with complete parsed data."""
        record = RecordData(
            record_id="test-id-789",
            timestamp="2024-01-01T12:00:00Z",
            input_type="text",
            original_text="今天很开心，想到一个新项目，明天要完成报告",
            parsed_data=ParsedData(
                mood=MoodData(type="开心", intensity=8),
                inspirations=[InspirationData(core_idea="新项目", category="工作")],
                todos=[TodoData(task="完成报告", time="明天")]
            )
        )
        assert record.parsed_data.mood is not None
        assert len(record.parsed_data.inspirations) == 1
        assert len(record.parsed_data.todos) == 1


class TestProcessResponse:
    """Tests for ProcessResponse model."""
    
    def test_process_response_success(self):
        """Test ProcessResponse for successful processing."""
        response = ProcessResponse(
            record_id="test-id-123",
            timestamp="2024-01-01T12:00:00Z",
            mood=MoodData(type="开心", intensity=8),
            inspirations=[InspirationData(core_idea="想法", category="工作")],
            todos=[TodoData(task="任务")]
        )
        assert response.error is None
        assert response.mood is not None
        assert len(response.inspirations) == 1
        assert len(response.todos) == 1
    
    def test_process_response_error(self):
        """Test ProcessResponse with error."""
        response = ProcessResponse(
            record_id="test-id-456",
            timestamp="2024-01-01T12:00:00Z",
            error="语音识别服务不可用"
        )
        assert response.error == "语音识别服务不可用"
        assert response.mood is None
        assert response.inspirations == []
        assert response.todos == []
    
    def test_process_response_empty_results(self):
        """Test ProcessResponse with empty results."""
        response = ProcessResponse(
            record_id="test-id-789",
            timestamp="2024-01-01T12:00:00Z"
        )
        assert response.error is None
        assert response.mood is None
        assert response.inspirations == []
        assert response.todos == []
    
    def test_process_response_serialization(self):
        """Test ProcessResponse can be serialized to dict."""
        response = ProcessResponse(
            record_id="test-id",
            timestamp="2024-01-01T12:00:00Z",
            mood=MoodData(type="开心", intensity=8, keywords=["愉快"])
        )
        data = response.model_dump()
        assert data["record_id"] == "test-id"
        assert data["mood"]["type"] == "开心"
        assert data["mood"]["intensity"] == 8
        assert data["mood"]["keywords"] == ["愉快"]


# Property-Based Tests
# These tests use hypothesis to verify properties hold across many random inputs

from hypothesis import given, strategies as st
from hypothesis import settings


class TestMoodDataProperties:
    """Property-based tests for MoodData model.
    
    **Validates: Requirements 4.1, 4.2, 4.3**
    """
    
    @given(
        mood_type=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
        intensity=st.one_of(st.none(), st.integers(min_value=1, max_value=10)),
        keywords=st.lists(st.text(min_size=0, max_size=20), min_size=0, max_size=10)
    )
    @settings(max_examples=100)
    def test_property_6_mood_data_structure_validation(self, mood_type, intensity, keywords):
        """
        Property 6: 情绪数据结构验证
        
        For any parsed mood data, it should contain type (string), intensity (1-10 integer),
        and keywords (string array) fields, with intensity within valid range.
        
        **Validates: Requirements 4.1, 4.2, 4.3**
        """
        # Create MoodData with valid inputs
        mood = MoodData(
            type=mood_type,
            intensity=intensity,
            keywords=keywords
        )
        
        # Property 1: type field exists and is either None or string
        assert hasattr(mood, 'type')
        assert mood.type is None or isinstance(mood.type, str)
        
        # Property 2: intensity field exists and is either None or integer in range 1-10
        assert hasattr(mood, 'intensity')
        if mood.intensity is not None:
            assert isinstance(mood.intensity, int)
            assert 1 <= mood.intensity <= 10
        
        # Property 3: keywords field exists and is a list of strings
        assert hasattr(mood, 'keywords')
        assert isinstance(mood.keywords, list)
        assert all(isinstance(kw, str) for kw in mood.keywords)
        
        # Property 4: All three fields should be present in the model
        model_dict = mood.model_dump()
        assert 'type' in model_dict
        assert 'intensity' in model_dict
        assert 'keywords' in model_dict
    
    @given(
        intensity=st.integers().filter(lambda x: x < 1 or x > 10)
    )
    @settings(max_examples=100)
    def test_property_6_mood_intensity_range_validation(self, intensity):
        """
        Property 6: 情绪数据结构验证 - Intensity Range
        
        For any intensity value outside the range [1, 10], MoodData should reject it
        with a ValidationError.
        
        **Validates: Requirements 4.2**
        """
        with pytest.raises(ValidationError) as exc_info:
            MoodData(type="测试", intensity=intensity)
        
        # Verify the error message mentions the constraint
        error_str = str(exc_info.value)
        assert "greater than or equal to 1" in error_str or "less than or equal to 10" in error_str
    
    @given(
        mood_type=st.one_of(st.none(), st.text(min_size=0, max_size=100)),
        keywords=st.lists(st.text(min_size=0, max_size=50), min_size=0, max_size=20)
    )
    @settings(max_examples=100)
    def test_property_6_mood_serialization_deserialization(self, mood_type, keywords):
        """
        Property 6: 情绪数据结构验证 - Serialization
        
        For any valid MoodData, it should be serializable to dict and deserializable
        back to MoodData with the same values.
        
        **Validates: Requirements 4.1, 4.2, 4.3**
        """
        # Create original mood with valid intensity
        original_mood = MoodData(
            type=mood_type,
            intensity=5,  # Use valid intensity
            keywords=keywords
        )
        
        # Serialize to dict
        mood_dict = original_mood.model_dump()
        
        # Deserialize back to MoodData
        deserialized_mood = MoodData(**mood_dict)
        
        # Verify all fields match
        assert deserialized_mood.type == original_mood.type
        assert deserialized_mood.intensity == original_mood.intensity
        assert deserialized_mood.keywords == original_mood.keywords


class TestInspirationDataProperties:
    """Property-based tests for InspirationData model.
    
    **Validates: Requirements 5.1, 5.2, 5.3**
    """
    
    @given(
        core_idea=st.text(min_size=1, max_size=20),
        tags=st.lists(st.text(min_size=0, max_size=20), min_size=0, max_size=5),
        category=st.sampled_from(["工作", "生活", "学习", "创意"])
    )
    @settings(max_examples=100)
    def test_property_7_inspiration_data_structure_validation(self, core_idea, tags, category):
        """
        Property 7: 灵感数据结构验证
        
        For any parsed inspiration data, it should contain core_idea (length ≤ 20),
        tags (array length ≤ 5), and category (enum: 工作/生活/学习/创意) fields,
        with all constraints satisfied.
        
        **Validates: Requirements 5.1, 5.2, 5.3**
        """
        # Create InspirationData with valid inputs
        inspiration = InspirationData(
            core_idea=core_idea,
            tags=tags,
            category=category
        )
        
        # Property 1: core_idea field exists and is a string with length ≤ 20
        assert hasattr(inspiration, 'core_idea')
        assert isinstance(inspiration.core_idea, str)
        assert len(inspiration.core_idea) <= 20
        
        # Property 2: tags field exists and is a list with length ≤ 5
        assert hasattr(inspiration, 'tags')
        assert isinstance(inspiration.tags, list)
        assert len(inspiration.tags) <= 5
        assert all(isinstance(tag, str) for tag in inspiration.tags)
        
        # Property 3: category field exists and is one of the valid enum values
        assert hasattr(inspiration, 'category')
        assert isinstance(inspiration.category, str)
        assert inspiration.category in ["工作", "生活", "学习", "创意"]
        
        # Property 4: All three fields should be present in the model
        model_dict = inspiration.model_dump()
        assert 'core_idea' in model_dict
        assert 'tags' in model_dict
        assert 'category' in model_dict
    
    @given(
        core_idea=st.text(min_size=21, max_size=100)
    )
    @settings(max_examples=100)
    def test_property_7_core_idea_length_validation(self, core_idea):
        """
        Property 7: 灵感数据结构验证 - Core Idea Length
        
        For any core_idea with length > 20, InspirationData should reject it
        with a ValidationError.
        
        **Validates: Requirements 5.1**
        """
        with pytest.raises(ValidationError) as exc_info:
            InspirationData(
                core_idea=core_idea,
                category="工作"
            )
        
        # Verify the error message mentions the length constraint
        error_str = str(exc_info.value)
        assert "at most 20 characters" in error_str
    
    @given(
        tags=st.lists(st.text(min_size=1, max_size=10), min_size=6, max_size=20)
    )
    @settings(max_examples=100)
    def test_property_7_tags_count_validation(self, tags):
        """
        Property 7: 灵感数据结构验证 - Tags Count
        
        For any tags list with more than 5 items, InspirationData should reject it
        with a ValidationError.
        
        **Validates: Requirements 5.2**
        """
        with pytest.raises(ValidationError) as exc_info:
            InspirationData(
                core_idea="想法",
                tags=tags,
                category="工作"
            )
        
        # Verify the error message mentions the count constraint
        error_str = str(exc_info.value)
        assert "at most 5 items" in error_str
    
    @given(
        category=st.text(min_size=1, max_size=20).filter(
            lambda x: x not in ["工作", "生活", "学习", "创意"]
        )
    )
    @settings(max_examples=100)
    def test_property_7_category_enum_validation(self, category):
        """
        Property 7: 灵感数据结构验证 - Category Enum
        
        For any category value not in the enum ["工作", "生活", "学习", "创意"],
        InspirationData should reject it with a ValidationError.
        
        **Validates: Requirements 5.3**
        """
        with pytest.raises(ValidationError) as exc_info:
            InspirationData(
                core_idea="想法",
                category=category
            )
        
        # Verify the error message mentions the enum constraint
        error_str = str(exc_info.value)
        assert "Input should be" in error_str
    
    @given(
        core_idea=st.text(min_size=1, max_size=20),
        tags=st.lists(st.text(min_size=0, max_size=30), min_size=0, max_size=5),
        category=st.sampled_from(["工作", "生活", "学习", "创意"])
    )
    @settings(max_examples=100)
    def test_property_7_inspiration_serialization_deserialization(self, core_idea, tags, category):
        """
        Property 7: 灵感数据结构验证 - Serialization
        
        For any valid InspirationData, it should be serializable to dict and deserializable
        back to InspirationData with the same values.
        
        **Validates: Requirements 5.1, 5.2, 5.3**
        """
        # Create original inspiration
        original_inspiration = InspirationData(
            core_idea=core_idea,
            tags=tags,
            category=category
        )
        
        # Serialize to dict
        inspiration_dict = original_inspiration.model_dump()
        
        # Deserialize back to InspirationData
        deserialized_inspiration = InspirationData(**inspiration_dict)
        
        # Verify all fields match
        assert deserialized_inspiration.core_idea == original_inspiration.core_idea
        assert deserialized_inspiration.tags == original_inspiration.tags
        assert deserialized_inspiration.category == original_inspiration.category
    
    @given(
        core_idea=st.text(min_size=1, max_size=20),
        category=st.sampled_from(["工作", "生活", "学习", "创意"])
    )
    @settings(max_examples=100)
    def test_property_7_inspiration_empty_tags_default(self, core_idea, category):
        """
        Property 7: 灵感数据结构验证 - Empty Tags Default
        
        For any InspirationData created without tags, it should default to an empty list.
        
        **Validates: Requirements 5.2**
        """
        # Create inspiration without tags
        inspiration = InspirationData(
            core_idea=core_idea,
            category=category
        )
        
        # Verify tags defaults to empty list
        assert inspiration.tags == []
        assert isinstance(inspiration.tags, list)


class TestTodoDataProperties:
    """Property-based tests for TodoData model.
    
    **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
    """
    
    @given(
        task=st.text(min_size=1, max_size=200),
        time=st.one_of(st.none(), st.text(min_size=0, max_size=50)),
        location=st.one_of(st.none(), st.text(min_size=0, max_size=100)),
        status=st.text(min_size=1, max_size=20)
    )
    @settings(max_examples=100)
    def test_property_8_todo_data_structure_validation(self, task, time, location, status):
        """
        Property 8: 待办数据结构验证
        
        For any parsed todo data, it should contain task (required), time (optional),
        location (optional), and status (defaults to "pending") fields.
        
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
        """
        # Create TodoData with valid inputs
        todo = TodoData(
            task=task,
            time=time,
            location=location,
            status=status
        )
        
        # Property 1: task field exists and is a required string
        assert hasattr(todo, 'task')
        assert isinstance(todo.task, str)
        assert len(todo.task) > 0  # task is required, so it should not be empty
        
        # Property 2: time field exists and is either None or string
        assert hasattr(todo, 'time')
        assert todo.time is None or isinstance(todo.time, str)
        
        # Property 3: location field exists and is either None or string
        assert hasattr(todo, 'location')
        assert todo.location is None or isinstance(todo.location, str)
        
        # Property 4: status field exists and is a string
        assert hasattr(todo, 'status')
        assert isinstance(todo.status, str)
        
        # Property 5: All four fields should be present in the model
        model_dict = todo.model_dump()
        assert 'task' in model_dict
        assert 'time' in model_dict
        assert 'location' in model_dict
        assert 'status' in model_dict
    
    @given(
        task=st.text(min_size=1, max_size=200)
    )
    @settings(max_examples=100)
    def test_property_8_todo_default_status(self, task):
        """
        Property 8: 待办数据结构验证 - Default Status
        
        For any new todo item created without explicit status, the status should
        default to "pending".
        
        **Validates: Requirements 6.4**
        """
        # Create TodoData without explicit status
        todo = TodoData(task=task)
        
        # Verify status defaults to "pending"
        assert todo.status == "pending"
        assert isinstance(todo.status, str)
    
    @given(
        task=st.text(min_size=1, max_size=200),
        time=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
        location=st.one_of(st.none(), st.text(min_size=1, max_size=100))
    )
    @settings(max_examples=100)
    def test_property_8_todo_optional_fields(self, task, time, location):
        """
        Property 8: 待办数据结构验证 - Optional Fields
        
        For any todo data, time and location fields should be optional and can be None.
        
        **Validates: Requirements 6.2, 6.3**
        """
        # Create TodoData with optional fields
        todo = TodoData(
            task=task,
            time=time,
            location=location
        )
        
        # Verify optional fields can be None or string
        if time is None:
            assert todo.time is None
        else:
            assert isinstance(todo.time, str)
        
        if location is None:
            assert todo.location is None
        else:
            assert isinstance(todo.location, str)
    
    @given(
        task=st.text(min_size=1, max_size=200),
        time=st.one_of(st.none(), st.text(min_size=0, max_size=50)),
        location=st.one_of(st.none(), st.text(min_size=0, max_size=100)),
        status=st.text(min_size=1, max_size=20)
    )
    @settings(max_examples=100)
    def test_property_8_todo_serialization_deserialization(self, task, time, location, status):
        """
        Property 8: 待办数据结构验证 - Serialization
        
        For any valid TodoData, it should be serializable to dict and deserializable
        back to TodoData with the same values.
        
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
        """
        # Create original todo
        original_todo = TodoData(
            task=task,
            time=time,
            location=location,
            status=status
        )
        
        # Serialize to dict
        todo_dict = original_todo.model_dump()
        
        # Deserialize back to TodoData
        deserialized_todo = TodoData(**todo_dict)
        
        # Verify all fields match
        assert deserialized_todo.task == original_todo.task
        assert deserialized_todo.time == original_todo.time
        assert deserialized_todo.location == original_todo.location
        assert deserialized_todo.status == original_todo.status
    
    @given(
        time=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=100)
    def test_property_8_todo_time_preservation(self, time):
        """
        Property 8: 待办数据结构验证 - Time Preservation
        
        For any todo data with time information, the time should be preserved as
        the original expression (e.g., "明晚", "下周三").
        
        **Validates: Requirements 6.2**
        """
        # Create TodoData with time
        todo = TodoData(
            task="测试任务",
            time=time
        )
        
        # Verify time is preserved exactly as provided
        assert todo.time == time
        assert isinstance(todo.time, str)
    
    @given(
        task=st.text(min_size=1, max_size=200)
    )
    @settings(max_examples=100)
    def test_property_8_todo_minimal_creation(self, task):
        """
        Property 8: 待办数据结构验证 - Minimal Creation
        
        For any todo data, only the task field is required. All other fields
        should have sensible defaults or be optional.
        
        **Validates: Requirements 6.1, 6.4**
        """
        # Create TodoData with only task
        todo = TodoData(task=task)
        
        # Verify task is set
        assert todo.task == task
        
        # Verify optional fields are None
        assert todo.time is None
        assert todo.location is None
        
        # Verify status has default value
        assert todo.status == "pending"
    
    def test_property_8_todo_task_required(self):
        """
        Property 8: 待办数据结构验证 - Task Required
        
        For any todo data, the task field is required and TodoData should reject
        creation without it.
        
        **Validates: Requirements 6.1**
        """
        # Attempt to create TodoData without task
        with pytest.raises(ValidationError) as exc_info:
            TodoData()
        
        # Verify the error message mentions the required field
        error_str = str(exc_info.value)
        assert "Field required" in error_str or "field required" in error_str.lower()
