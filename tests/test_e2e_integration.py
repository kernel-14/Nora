"""End-to-end integration tests for Voice Text Processor.

This module tests the complete workflow from input to storage,
including audio processing, text processing, and error scenarios.

Requirements: All requirements (end-to-end validation)
"""

import os
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
from io import BytesIO
from fastapi.testclient import TestClient


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Close all logging handlers before cleanup to release file handles
    import logging
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)
    # Give Windows time to release file handles
    import time
    time.sleep(0.1)
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        # On Windows, sometimes files are still locked - ignore cleanup errors
        pass


@pytest.fixture
def test_client(temp_data_dir):
    """Create a test client with temporary data directory."""
    # Reset config
    import app.config
    app.config._config = None
    
    with patch.dict(os.environ, {
        "ZHIPU_API_KEY": "test_key_1234567890",
        "DATA_DIR": temp_data_dir,
        "LOG_FILE": str(Path(temp_data_dir) / "test.log")
    }, clear=True):
        from app.main import app
        with TestClient(app) as client:
            yield client


class TestAudioToStorageE2E:
    """End-to-end tests for audio processing workflow.
    
    Tests: 音频上传 → ASR → 语义解析 → 存储 → 响应
    """
    
    @patch("app.main.ASRService")
    @patch("app.main.SemanticParserService")
    def test_complete_audio_workflow_with_all_data(
        self, 
        mock_parser_class, 
        mock_asr_class, 
        test_client,
        temp_data_dir
    ):
        """Test complete audio workflow: upload → ASR → parsing → storage → response.
        
        This test validates the entire pipeline with all data types present.
        """
        # Mock ASR service
        mock_asr = MagicMock()
        mock_asr.transcribe = AsyncMock(
            return_value="今天心情很好，想到一个新项目想法，明天要完成报告"
        )
        mock_asr.close = AsyncMock()
        mock_asr_class.return_value = mock_asr
        
        # Mock semantic parser with complete data
        from app.models import MoodData, InspirationData, TodoData, ParsedData
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(return_value=ParsedData(
            mood=MoodData(type="开心", intensity=8, keywords=["愉快", "放松"]),
            inspirations=[
                InspirationData(core_idea="新项目想法", tags=["创新", "技术"], category="工作")
            ],
            todos=[
                TodoData(task="完成报告", time="明天", location="办公室")
            ]
        ))
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Create fake audio file
        audio_data = b"fake audio content for testing"
        files = {"audio": ("test.mp3", BytesIO(audio_data), "audio/mpeg")}
        
        # Make request
        response = test_client.post("/api/process", files=files)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "record_id" in data
        assert "timestamp" in data
        assert data["mood"]["type"] == "开心"
        assert data["mood"]["intensity"] == 8
        assert len(data["inspirations"]) == 1
        assert data["inspirations"][0]["core_idea"] == "新项目想法"
        assert len(data["todos"]) == 1
        assert data["todos"][0]["task"] == "完成报告"
        
        # Verify ASR was called
        mock_asr.transcribe.assert_called_once()
        
        # Verify semantic parser was called with transcribed text
        mock_parser.parse.assert_called_once_with(
            "今天心情很好，想到一个新项目想法，明天要完成报告"
        )
        
        # Verify storage - check all JSON files
        records_file = Path(temp_data_dir) / "records.json"
        moods_file = Path(temp_data_dir) / "moods.json"
        inspirations_file = Path(temp_data_dir) / "inspirations.json"
        todos_file = Path(temp_data_dir) / "todos.json"
        
        # Check records.json
        assert records_file.exists()
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        assert len(records) == 1
        assert records[0]["record_id"] == data["record_id"]
        assert records[0]["input_type"] == "audio"
        assert records[0]["original_text"] == "今天心情很好，想到一个新项目想法，明天要完成报告"
        
        # Check moods.json
        assert moods_file.exists()
        with open(moods_file, 'r', encoding='utf-8') as f:
            moods = json.load(f)
        assert len(moods) == 1
        assert moods[0]["record_id"] == data["record_id"]
        assert moods[0]["type"] == "开心"
        
        # Check inspirations.json
        assert inspirations_file.exists()
        with open(inspirations_file, 'r', encoding='utf-8') as f:
            inspirations = json.load(f)
        assert len(inspirations) == 1
        assert inspirations[0]["record_id"] == data["record_id"]
        assert inspirations[0]["core_idea"] == "新项目想法"
        
        # Check todos.json
        assert todos_file.exists()
        with open(todos_file, 'r', encoding='utf-8') as f:
            todos = json.load(f)
        assert len(todos) == 1
        assert todos[0]["record_id"] == data["record_id"]
        assert todos[0]["task"] == "完成报告"

    @patch("app.main.ASRService")
    @patch("app.main.SemanticParserService")
    def test_audio_workflow_with_partial_data(
        self, 
        mock_parser_class, 
        mock_asr_class, 
        test_client,
        temp_data_dir
    ):
        """Test audio workflow with only some data types present."""
        # Mock ASR service
        mock_asr = MagicMock()
        mock_asr.transcribe = AsyncMock(return_value="今天感觉很平静")
        mock_asr.close = AsyncMock()
        mock_asr_class.return_value = mock_asr
        
        # Mock semantic parser with only mood (no inspirations or todos)
        from app.models import MoodData, ParsedData
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(return_value=ParsedData(
            mood=MoodData(type="平静", intensity=5, keywords=["安静"])
        ))
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Create fake audio file
        audio_data = b"fake audio content"
        files = {"audio": ("test.wav", BytesIO(audio_data), "audio/wav")}
        
        # Make request
        response = test_client.post("/api/process", files=files)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["mood"]["type"] == "平静"
        assert len(data["inspirations"]) == 0
        assert len(data["todos"]) == 0
        
        # Verify storage - only records.json and moods.json should exist
        records_file = Path(temp_data_dir) / "records.json"
        moods_file = Path(temp_data_dir) / "moods.json"
        inspirations_file = Path(temp_data_dir) / "inspirations.json"
        todos_file = Path(temp_data_dir) / "todos.json"
        
        assert records_file.exists()
        assert moods_file.exists()
        assert not inspirations_file.exists()
        assert not todos_file.exists()
    
    @patch("app.main.ASRService")
    @patch("app.main.SemanticParserService")
    def test_audio_workflow_with_multiple_items(
        self, 
        mock_parser_class, 
        mock_asr_class, 
        test_client,
        temp_data_dir
    ):
        """Test audio workflow with multiple inspirations and todos."""
        # Mock ASR service
        mock_asr = MagicMock()
        mock_asr.transcribe = AsyncMock(
            return_value="有三个想法和两个任务要做"
        )
        mock_asr.close = AsyncMock()
        mock_asr_class.return_value = mock_asr
        
        # Mock semantic parser with multiple items
        from app.models import InspirationData, TodoData, ParsedData
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(return_value=ParsedData(
            inspirations=[
                InspirationData(core_idea="想法1", tags=["标签1"], category="工作"),
                InspirationData(core_idea="想法2", tags=["标签2"], category="生活"),
                InspirationData(core_idea="想法3", tags=["标签3"], category="学习")
            ],
            todos=[
                TodoData(task="任务1", time="今天", location="家里"),
                TodoData(task="任务2", time="明天", location="公司")
            ]
        ))
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Create fake audio file
        audio_data = b"fake audio content"
        files = {"audio": ("test.m4a", BytesIO(audio_data), "audio/m4a")}
        
        # Make request
        response = test_client.post("/api/process", files=files)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data["inspirations"]) == 3
        assert len(data["todos"]) == 2
        
        # Verify storage
        inspirations_file = Path(temp_data_dir) / "inspirations.json"
        todos_file = Path(temp_data_dir) / "todos.json"
        
        with open(inspirations_file, 'r', encoding='utf-8') as f:
            inspirations = json.load(f)
        assert len(inspirations) == 3
        
        with open(todos_file, 'r', encoding='utf-8') as f:
            todos = json.load(f)
        assert len(todos) == 2


class TestTextToStorageE2E:
    """End-to-end tests for text processing workflow.
    
    Tests: 文本提交 → 语义解析 → 存储 → 响应
    """
    
    @patch("app.main.SemanticParserService")
    def test_complete_text_workflow_with_all_data(
        self, 
        mock_parser_class, 
        test_client,
        temp_data_dir
    ):
        """Test complete text workflow: submit → parsing → storage → response.
        
        This test validates the entire pipeline for text input with all data types.
        """
        # Mock semantic parser with complete data
        from app.models import MoodData, InspirationData, TodoData, ParsedData
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(return_value=ParsedData(
            mood=MoodData(type="焦虑", intensity=6, keywords=["紧张", "担心"]),
            inspirations=[
                InspirationData(core_idea="解决方案", tags=["问题解决"], category="工作")
            ],
            todos=[
                TodoData(task="准备会议", time="下午3点", location="会议室"),
                TodoData(task="发送邮件", time="今晚", location=None)
            ]
        ))
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Make request with text
        text_input = "有点焦虑，想到一个解决方案，下午要准备会议，今晚要发送邮件"
        response = test_client.post(
            "/api/process",
            data={"text": text_input}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "record_id" in data
        assert "timestamp" in data
        assert data["mood"]["type"] == "焦虑"
        assert data["mood"]["intensity"] == 6
        assert len(data["inspirations"]) == 1
        assert len(data["todos"]) == 2
        
        # Verify semantic parser was called with input text
        mock_parser.parse.assert_called_once_with(text_input)
        
        # Verify storage - check all JSON files
        records_file = Path(temp_data_dir) / "records.json"
        moods_file = Path(temp_data_dir) / "moods.json"
        inspirations_file = Path(temp_data_dir) / "inspirations.json"
        todos_file = Path(temp_data_dir) / "todos.json"
        
        # Check records.json
        assert records_file.exists()
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        assert len(records) == 1
        assert records[0]["record_id"] == data["record_id"]
        assert records[0]["input_type"] == "text"
        assert records[0]["original_text"] == text_input
        
        # Check moods.json
        assert moods_file.exists()
        with open(moods_file, 'r', encoding='utf-8') as f:
            moods = json.load(f)
        assert len(moods) == 1
        assert moods[0]["type"] == "焦虑"
        
        # Check inspirations.json
        assert inspirations_file.exists()
        with open(inspirations_file, 'r', encoding='utf-8') as f:
            inspirations = json.load(f)
        assert len(inspirations) == 1
        
        # Check todos.json
        assert todos_file.exists()
        with open(todos_file, 'r', encoding='utf-8') as f:
            todos = json.load(f)
        assert len(todos) == 2
    
    @patch("app.main.SemanticParserService")
    def test_text_workflow_with_no_data(
        self, 
        mock_parser_class, 
        test_client,
        temp_data_dir
    ):
        """Test text workflow when no structured data is extracted."""
        # Mock semantic parser with empty data
        from app.models import ParsedData
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(return_value=ParsedData())
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Make request with text
        response = test_client.post(
            "/api/process",
            data={"text": "这是一段普通的文本"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["mood"] is None
        assert len(data["inspirations"]) == 0
        assert len(data["todos"]) == 0
        
        # Verify storage - only records.json should exist
        records_file = Path(temp_data_dir) / "records.json"
        moods_file = Path(temp_data_dir) / "moods.json"
        inspirations_file = Path(temp_data_dir) / "inspirations.json"
        todos_file = Path(temp_data_dir) / "todos.json"
        
        assert records_file.exists()
        assert not moods_file.exists()
        assert not inspirations_file.exists()
        assert not todos_file.exists()

    @patch("app.main.SemanticParserService")
    def test_text_workflow_with_utf8_characters(
        self, 
        mock_parser_class, 
        test_client,
        temp_data_dir
    ):
        """Test text workflow with various UTF-8 characters (Chinese, emoji, etc.)."""
        # Mock semantic parser
        from app.models import MoodData, ParsedData
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(return_value=ParsedData(
            mood=MoodData(type="开心😊", intensity=9, keywords=["快乐", "幸福"])
        ))
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Make request with UTF-8 text including emoji
        text_input = "今天超级开心😊！感觉特别幸福💖"
        response = test_client.post(
            "/api/process",
            data={"text": text_input}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["mood"]["type"] == "开心😊"
        
        # Verify storage preserves UTF-8
        records_file = Path(temp_data_dir) / "records.json"
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        assert records[0]["original_text"] == text_input
    
    @patch("app.main.SemanticParserService")
    def test_multiple_text_submissions(
        self, 
        mock_parser_class, 
        test_client,
        temp_data_dir
    ):
        """Test multiple text submissions accumulate in storage."""
        # Mock semantic parser
        from app.models import MoodData, ParsedData
        mock_parser = MagicMock()
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # First submission
        mock_parser.parse = AsyncMock(return_value=ParsedData(
            mood=MoodData(type="开心", intensity=8)
        ))
        response1 = test_client.post(
            "/api/process",
            data={"text": "今天很开心"}
        )
        assert response1.status_code == 200
        
        # Second submission
        mock_parser.parse = AsyncMock(return_value=ParsedData(
            mood=MoodData(type="平静", intensity=5)
        ))
        response2 = test_client.post(
            "/api/process",
            data={"text": "现在很平静"}
        )
        assert response2.status_code == 200
        
        # Verify both records are stored
        records_file = Path(temp_data_dir) / "records.json"
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        assert len(records) == 2
        
        # Verify both moods are stored
        moods_file = Path(temp_data_dir) / "moods.json"
        with open(moods_file, 'r', encoding='utf-8') as f:
            moods = json.load(f)
        assert len(moods) == 2
        assert moods[0]["type"] == "开心"
        assert moods[1]["type"] == "平静"


class TestErrorScenariosE2E:
    """End-to-end tests for error scenarios.
    
    Tests: 错误场景的端到端处理
    """
    
    def test_validation_error_no_input(self, test_client, temp_data_dir):
        """Test validation error when no input is provided."""
        response = test_client.post("/api/process")
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "timestamp" in data
        assert "请提供音频文件或文本内容" in data["error"]
        
        # Verify no files are created
        records_file = Path(temp_data_dir) / "records.json"
        assert not records_file.exists()

    def test_validation_error_both_inputs(self, test_client, temp_data_dir):
        """Test validation error when both audio and text are provided."""
        audio_data = b"fake audio"
        files = {"audio": ("test.mp3", BytesIO(audio_data), "audio/mpeg")}
        
        response = test_client.post(
            "/api/process",
            files=files,
            data={"text": "some text"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        
        # Verify no files are created
        records_file = Path(temp_data_dir) / "records.json"
        assert not records_file.exists()
    
    def test_validation_error_empty_text(self, test_client, temp_data_dir):
        """Test validation error when text is empty."""
        response = test_client.post(
            "/api/process",
            data={"text": ""}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        # Empty string is treated as no input by FastAPI
        assert "请提供音频文件或文本内容" in data["error"]
    
    def test_validation_error_unsupported_audio_format(self, test_client, temp_data_dir):
        """Test validation error for unsupported audio format."""
        audio_data = b"fake audio"
        files = {"audio": ("test.ogg", BytesIO(audio_data), "audio/ogg")}
        
        response = test_client.post("/api/process", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "不支持的音频格式" in data["error"]
        
        # Verify no files are created
        records_file = Path(temp_data_dir) / "records.json"
        assert not records_file.exists()
    
    @patch("app.main.ASRService")
    def test_asr_error_end_to_end(
        self, 
        mock_asr_class, 
        test_client,
        temp_data_dir
    ):
        """Test end-to-end error handling when ASR service fails."""
        # Mock ASR service to raise error
        from app.asr_service import ASRServiceError
        mock_asr = MagicMock()
        mock_asr.transcribe = AsyncMock(
            side_effect=ASRServiceError("API连接超时")
        )
        mock_asr.close = AsyncMock()
        mock_asr_class.return_value = mock_asr
        
        # Create audio file
        audio_data = b"fake audio content"
        files = {"audio": ("test.mp3", BytesIO(audio_data), "audio/mpeg")}
        
        # Make request
        response = test_client.post("/api/process", files=files)
        
        # Verify error response
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "语音识别服务不可用" in data["error"]
        assert "timestamp" in data
        
        # Verify no files are created
        records_file = Path(temp_data_dir) / "records.json"
        assert not records_file.exists()
    
    @patch("app.main.SemanticParserService")
    def test_semantic_parser_error_end_to_end(
        self, 
        mock_parser_class, 
        test_client,
        temp_data_dir
    ):
        """Test end-to-end error handling when semantic parser fails."""
        # Mock semantic parser to raise error
        from app.semantic_parser import SemanticParserError
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(
            side_effect=SemanticParserError("API返回格式错误")
        )
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Make request
        response = test_client.post(
            "/api/process",
            data={"text": "测试文本"}
        )
        
        # Verify error response
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "语义解析服务不可用" in data["error"]
        assert "timestamp" in data
        
        # Verify no files are created
        records_file = Path(temp_data_dir) / "records.json"
        assert not records_file.exists()

    @patch("app.main.SemanticParserService")
    @patch("app.main.StorageService")
    def test_storage_error_end_to_end(
        self, 
        mock_storage_class,
        mock_parser_class, 
        test_client,
        temp_data_dir
    ):
        """Test end-to-end error handling when storage fails."""
        # Mock semantic parser
        from app.models import ParsedData
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(return_value=ParsedData())
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Mock storage service to raise error
        from app.storage import StorageError
        mock_storage = MagicMock()
        mock_storage.save_record = MagicMock(
            side_effect=StorageError("磁盘空间不足")
        )
        mock_storage_class.return_value = mock_storage
        
        # Make request
        response = test_client.post(
            "/api/process",
            data={"text": "测试文本"}
        )
        
        # Verify error response
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "数据存储失败" in data["error"]
        assert "timestamp" in data
    
    @patch("app.main.ASRService")
    @patch("app.main.SemanticParserService")
    def test_asr_empty_result_end_to_end(
        self, 
        mock_parser_class,
        mock_asr_class, 
        test_client,
        temp_data_dir
    ):
        """Test end-to-end handling when ASR returns empty text."""
        # Mock ASR service to return empty string
        mock_asr = MagicMock()
        mock_asr.transcribe = AsyncMock(return_value="")
        mock_asr.close = AsyncMock()
        mock_asr_class.return_value = mock_asr
        
        # Mock semantic parser
        from app.models import ParsedData
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(return_value=ParsedData())
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Create audio file
        audio_data = b"silent audio"
        files = {"audio": ("test.mp3", BytesIO(audio_data), "audio/mpeg")}
        
        # Make request
        response = test_client.post("/api/process", files=files)
        
        # Should succeed but with empty text
        assert response.status_code == 200
        data = response.json()
        
        # Verify record was saved with empty text
        records_file = Path(temp_data_dir) / "records.json"
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        assert len(records) == 1
        assert records[0]["original_text"] == ""


class TestConcurrentRequestsE2E:
    """End-to-end tests for concurrent request handling."""
    
    @patch("app.main.SemanticParserService")
    def test_concurrent_text_submissions(
        self, 
        mock_parser_class, 
        test_client,
        temp_data_dir
    ):
        """Test that concurrent requests are handled correctly and stored separately."""
        # Mock semantic parser
        from app.models import MoodData, ParsedData
        mock_parser = MagicMock()
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Simulate multiple concurrent requests
        responses = []
        for i in range(5):
            mock_parser.parse = AsyncMock(return_value=ParsedData(
                mood=MoodData(type=f"情绪{i}", intensity=i+1)
            ))
            response = test_client.post(
                "/api/process",
                data={"text": f"测试文本{i}"}
            )
            responses.append(response)
        
        # Verify all requests succeeded
        for response in responses:
            assert response.status_code == 200
        
        # Verify all records are stored with unique IDs
        records_file = Path(temp_data_dir) / "records.json"
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        assert len(records) == 5
        
        # Check all record IDs are unique
        record_ids = [r["record_id"] for r in records]
        assert len(record_ids) == len(set(record_ids))
        
        # Verify all moods are stored
        moods_file = Path(temp_data_dir) / "moods.json"
        with open(moods_file, 'r', encoding='utf-8') as f:
            moods = json.load(f)
        assert len(moods) == 5


class TestDataIntegrityE2E:
    """End-to-end tests for data integrity across the pipeline."""
    
    @patch("app.main.SemanticParserService")
    def test_record_id_consistency_across_files(
        self, 
        mock_parser_class, 
        test_client,
        temp_data_dir
    ):
        """Test that record_id is consistent across all JSON files."""
        # Mock semantic parser with all data types
        from app.models import MoodData, InspirationData, TodoData, ParsedData
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(return_value=ParsedData(
            mood=MoodData(type="开心", intensity=8),
            inspirations=[InspirationData(core_idea="想法", tags=[], category="生活")],
            todos=[TodoData(task="任务")]
        ))
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Make request
        response = test_client.post(
            "/api/process",
            data={"text": "测试数据完整性"}
        )
        
        assert response.status_code == 200
        record_id = response.json()["record_id"]
        
        # Verify record_id is consistent across all files
        records_file = Path(temp_data_dir) / "records.json"
        moods_file = Path(temp_data_dir) / "moods.json"
        inspirations_file = Path(temp_data_dir) / "inspirations.json"
        todos_file = Path(temp_data_dir) / "todos.json"
        
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        assert records[0]["record_id"] == record_id
        
        with open(moods_file, 'r', encoding='utf-8') as f:
            moods = json.load(f)
        assert moods[0]["record_id"] == record_id
        
        with open(inspirations_file, 'r', encoding='utf-8') as f:
            inspirations = json.load(f)
        assert inspirations[0]["record_id"] == record_id
        
        with open(todos_file, 'r', encoding='utf-8') as f:
            todos = json.load(f)
        assert todos[0]["record_id"] == record_id
    
    @patch("app.main.SemanticParserService")
    def test_timestamp_consistency(
        self, 
        mock_parser_class, 
        test_client,
        temp_data_dir
    ):
        """Test that timestamps are consistent and properly formatted."""
        # Mock semantic parser
        from app.models import MoodData, ParsedData
        mock_parser = MagicMock()
        mock_parser.parse = AsyncMock(return_value=ParsedData(
            mood=MoodData(type="开心", intensity=8)
        ))
        mock_parser.close = AsyncMock()
        mock_parser_class.return_value = mock_parser
        
        # Make request
        response = test_client.post(
            "/api/process",
            data={"text": "测试时间戳"}
        )
        
        assert response.status_code == 200
        timestamp = response.json()["timestamp"]
        
        # Verify timestamp format (ISO 8601 with Z suffix)
        assert timestamp.endswith("Z")
        assert "T" in timestamp
        
        # Verify timestamp is consistent in storage
        moods_file = Path(temp_data_dir) / "moods.json"
        with open(moods_file, 'r', encoding='utf-8') as f:
            moods = json.load(f)
        assert moods[0]["timestamp"] == timestamp
