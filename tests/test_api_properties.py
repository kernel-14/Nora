"""Property-based tests for API endpoints.

This module contains property-based tests for the /api/process endpoint,
validating universal properties that should hold across all inputs.

Requirements: 1.1, 1.2, 1.3, 8.4, 8.5, 8.6, 9.1, 9.3
"""

import os
import pytest
import tempfile
import shutil
from unittest.mock import patch, AsyncMock, MagicMock
from io import BytesIO
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient


# Note: We don't use pytest fixtures with hypothesis tests because
# fixtures are not reset between examples. Instead, we create temp
# directories directly in the test methods.


# Custom strategies for generating test data
@st.composite
def audio_filename_strategy(draw):
    """Generate audio filenames with various extensions."""
    base_name = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        min_codepoint=ord('a'),
        max_codepoint=ord('z')
    )))
    extension = draw(st.sampled_from([
        '.mp3', '.wav', '.m4a',  # Supported formats
        '.ogg', '.flac', '.aac', '.wma', '.txt', '.pdf'  # Unsupported formats
    ]))
    return base_name + extension


@st.composite
def utf8_text_strategy(draw):
    """Generate UTF-8 text including Chinese, emoji, and special characters."""
    return draw(st.text(
        min_size=1,
        max_size=200,
        alphabet=st.characters(
            blacklist_categories=('Cs',),  # Exclude surrogates
            blacklist_characters='\x00'  # Exclude null character
        )
    ))


class TestProperty1AudioFormatValidation:
    """Property 1: 音频格式验证
    
    For any submitted file, if the file extension is mp3, wav, or m4a,
    the system should accept the file; if it's another format,
    the system should reject it and return an error.
    
    **Validates: Requirements 1.1**
    """
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    @patch("app.main.ASRService")
    @patch("app.main.SemanticParserService")
    @given(filename=audio_filename_strategy())
    @settings(max_examples=25)
    def test_property_1_audio_format_validation(
        self,
        mock_parser_class,
        mock_asr_class,
        filename
    ):
        """Test that audio format validation works correctly for all file types.
        
        Feature: voice-text-processor, Property 1: 音频格式验证
        """
        # Create temporary directory for this test
        temp_dir = tempfile.mkdtemp()
        try:
            # Reset config
            import app.config
            app.config._config = None
            
            # Mock services
            from app.models import ParsedData
            mock_asr = MagicMock()
            mock_asr.transcribe = AsyncMock(return_value="转写后的文本")
            mock_asr.close = AsyncMock()
            mock_asr_class.return_value = mock_asr
            
            mock_parser = MagicMock()
            mock_parser.parse = AsyncMock(return_value=ParsedData(
                mood=None,
                inspirations=[],
                todos=[]
            ))
            mock_parser.close = AsyncMock()
            mock_parser_class.return_value = mock_parser
            
            with patch.dict(os.environ, {
                "DATA_DIR": os.path.join(temp_dir, "data"),
                "LOG_FILE": os.path.join(temp_dir, "logs", "app.log")
            }, clear=False):
                from app.main import app
                
                with TestClient(app) as client:
                    # Create fake audio file
                    audio_data = b"fake audio content"
                    files = {"audio": (filename, BytesIO(audio_data), "audio/mpeg")}
                    
                    response = client.post("/api/process", files=files)
                    
                    # Extract file extension
                    file_ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
                    supported_formats = {".mp3", ".wav", ".m4a"}
                    
                    if file_ext in supported_formats:
                        # Should accept the file (200 or 500 if processing fails)
                        assert response.status_code in [200, 500], \
                            f"Supported format {file_ext} should be accepted"
                        
                        # If 200, should have record_id
                        if response.status_code == 200:
                            data = response.json()
                            assert "record_id" in data
                    else:
                        # Should reject the file with 400
                        assert response.status_code == 400, \
                            f"Unsupported format {file_ext} should be rejected"
                        data = response.json()
                        assert "error" in data
                        assert "不支持的音频格式" in data["error"]
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProperty2UTF8TextAcceptance:
    """Property 2: UTF-8 文本接受
    
    For any UTF-8 encoded text string (including Chinese, emoji, special characters),
    the system should correctly accept and process it.
    
    **Validates: Requirements 1.2**
    """
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    @patch("app.main.SemanticParserService")
    @given(text=utf8_text_strategy())
    @settings(max_examples=30)
    def test_property_2_utf8_text_acceptance(
        self,
        mock_parser_class,
        text
    ):
        """Test that UTF-8 text is accepted regardless of content.
        
        Feature: voice-text-processor, Property 2: UTF-8 文本接受
        """
        # Create temporary directory for this test
        temp_dir = tempfile.mkdtemp()
        try:
            # Reset config
            import app.config
            app.config._config = None
            
            # Mock semantic parser
            from app.models import ParsedData
            mock_parser = MagicMock()
            mock_parser.parse = AsyncMock(return_value=ParsedData(
                mood=None,
                inspirations=[],
                todos=[]
            ))
            mock_parser.close = AsyncMock()
            mock_parser_class.return_value = mock_parser
            
            with patch.dict(os.environ, {
                "DATA_DIR": os.path.join(temp_dir, "data"),
                "LOG_FILE": os.path.join(temp_dir, "logs", "app.log")
            }, clear=False):
                from app.main import app
                
                with TestClient(app) as client:
                    # Submit text input
                    response = client.post(
                        "/api/process",
                        data={"text": text}
                    )
                    
                    # Should accept the input (not reject with 400 for encoding issues)
                    # May return 200 (success) or 500 (processing error), but not 400
                    assert response.status_code in [200, 500], \
                        f"UTF-8 text should be accepted, got {response.status_code}"
                    
                    # If successful, should have required fields
                    if response.status_code == 200:
                        data = response.json()
                        assert "record_id" in data
                        assert "timestamp" in data
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProperty3InvalidInputErrorHandling:
    """Property 3: 无效输入错误处理
    
    For any empty input or invalid format input, the system should return
    a JSON response containing an error field, rather than crashing or
    returning a success status.
    
    **Validates: Requirements 1.3, 9.1**
    """
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    @settings(max_examples=20)
    @given(
        has_audio=st.booleans(),
        has_text=st.booleans(),
        text_is_empty=st.booleans()
    )
    def test_property_3_invalid_input_error_handling(
        self,
        has_audio,
        has_text,
        text_is_empty
    ):
        """Test that invalid inputs return proper error responses.
        
        Feature: voice-text-processor, Property 3: 无效输入错误处理
        """
        # Skip valid input combinations
        if (has_audio and not has_text) or (has_text and not has_audio and not text_is_empty):
            return
        
        # Create temporary directory for this test
        temp_dir = tempfile.mkdtemp()
        try:
            # Reset config
            import app.config
            app.config._config = None
            
            with patch.dict(os.environ, {
                "DATA_DIR": os.path.join(temp_dir, "data"),
                "LOG_FILE": os.path.join(temp_dir, "logs", "app.log")
            }, clear=False):
                from app.main import app
                
                with TestClient(app) as client:
                    # Prepare request based on parameters
                    if not has_audio and not has_text:
                        # No input at all
                        response = client.post("/api/process")
                    elif has_audio and has_text:
                        # Both inputs (invalid)
                        audio_data = b"fake audio"
                        files = {"audio": ("test.mp3", BytesIO(audio_data), "audio/mpeg")}
                        response = client.post(
                            "/api/process",
                            files=files,
                            data={"text": "some text"}
                        )
                    elif has_text and text_is_empty:
                        # Empty text
                        response = client.post(
                            "/api/process",
                            data={"text": ""}
                        )
                    else:
                        # Should not reach here
                        return
                    
                    # Should return error response (400), not crash (500) or succeed (200)
                    assert response.status_code == 400, \
                        "Invalid input should return 400 error"
                    
                    # Response should be valid JSON with error field
                    data = response.json()
                    assert "error" in data, "Error response must contain 'error' field"
                    assert isinstance(data["error"], str), "Error field must be a string"
                    assert len(data["error"]) > 0, "Error message must not be empty"
                    
                    # Should also have timestamp
                    assert "timestamp" in data
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProperty12SuccessResponseFormat:
    """Property 12: 成功响应格式
    
    For any successfully processed request, the HTTP response should return
    200 status code, and the response JSON should contain record_id, timestamp,
    mood, inspirations, and todos fields.
    
    **Validates: Requirements 8.4, 8.6**
    """
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    @patch("app.main.SemanticParserService")
    @given(text=st.text(min_size=1, max_size=100))
    @settings(max_examples=25)
    def test_property_12_success_response_format(
        self,
        mock_parser_class,
        text
    ):
        """Test that successful responses have the correct format.
        
        Feature: voice-text-processor, Property 12: 成功响应格式
        """
        # Create temporary directory for this test
        temp_dir = tempfile.mkdtemp()
        try:
            # Reset config
            import app.config
            app.config._config = None
            
            # Mock semantic parser to always succeed
            from app.models import ParsedData, MoodData, InspirationData, TodoData
            
            # Generate varied parsed data
            mock_parser = MagicMock()
            mock_parser.parse = AsyncMock(return_value=ParsedData(
                mood=MoodData(type="测试情绪", intensity=5, keywords=["测试"]),
                inspirations=[InspirationData(core_idea="测试想法", tags=["测试"], category="工作")],
                todos=[TodoData(task="测试任务", time="今天", location="测试地点")]
            ))
            mock_parser.close = AsyncMock()
            mock_parser_class.return_value = mock_parser
            
            with patch.dict(os.environ, {
                "DATA_DIR": os.path.join(temp_dir, "data"),
                "LOG_FILE": os.path.join(temp_dir, "logs", "app.log")
            }, clear=False):
                from app.main import app
                
                with TestClient(app) as client:
                    response = client.post(
                        "/api/process",
                        data={"text": text}
                    )
                    
                    # Should return 200 status code
                    assert response.status_code == 200, \
                        f"Success response should return 200, got {response.status_code}"
                    
                    # Response should be valid JSON
                    data = response.json()
                    
                    # Must contain all required fields
                    assert "record_id" in data, "Response must contain 'record_id'"
                    assert "timestamp" in data, "Response must contain 'timestamp'"
                    assert "mood" in data, "Response must contain 'mood'"
                    assert "inspirations" in data, "Response must contain 'inspirations'"
                    assert "todos" in data, "Response must contain 'todos'"
                    
                    # Validate field types
                    assert isinstance(data["record_id"], str), "record_id must be string"
                    assert len(data["record_id"]) > 0, "record_id must not be empty"
                    
                    assert isinstance(data["timestamp"], str), "timestamp must be string"
                    assert len(data["timestamp"]) > 0, "timestamp must not be empty"
                    
                    # mood can be None or dict
                    assert data["mood"] is None or isinstance(data["mood"], dict), \
                        "mood must be None or dict"
                    
                    # inspirations must be list
                    assert isinstance(data["inspirations"], list), \
                        "inspirations must be list"
                    
                    # todos must be list
                    assert isinstance(data["todos"], list), \
                        "todos must be list"
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestProperty13ErrorResponseFormat:
    """Property 13: 错误响应格式
    
    For any failed request, the HTTP response should return appropriate error
    status code (400 or 500), and the response JSON should contain an error
    field describing the specific error.
    
    **Validates: Requirements 8.5, 9.1, 9.3**
    """
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    @settings(max_examples=20)
    @given(
        error_type=st.sampled_from([
            "validation_empty",
            "validation_both",
            "validation_format",
            "asr_error",
            "parser_error",
            "storage_error"
        ])
    )
    def test_property_13_error_response_format(
        self,
        error_type
    ):
        """Test that error responses have the correct format.
        
        Feature: voice-text-processor, Property 13: 错误响应格式
        """
        # Create temporary directory for this test
        temp_dir = tempfile.mkdtemp()
        try:
            # Reset config
            import app.config
            app.config._config = None
            
            with patch.dict(os.environ, {
                "DATA_DIR": os.path.join(temp_dir, "data"),
                "LOG_FILE": os.path.join(temp_dir, "logs", "app.log")
            }, clear=False):
                from app.main import app
                
                with TestClient(app) as client:
                    # Trigger different types of errors
                    if error_type == "validation_empty":
                        # Empty input
                        response = client.post("/api/process")
                        expected_status = 400
                    
                    elif error_type == "validation_both":
                        # Both audio and text
                        audio_data = b"fake audio"
                        files = {"audio": ("test.mp3", BytesIO(audio_data), "audio/mpeg")}
                        response = client.post(
                            "/api/process",
                            files=files,
                            data={"text": "some text"}
                        )
                        expected_status = 400
                    
                    elif error_type == "validation_format":
                        # Unsupported audio format
                        audio_data = b"fake audio"
                        files = {"audio": ("test.ogg", BytesIO(audio_data), "audio/ogg")}
                        response = client.post("/api/process", files=files)
                        expected_status = 400
                    
                    elif error_type == "asr_error":
                        # ASR service error
                        with patch("app.main.ASRService") as mock_asr_class:
                            from app.asr_service import ASRServiceError
                            mock_asr = MagicMock()
                            mock_asr.transcribe = AsyncMock(
                                side_effect=ASRServiceError("API调用失败")
                            )
                            mock_asr.close = AsyncMock()
                            mock_asr_class.return_value = mock_asr
                            
                            audio_data = b"fake audio"
                            files = {"audio": ("test.mp3", BytesIO(audio_data), "audio/mpeg")}
                            response = client.post("/api/process", files=files)
                        expected_status = 500
                    
                    elif error_type == "parser_error":
                        # Semantic parser error
                        with patch("app.main.SemanticParserService") as mock_parser_class:
                            from app.semantic_parser import SemanticParserError
                            mock_parser = MagicMock()
                            mock_parser.parse = AsyncMock(
                                side_effect=SemanticParserError("API调用失败")
                            )
                            mock_parser.close = AsyncMock()
                            mock_parser_class.return_value = mock_parser
                            
                            response = client.post(
                                "/api/process",
                                data={"text": "test text"}
                            )
                        expected_status = 500
                    
                    elif error_type == "storage_error":
                        # Storage error
                        with patch("app.main.SemanticParserService") as mock_parser_class, \
                             patch("app.main.StorageService") as mock_storage_class:
                            from app.models import ParsedData
                            from app.storage import StorageError
                            
                            mock_parser = MagicMock()
                            mock_parser.parse = AsyncMock(return_value=ParsedData(
                                mood=None,
                                inspirations=[],
                                todos=[]
                            ))
                            mock_parser.close = AsyncMock()
                            mock_parser_class.return_value = mock_parser
                            
                            mock_storage = MagicMock()
                            mock_storage.save_record = MagicMock(
                                side_effect=StorageError("磁盘空间不足")
                            )
                            mock_storage_class.return_value = mock_storage
                            
                            response = client.post(
                                "/api/process",
                                data={"text": "test text"}
                            )
                        expected_status = 500
                    
                    # Verify status code
                    assert response.status_code == expected_status, \
                        f"Error type {error_type} should return {expected_status}"
                    
                    # Response should be valid JSON
                    data = response.json()
                    
                    # Must contain error field
                    assert "error" in data, "Error response must contain 'error' field"
                    assert isinstance(data["error"], str), "Error field must be a string"
                    assert len(data["error"]) > 0, "Error message must not be empty"
                    
                    # Should also have timestamp
                    assert "timestamp" in data, "Error response must contain 'timestamp'"
                    assert isinstance(data["timestamp"], str), "timestamp must be string"
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
