"""Unit tests for semantic parser service.

This module contains unit tests for the SemanticParserService class, testing
API call success scenarios, failure scenarios, System Prompt usage, and edge cases.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import pytest
import json
from unittest.mock import MagicMock
import httpx

from app.semantic_parser import SemanticParserService, SemanticParserError
from app.models import ParsedData, MoodData, InspirationData, TodoData


@pytest.fixture
def semantic_parser_service():
    """Create a SemanticParserService instance for testing."""
    return SemanticParserService(api_key="test_api_key_12345")


@pytest.fixture
def mock_text():
    """Create mock text for testing."""
    return "今天心情很好，想到了一个新项目的创意，明天要去办公室开会。"


@pytest.mark.asyncio
async def test_semantic_parser_initialization(semantic_parser_service):
    """Test semantic parser service initialization.
    
    Requirements: 3.1, 3.2
    """
    assert semantic_parser_service.api_key == "test_api_key_12345"
    assert semantic_parser_service.model == "glm-4-flash"
    assert semantic_parser_service.api_url == "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    assert isinstance(semantic_parser_service.client, httpx.AsyncClient)
    
    # Verify system prompt is correctly set
    expected_prompt = (
        "你是一个数据转换器。请将文本解析为 JSON 格式。"
        "维度包括：1.情绪(type,intensity,keywords); "
        "2.灵感(core_idea,tags,category); "
        "3.待办(task,time,location)。"
        "必须严格遵循 JSON 格式返回。"
    )
    assert semantic_parser_service.system_prompt == expected_prompt
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_success_with_all_dimensions(semantic_parser_service, mock_text, mocker):
    """Test successful parsing with all dimensions present.
    
    Requirements: 3.1, 3.2, 3.3
    """
    # Mock successful API response with all dimensions
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "created": 1234567890,
        "model": "glm-4-flash",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps({
                        "mood": {
                            "type": "开心",
                            "intensity": 8,
                            "keywords": ["愉快", "放松"]
                        },
                        "inspirations": [
                            {
                                "core_idea": "新项目创意",
                                "tags": ["创新", "技术"],
                                "category": "工作"
                            }
                        ],
                        "todos": [
                            {
                                "task": "去办公室开会",
                                "time": "明天",
                                "location": "办公室",
                                "status": "pending"
                            }
                        ]
                    })
                }
            }
        ]
    }
    
    # Mock the HTTP client post method
    mock_post = mocker.patch.object(
        semantic_parser_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call parse
    result = await semantic_parser_service.parse(mock_text)
    
    # Verify result structure
    assert isinstance(result, ParsedData)
    assert result.mood is not None
    assert result.mood.type == "开心"
    assert result.mood.intensity == 8
    assert result.mood.keywords == ["愉快", "放松"]
    assert len(result.inspirations) == 1
    assert result.inspirations[0].core_idea == "新项目创意"
    assert result.inspirations[0].tags == ["创新", "技术"]
    assert result.inspirations[0].category == "工作"
    assert len(result.todos) == 1
    assert result.todos[0].task == "去办公室开会"
    assert result.todos[0].time == "明天"
    assert result.todos[0].location == "办公室"
    assert result.todos[0].status == "pending"
    
    # Verify API was called correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args.kwargs['headers']['Authorization'] == "Bearer test_api_key_12345"
    assert call_args.kwargs['json']['model'] == "glm-4-flash"
    
    # Verify system prompt is used
    messages = call_args.kwargs['json']['messages']
    assert len(messages) == 2
    assert messages[0]['role'] == "system"
    assert messages[0]['content'] == semantic_parser_service.system_prompt
    assert messages[1]['role'] == "user"
    assert messages[1]['content'] == mock_text
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_success_with_markdown_json(semantic_parser_service, mock_text, mocker):
    """Test successful parsing when API returns JSON in markdown code blocks.
    
    Requirements: 3.1, 3.3
    """
    # Mock API response with JSON in markdown code blocks
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "```json\n" + json.dumps({
                        "mood": {
                            "type": "开心",
                            "intensity": 7,
                            "keywords": ["愉快"]
                        },
                        "inspirations": [],
                        "todos": []
                    }) + "\n```"
                }
            }
        ]
    }
    
    # Mock the HTTP client post method
    mocker.patch.object(
        semantic_parser_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call parse
    result = await semantic_parser_service.parse(mock_text)
    
    # Verify result
    assert isinstance(result, ParsedData)
    assert result.mood is not None
    assert result.mood.type == "开心"
    assert result.mood.intensity == 7
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_no_mood_dimension(semantic_parser_service, mocker):
    """Test parsing text with no mood information.
    
    This tests the edge case where the text does not contain mood information,
    and the parser should return null for the mood dimension.
    
    Requirements: 3.4
    """
    text = "明天要去办公室开会，准备项目报告。"
    
    # Mock API response without mood
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "mood": None,
                        "inspirations": [],
                        "todos": [
                            {
                                "task": "去办公室开会",
                                "time": "明天",
                                "location": "办公室"
                            }
                        ]
                    })
                }
            }
        ]
    }
    
    # Mock the HTTP client post method
    mocker.patch.object(
        semantic_parser_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call parse
    result = await semantic_parser_service.parse(text)
    
    # Verify mood is None
    assert result.mood is None
    assert len(result.todos) == 1
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_no_inspiration_dimension(semantic_parser_service, mocker):
    """Test parsing text with no inspiration information.
    
    This tests the edge case where the text does not contain inspiration information,
    and the parser should return an empty array for the inspirations dimension.
    
    Requirements: 3.4
    """
    text = "今天心情不错，明天要去开会。"
    
    # Mock API response without inspirations
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "mood": {
                            "type": "开心",
                            "intensity": 7,
                            "keywords": ["不错"]
                        },
                        "inspirations": [],
                        "todos": [
                            {
                                "task": "去开会",
                                "time": "明天"
                            }
                        ]
                    })
                }
            }
        ]
    }
    
    # Mock the HTTP client post method
    mocker.patch.object(
        semantic_parser_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call parse
    result = await semantic_parser_service.parse(text)
    
    # Verify inspirations is empty array
    assert result.inspirations == []
    assert result.mood is not None
    assert len(result.todos) == 1
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_no_todo_dimension(semantic_parser_service, mocker):
    """Test parsing text with no todo information.
    
    This tests the edge case where the text does not contain todo information,
    and the parser should return an empty array for the todos dimension.
    
    Requirements: 3.4
    """
    text = "今天心情很好，想到了一个有趣的想法。"
    
    # Mock API response without todos
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "mood": {
                            "type": "开心",
                            "intensity": 8,
                            "keywords": ["很好"]
                        },
                        "inspirations": [
                            {
                                "core_idea": "有趣的想法",
                                "tags": ["创意"],
                                "category": "生活"
                            }
                        ],
                        "todos": []
                    })
                }
            }
        ]
    }
    
    # Mock the HTTP client post method
    mocker.patch.object(
        semantic_parser_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call parse
    result = await semantic_parser_service.parse(text)
    
    # Verify todos is empty array
    assert result.todos == []
    assert result.mood is not None
    assert len(result.inspirations) == 1
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_api_error_status(semantic_parser_service, mock_text, mocker):
    """Test parsing when API returns error status code.
    
    Requirements: 3.5
    """
    # Mock API error response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {
        "error": {
            "message": "Internal server error",
            "code": "internal_error"
        }
    }
    mock_response.text = "Internal server error"
    
    # Mock the HTTP client post method
    mocker.patch.object(
        semantic_parser_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call parse and expect exception
    with pytest.raises(SemanticParserError) as exc_info:
        await semantic_parser_service.parse(mock_text)
    
    # Verify error message
    assert "语义解析服务不可用" in str(exc_info.value)
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_api_timeout(semantic_parser_service, mock_text, mocker):
    """Test parsing when API request times out.
    
    Requirements: 3.5
    """
    # Mock timeout exception
    mocker.patch.object(
        semantic_parser_service.client,
        'post',
        side_effect=httpx.TimeoutException("Request timeout")
    )
    
    # Call parse and expect exception
    with pytest.raises(SemanticParserError) as exc_info:
        await semantic_parser_service.parse(mock_text)
    
    # Verify error message
    assert "语义解析服务不可用" in str(exc_info.value)
    assert "请求超时" in str(exc_info.value)
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_network_error(semantic_parser_service, mock_text, mocker):
    """Test parsing when network error occurs.
    
    Requirements: 3.5
    """
    # Mock network error
    mocker.patch.object(
        semantic_parser_service.client,
        'post',
        side_effect=httpx.RequestError("Network error")
    )
    
    # Call parse and expect exception
    with pytest.raises(SemanticParserError) as exc_info:
        await semantic_parser_service.parse(mock_text)
    
    # Verify error message
    assert "语义解析服务不可用" in str(exc_info.value)
    assert "网络错误" in str(exc_info.value)
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_invalid_json_response(semantic_parser_service, mock_text, mocker):
    """Test parsing when API returns invalid JSON.
    
    Requirements: 3.5
    """
    # Mock response with invalid JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    
    # Mock the HTTP client post method
    mocker.patch.object(
        semantic_parser_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call parse and expect exception
    with pytest.raises(SemanticParserError) as exc_info:
        await semantic_parser_service.parse(mock_text)
    
    # Verify error message
    assert "语义解析服务不可用" in str(exc_info.value)
    assert "响应格式无效" in str(exc_info.value)
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_invalid_response_structure(semantic_parser_service, mock_text, mocker):
    """Test parsing when API response has invalid structure.
    
    Requirements: 3.5
    """
    # Mock response without required fields
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "created": 1234567890
        # Missing "choices" field
    }
    
    # Mock the HTTP client post method
    mocker.patch.object(
        semantic_parser_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call parse and expect exception
    with pytest.raises(SemanticParserError) as exc_info:
        await semantic_parser_service.parse(mock_text)
    
    # Verify error message
    assert "语义解析服务不可用" in str(exc_info.value)
    assert "响应结构无效" in str(exc_info.value)
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_invalid_json_content(semantic_parser_service, mock_text, mocker):
    """Test parsing when API returns non-JSON content.
    
    Requirements: 3.5
    """
    # Mock response with non-JSON content
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "This is not valid JSON content"
                }
            }
        ]
    }
    
    # Mock the HTTP client post method
    mocker.patch.object(
        semantic_parser_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call parse and expect exception
    with pytest.raises(SemanticParserError) as exc_info:
        await semantic_parser_service.parse(mock_text)
    
    # Verify error message
    assert "语义解析服务不可用" in str(exc_info.value)
    assert "JSON 解析失败" in str(exc_info.value)
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_parse_unexpected_exception(semantic_parser_service, mock_text, mocker):
    """Test parsing when unexpected exception occurs.
    
    Requirements: 3.5
    """
    # Mock unexpected exception
    mocker.patch.object(
        semantic_parser_service.client,
        'post',
        side_effect=Exception("Unexpected error")
    )
    
    # Call parse and expect exception
    with pytest.raises(SemanticParserError) as exc_info:
        await semantic_parser_service.parse(mock_text)
    
    # Verify error message
    assert "语义解析服务不可用" in str(exc_info.value)
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_system_prompt_usage(semantic_parser_service, mock_text, mocker):
    """Test that the correct System Prompt is used in API calls.
    
    This verifies that the system prompt specified in requirements is
    correctly included in the API request.
    
    Requirements: 3.2
    """
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "mood": None,
                        "inspirations": [],
                        "todos": []
                    })
                }
            }
        ]
    }
    
    # Mock the HTTP client post method
    mock_post = mocker.patch.object(
        semantic_parser_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call parse
    await semantic_parser_service.parse(mock_text)
    
    # Verify system prompt is used correctly
    call_args = mock_post.call_args
    messages = call_args.kwargs['json']['messages']
    
    expected_system_prompt = (
        "你是一个数据转换器。请将文本解析为 JSON 格式。"
        "维度包括：1.情绪(type,intensity,keywords); "
        "2.灵感(core_idea,tags,category); "
        "3.待办(task,time,location)。"
        "必须严格遵循 JSON 格式返回。"
    )
    
    assert messages[0]['role'] == "system"
    assert messages[0]['content'] == expected_system_prompt
    
    # Clean up
    await semantic_parser_service.close()


@pytest.mark.asyncio
async def test_close_client(semantic_parser_service):
    """Test closing the HTTP client.
    
    Requirements: 3.1
    """
    # Verify client is open
    assert not semantic_parser_service.client.is_closed
    
    # Close the client
    await semantic_parser_service.close()
    
    # Verify client is closed
    assert semantic_parser_service.client.is_closed
