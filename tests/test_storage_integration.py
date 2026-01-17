"""Integration tests for storage service.

This module tests the complete workflow of saving records and appending
related data to demonstrate the storage service functionality.

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.7
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from app.storage import StorageService
from app.models import (
    RecordData,
    ParsedData,
    MoodData,
    InspirationData,
    TodoData
)


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def storage_service(temp_data_dir):
    """Create a StorageService instance with temporary directory."""
    return StorageService(temp_data_dir)


class TestStorageIntegration:
    """Integration tests for complete storage workflow."""
    
    def test_complete_workflow_with_all_data(self, storage_service):
        """Test complete workflow: save record and append all related data."""
        # Create a complete record
        timestamp = "2024-01-01T12:00:00Z"
        mood = MoodData(type="开心", intensity=8, keywords=["愉快", "放松"])
        inspirations = [
            InspirationData(core_idea="新项目想法", tags=["创新", "技术"], category="工作"),
            InspirationData(core_idea="周末计划", tags=["休闲"], category="生活")
        ]
        todos = [
            TodoData(task="完成报告", time="明天下午", location="办公室"),
            TodoData(task="买菜", time="今晚", location="超市")
        ]
        
        record = RecordData(
            record_id="",  # Will be generated
            timestamp=timestamp,
            input_type="text",
            original_text="今天很开心，想到一个新项目想法，还要完成报告和买菜",
            parsed_data=ParsedData(
                mood=mood,
                inspirations=inspirations,
                todos=todos
            )
        )
        
        # Save record
        record_id = storage_service.save_record(record)
        assert record_id
        
        # Append mood
        storage_service.append_mood(mood, record_id, timestamp)
        
        # Append inspirations
        storage_service.append_inspirations(inspirations, record_id, timestamp)
        
        # Append todos
        storage_service.append_todos(todos, record_id, timestamp)
        
        # Verify records.json
        with open(storage_service.records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        assert len(records) == 1
        assert records[0]["record_id"] == record_id
        assert records[0]["original_text"] == record.original_text
        
        # Verify moods.json
        with open(storage_service.moods_file, 'r', encoding='utf-8') as f:
            moods = json.load(f)
        assert len(moods) == 1
        assert moods[0]["record_id"] == record_id
        assert moods[0]["type"] == "开心"
        assert moods[0]["intensity"] == 8
        
        # Verify inspirations.json
        with open(storage_service.inspirations_file, 'r', encoding='utf-8') as f:
            all_inspirations = json.load(f)
        assert len(all_inspirations) == 2
        assert all_inspirations[0]["record_id"] == record_id
        assert all_inspirations[0]["core_idea"] == "新项目想法"
        assert all_inspirations[1]["core_idea"] == "周末计划"
        
        # Verify todos.json
        with open(storage_service.todos_file, 'r', encoding='utf-8') as f:
            all_todos = json.load(f)
        assert len(all_todos) == 2
        assert all_todos[0]["record_id"] == record_id
        assert all_todos[0]["task"] == "完成报告"
        assert all_todos[1]["task"] == "买菜"
    
    def test_multiple_records_workflow(self, storage_service):
        """Test saving multiple records and verifying data accumulation."""
        # First record
        record1 = RecordData(
            record_id="",
            timestamp="2024-01-01T12:00:00Z",
            input_type="text",
            original_text="今天很开心",
            parsed_data=ParsedData(
                mood=MoodData(type="开心", intensity=8)
            )
        )
        record_id1 = storage_service.save_record(record1)
        storage_service.append_mood(record1.parsed_data.mood, record_id1, record1.timestamp)
        
        # Second record
        record2 = RecordData(
            record_id="",
            timestamp="2024-01-01T13:00:00Z",
            input_type="text",
            original_text="有点焦虑",
            parsed_data=ParsedData(
                mood=MoodData(type="焦虑", intensity=6)
            )
        )
        record_id2 = storage_service.save_record(record2)
        storage_service.append_mood(record2.parsed_data.mood, record_id2, record2.timestamp)
        
        # Verify records accumulated
        with open(storage_service.records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        assert len(records) == 2
        
        # Verify moods accumulated
        with open(storage_service.moods_file, 'r', encoding='utf-8') as f:
            moods = json.load(f)
        assert len(moods) == 2
        assert moods[0]["type"] == "开心"
        assert moods[1]["type"] == "焦虑"
    
    def test_workflow_with_partial_data(self, storage_service):
        """Test workflow when only some data types are present."""
        # Record with only mood (no inspirations or todos)
        timestamp = "2024-01-01T12:00:00Z"
        mood = MoodData(type="平静", intensity=5)
        
        record = RecordData(
            record_id="",
            timestamp=timestamp,
            input_type="text",
            original_text="今天感觉很平静",
            parsed_data=ParsedData(mood=mood)
        )
        
        record_id = storage_service.save_record(record)
        storage_service.append_mood(mood, record_id, timestamp)
        
        # Empty lists should not create files
        storage_service.append_inspirations([], record_id, timestamp)
        storage_service.append_todos([], record_id, timestamp)
        
        # Verify only records.json and moods.json exist
        assert storage_service.records_file.exists()
        assert storage_service.moods_file.exists()
        assert not storage_service.inspirations_file.exists()
        assert not storage_service.todos_file.exists()
    
    def test_unique_id_generation_across_records(self, storage_service):
        """Test that each record gets a unique ID."""
        record_ids = []
        
        for i in range(5):
            record = RecordData(
                record_id="",
                timestamp=f"2024-01-01T{12+i}:00:00Z",
                input_type="text",
                original_text=f"测试文本 {i}",
                parsed_data=ParsedData()
            )
            record_id = storage_service.save_record(record)
            record_ids.append(record_id)
        
        # All IDs should be unique
        assert len(record_ids) == len(set(record_ids))
        
        # All IDs should be valid UUIDs (36 characters with hyphens)
        for record_id in record_ids:
            assert len(record_id) == 36
            assert record_id.count('-') == 4
