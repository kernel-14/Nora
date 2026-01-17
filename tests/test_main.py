"""Tests for main FastAPI application.

Requirements: 10.4 - Startup configuration validation
Requirements: 8.1, 8.2, 8.3 - API endpoint implementation
"""

import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from io import BytesIO


class TestApplicationStartup:
    """Test application startup and configuration validation.
    
    Requirement 10.4: Application should refuse to start if required config is missing.
    """
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    def test_app_starts_with_valid_config(self, tmp_path):
        """Test that application starts successfully with valid configuration."""
        # Reset config
        import app.config
        app.config._config = None
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            # Import app after setting environment
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                response = client.get("/")
                
                assert response.status_code == 200
                assert response.json()["status"] == "running"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_app_refuses_to_start_without_api_key(self):
        """Test that application refuses to start without API key.
        
        Requirement 10.4: Missing required config should cause startup failure.
        """
        # Reset the config module
        import app.config
        app.config._config = None
        
        # Import fresh app module
        import importlib
        import app.main
        importlib.reload(app.main)
        
        from fastapi.testclient import TestClient
        
        with pytest.raises(RuntimeError, match="Configuration error"):
            with TestClient(app.main.app) as client:
                # Trigger lifespan startup
                pass


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    def test_health_check_success(self, tmp_path):
        """Test health check returns healthy status."""
        # Reset config
        import app.config
        app.config._config = None
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                response = client.get("/health")
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                assert "data_dir" in data
                assert "max_audio_size" in data


class TestRootEndpoint:
    """Test root endpoint."""
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    def test_root_endpoint(self, tmp_path):
        """Test root endpoint returns service information."""
        # Reset config
        import app.config
        app.config._config = None
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                response = client.get("/")
                
                assert response.status_code == 200
                data = response.json()
                assert data["service"] == "Voice Text Processor"
                assert data["status"] == "running"
                assert "version" in data



class TestProcessEndpoint:
    """Test /api/process endpoint.
    
    Requirements: 8.1, 8.2, 8.3 - API endpoint, business logic, error handling
    """
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    def test_process_endpoint_exists(self, tmp_path):
        """Test that POST /api/process endpoint exists.
        
        Requirement 8.1: System should provide POST /api/process interface.
        """
        # Reset config
        import app.config
        app.config._config = None
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                # Test with empty request (should fail validation but endpoint exists)
                response = client.post("/api/process")
                
                # Should return 400 (validation error), not 404 (not found)
                assert response.status_code == 400
                assert "error" in response.json()
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    @patch("app.main.SemanticParserService")
    def test_process_text_input(self, mock_parser_class, tmp_path):
        """Test processing text input (application/json format).
        
        Requirement 8.3: System should accept application/json format.
        """
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
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                # Use data parameter for form data
                response = client.post(
                    "/api/process",
                    data={"text": "今天心情很好"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "record_id" in data
                assert "timestamp" in data
                assert "mood" in data
                assert "inspirations" in data
                assert "todos" in data
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    @patch("app.main.ASRService")
    @patch("app.main.SemanticParserService")
    def test_process_audio_input(self, mock_parser_class, mock_asr_class, tmp_path):
        """Test processing audio input (multipart/form-data format).
        
        Requirement 8.2: System should accept multipart/form-data format.
        """
        # Reset config
        import app.config
        app.config._config = None
        
        # Mock ASR service
        mock_asr = MagicMock()
        mock_asr.transcribe = AsyncMock(return_value="转写后的文本")
        mock_asr.close = AsyncMock()
        mock_asr_class.return_value = mock_asr
        
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
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                # Create fake audio file
                audio_data = b"fake audio content"
                files = {"audio": ("test.mp3", BytesIO(audio_data), "audio/mpeg")}
                
                response = client.post("/api/process", files=files)
                
                assert response.status_code == 200
                data = response.json()
                assert "record_id" in data
                assert "timestamp" in data
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    def test_validation_error_empty_input(self, tmp_path):
        """Test validation error for empty input.
        
        Requirement 8.3: System should return HTTP 400 for validation errors.
        """
        # Reset config
        import app.config
        app.config._config = None
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                response = client.post("/api/process")
                
                assert response.status_code == 400
                data = response.json()
                assert "error" in data
                assert "timestamp" in data
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    def test_validation_error_unsupported_audio_format(self, tmp_path):
        """Test validation error for unsupported audio format.
        
        Requirement 1.1: System should reject unsupported audio formats.
        """
        # Reset config
        import app.config
        app.config._config = None
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                # Create fake audio file with unsupported format
                audio_data = b"fake audio content"
                files = {"audio": ("test.ogg", BytesIO(audio_data), "audio/ogg")}
                
                response = client.post("/api/process", files=files)
                
                assert response.status_code == 400
                data = response.json()
                assert "error" in data
                assert "不支持的音频格式" in data["error"]
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    def test_validation_error_file_too_large(self, tmp_path):
        """Test validation error for file size exceeding limit.
        
        Requirement 1.4: System should reject files larger than max size.
        """
        # Reset config
        import app.config
        app.config._config = None
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log"),
            "MAX_AUDIO_SIZE": "100"  # Set very small limit
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                # Create audio file larger than limit
                audio_data = b"x" * 200  # 200 bytes > 100 bytes limit
                files = {"audio": ("test.mp3", BytesIO(audio_data), "audio/mpeg")}
                
                response = client.post("/api/process", files=files)
                
                assert response.status_code == 400
                data = response.json()
                assert "error" in data
                assert "音频文件过大" in data["error"]
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    @patch("app.main.ASRService")
    def test_asr_service_error(self, mock_asr_class, tmp_path):
        """Test ASR service error handling.
        
        Requirement 8.3: System should return HTTP 500 for ASR service errors.
        """
        # Reset config
        import app.config
        app.config._config = None
        
        # Mock ASR service to raise error
        from app.asr_service import ASRServiceError
        mock_asr = MagicMock()
        mock_asr.transcribe = AsyncMock(side_effect=ASRServiceError("API调用失败"))
        mock_asr.close = AsyncMock()
        mock_asr_class.return_value = mock_asr
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                audio_data = b"fake audio content"
                files = {"audio": ("test.mp3", BytesIO(audio_data), "audio/mpeg")}
                
                response = client.post("/api/process", files=files)
                
                assert response.status_code == 500
                data = response.json()
                assert "error" in data
                assert "语音识别服务不可用" in data["error"]
                assert "timestamp" in data
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    @patch("app.main.SemanticParserService")
    def test_semantic_parser_error(self, mock_parser_class, tmp_path):
        """Test semantic parser error handling.
        
        Requirement 8.3: System should return HTTP 500 for semantic parser errors.
        """
        # Reset config
        import app.config
        app.config._config = None
        
        # Mock semantic parser to raise error
        from app.semantic_parser import SemanticParserError
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(side_effect=SemanticParserError("API调用失败"))
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                # Use data parameter for form data
                response = client.post(
                    "/api/process",
                    data={"text": "今天心情很好"}
                )
                
                assert response.status_code == 500
                data = response.json()
                assert "error" in data
                assert "语义解析服务不可用" in data["error"]
                assert "timestamp" in data
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    @patch("app.main.SemanticParserService")
    @patch("app.main.StorageService")
    def test_storage_error(self, mock_storage_class, mock_parser_class, tmp_path):
        """Test storage error handling.
        
        Requirement 8.3: System should return HTTP 500 for storage errors.
        """
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
        
        # Mock storage service to raise error
        from app.storage import StorageError
        mock_storage = MagicMock()
        mock_storage.save_record = MagicMock(side_effect=StorageError("磁盘空间不足"))
        mock_storage_class.return_value = mock_storage
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                # Use data parameter for form data
                response = client.post(
                    "/api/process",
                    data={"text": "今天心情很好"}
                )
                
                assert response.status_code == 500
                data = response.json()
                assert "error" in data
                assert "数据存储失败" in data["error"]
                assert "timestamp" in data
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    @patch("app.main.SemanticParserService")
    def test_success_response_format(self, mock_parser_class, tmp_path):
        """Test success response format.
        
        Requirement 8.4, 8.6: Success response should include all required fields.
        """
        # Reset config
        import app.config
        app.config._config = None
        
        # Mock semantic parser with full data
        from app.models import MoodData, InspirationData, TodoData, ParsedData
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(return_value=ParsedData(
            mood=MoodData(type="开心", intensity=8, keywords=["愉快"]),
            inspirations=[InspirationData(core_idea="新想法", tags=["创新"], category="工作")],
            todos=[TodoData(task="完成报告", time="明天", location="办公室")]
        ))
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(tmp_path / "data"),
            "LOG_FILE": str(tmp_path / "logs" / "app.log")
        }, clear=False):
            from fastapi.testclient import TestClient
            from app.main import app
            
            with TestClient(app) as client:
                # Use data parameter for form data
                response = client.post(
                    "/api/process",
                    data={"text": "今天心情很好，有个新想法，明天要完成报告"}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Check all required fields
                assert "record_id" in data
                assert "timestamp" in data
                assert "mood" in data
                assert "inspirations" in data
                assert "todos" in data
                
                # Check mood data
                assert data["mood"]["type"] == "开心"
                assert data["mood"]["intensity"] == 8
                
                # Check inspirations
                assert len(data["inspirations"]) == 1
                assert data["inspirations"][0]["core_idea"] == "新想法"
                
                # Check todos
                assert len(data["todos"]) == 1
                assert data["todos"][0]["task"] == "完成报告"
