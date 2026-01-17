"""Unit tests for ASR service.

This module contains unit tests for the ASRService class, testing
API call success scenarios, failure scenarios, and edge cases.

Requirements: 2.1, 2.2, 2.3, 2.4
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx

from app.asr_service import ASRService, ASRServiceError


@pytest.fixture
def asr_service():
    """Create an ASRService instance for testing."""
    return ASRService(api_key="test_api_key_12345")


@pytest.fixture
def mock_audio_file():
    """Create mock audio file bytes."""
    return b"fake_audio_data_for_testing"


@pytest.mark.asyncio
async def test_asr_service_initialization(asr_service):
    """Test ASR service initialization.
    
    Requirements: 2.1
    """
    assert asr_service.api_key == "test_api_key_12345"
    assert asr_service.model == "glm-asr-2512"
    assert asr_service.api_url == "https://api.z.ai/api/paas/v4/audio/transcriptions"
    assert isinstance(asr_service.client, httpx.AsyncClient)
    
    # Clean up
    await asr_service.close()


@pytest.mark.asyncio
async def test_transcribe_success(asr_service, mock_audio_file, mocker):
    """Test successful transcription.
    
    Requirements: 2.1, 2.2
    """
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "created": 1234567890,
        "request_id": "test_request_id",
        "model": "glm-asr-2512",
        "text": "这是一段测试语音转写的文本内容"
    }
    
    # Mock the HTTP client post method
    mock_post = mocker.patch.object(
        asr_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call transcribe
    result = await asr_service.transcribe(mock_audio_file, "test.mp3")
    
    # Verify result
    assert result == "这是一段测试语音转写的文本内容"
    
    # Verify API was called correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args.kwargs['headers']['Authorization'] == "Bearer test_api_key_12345"
    assert call_args.kwargs['data']['model'] == "glm-asr-2512"
    assert call_args.kwargs['data']['stream'] == "false"
    
    # Clean up
    await asr_service.close()


@pytest.mark.asyncio
async def test_transcribe_empty_result(asr_service, mock_audio_file, mocker):
    """Test transcription with empty recognition result.
    
    This tests the edge case where the audio cannot be recognized
    and the API returns an empty text field.
    
    Requirements: 2.4
    """
    # Mock API response with empty text
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "created": 1234567890,
        "request_id": "test_request_id",
        "model": "glm-asr-2512",
        "text": ""
    }
    
    # Mock the HTTP client post method
    mocker.patch.object(
        asr_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call transcribe
    result = await asr_service.transcribe(mock_audio_file, "empty.mp3")
    
    # Verify result is empty string
    assert result == ""
    
    # Clean up
    await asr_service.close()


@pytest.mark.asyncio
async def test_transcribe_whitespace_only_result(asr_service, mock_audio_file, mocker):
    """Test transcription with whitespace-only result.
    
    Requirements: 2.4
    """
    # Mock API response with whitespace-only text
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "created": 1234567890,
        "request_id": "test_request_id",
        "model": "glm-asr-2512",
        "text": "   \n\t  "
    }
    
    # Mock the HTTP client post method
    mocker.patch.object(
        asr_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call transcribe
    result = await asr_service.transcribe(mock_audio_file, "whitespace.mp3")
    
    # Verify result is empty string
    assert result == ""
    
    # Clean up
    await asr_service.close()


@pytest.mark.asyncio
async def test_transcribe_api_error_status(asr_service, mock_audio_file, mocker):
    """Test transcription when API returns error status code.
    
    Requirements: 2.3
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
        asr_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call transcribe and expect exception
    with pytest.raises(ASRServiceError) as exc_info:
        await asr_service.transcribe(mock_audio_file, "error.mp3")
    
    # Verify error message
    assert "语音识别服务不可用" in str(exc_info.value)
    
    # Clean up
    await asr_service.close()


@pytest.mark.asyncio
async def test_transcribe_api_timeout(asr_service, mock_audio_file, mocker):
    """Test transcription when API request times out.
    
    Requirements: 2.3
    """
    # Mock timeout exception
    mocker.patch.object(
        asr_service.client,
        'post',
        side_effect=httpx.TimeoutException("Request timeout")
    )
    
    # Call transcribe and expect exception
    with pytest.raises(ASRServiceError) as exc_info:
        await asr_service.transcribe(mock_audio_file, "timeout.mp3")
    
    # Verify error message
    assert "语音识别服务不可用" in str(exc_info.value)
    assert "请求超时" in str(exc_info.value)
    
    # Clean up
    await asr_service.close()


@pytest.mark.asyncio
async def test_transcribe_network_error(asr_service, mock_audio_file, mocker):
    """Test transcription when network error occurs.
    
    Requirements: 2.3
    """
    # Mock network error
    mocker.patch.object(
        asr_service.client,
        'post',
        side_effect=httpx.RequestError("Network error")
    )
    
    # Call transcribe and expect exception
    with pytest.raises(ASRServiceError) as exc_info:
        await asr_service.transcribe(mock_audio_file, "network_error.mp3")
    
    # Verify error message
    assert "语音识别服务不可用" in str(exc_info.value)
    assert "网络错误" in str(exc_info.value)
    
    # Clean up
    await asr_service.close()


@pytest.mark.asyncio
async def test_transcribe_invalid_json_response(asr_service, mock_audio_file, mocker):
    """Test transcription when API returns invalid JSON.
    
    Requirements: 2.3
    """
    # Mock response with invalid JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    
    # Mock the HTTP client post method
    mocker.patch.object(
        asr_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call transcribe and expect exception
    with pytest.raises(ASRServiceError) as exc_info:
        await asr_service.transcribe(mock_audio_file, "invalid_json.mp3")
    
    # Verify error message
    assert "语音识别服务不可用" in str(exc_info.value)
    assert "响应格式无效" in str(exc_info.value)
    
    # Clean up
    await asr_service.close()


@pytest.mark.asyncio
async def test_transcribe_missing_text_field(asr_service, mock_audio_file, mocker):
    """Test transcription when API response is missing text field.
    
    Requirements: 2.3
    """
    # Mock response without text field
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "created": 1234567890,
        "request_id": "test_request_id",
        "model": "glm-asr-2512"
        # Missing "text" field
    }
    
    # Mock the HTTP client post method
    mocker.patch.object(
        asr_service.client,
        'post',
        return_value=mock_response
    )
    
    # Call transcribe - should return empty string when text field is missing
    result = await asr_service.transcribe(mock_audio_file, "missing_text.mp3")
    
    # Verify result is empty string
    assert result == ""
    
    # Clean up
    await asr_service.close()


@pytest.mark.asyncio
async def test_transcribe_unexpected_exception(asr_service, mock_audio_file, mocker):
    """Test transcription when unexpected exception occurs.
    
    Requirements: 2.3
    """
    # Mock unexpected exception
    mocker.patch.object(
        asr_service.client,
        'post',
        side_effect=Exception("Unexpected error")
    )
    
    # Call transcribe and expect exception
    with pytest.raises(ASRServiceError) as exc_info:
        await asr_service.transcribe(mock_audio_file, "unexpected.mp3")
    
    # Verify error message
    assert "语音识别服务不可用" in str(exc_info.value)
    
    # Clean up
    await asr_service.close()


@pytest.mark.asyncio
async def test_close_client(asr_service):
    """Test closing the HTTP client.
    
    Requirements: 2.1
    """
    # Verify client is open
    assert not asr_service.client.is_closed
    
    # Close the client
    await asr_service.close()
    
    # Verify client is closed
    assert asr_service.client.is_closed
