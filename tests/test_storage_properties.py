"""Property-based tests for storage service.

This module uses hypothesis to verify that storage properties hold across
many random inputs, ensuring data persistence integrity.

Requirements: 7.1, 7.2, 7.3, 7.4
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from hypothesis import given, strategies as st
from hypothesis import settings

from app.storage import StorageService, StorageError
from app.models import (
    RecordData,
    ParsedData,
    MoodData,
    InspirationData,
    TodoData
)


# Note: We don't use pytest fixtures with hypothesis tests because
# fixtures are not reset between examples. Instead, we create temp
# directories directly in the test methods.


# Custom strategies for generating valid model data
@st.composite
def mood_data_strategy(draw):
    """Generate valid MoodData instances."""
    mood_type = draw(st.one_of(st.none(), st.text(min_size=1, max_size=20)))
    intensity = draw(st.one_of(st.none(), st.integers(min_value=1, max_value=10)))
    keywords = draw(st.lists(st.text(min_size=1, max_size=15), min_size=0, max_size=5))
    
    return MoodData(type=mood_type, intensity=intensity, keywords=keywords)


@st.composite
def inspiration_data_strategy(draw):
    """Generate valid InspirationData instances."""
    core_idea = draw(st.text(min_size=1, max_size=20))
    tags = draw(st.lists(st.text(min_size=1, max_size=10), min_size=0, max_size=5))
    category = draw(st.sampled_from(["工作", "生活", "学习", "创意"]))
    
    return InspirationData(core_idea=core_idea, tags=tags, category=category)


@st.composite
def todo_data_strategy(draw):
    """Generate valid TodoData instances."""
    task = draw(st.text(min_size=1, max_size=50))
    time = draw(st.one_of(st.none(), st.text(min_size=1, max_size=20)))
    location = draw(st.one_of(st.none(), st.text(min_size=1, max_size=20)))
    status = "pending"  # Always default to pending for new todos
    
    return TodoData(task=task, time=time, location=location, status=status)


@st.composite
def parsed_data_strategy(draw):
    """Generate valid ParsedData instances with optional mood, inspirations, and todos."""
    # Randomly include or exclude mood
    has_mood = draw(st.booleans())
    mood = draw(mood_data_strategy()) if has_mood else None
    
    # Generate 0-3 inspirations
    inspirations = draw(st.lists(inspiration_data_strategy(), min_size=0, max_size=3))
    
    # Generate 0-3 todos
    todos = draw(st.lists(todo_data_strategy(), min_size=0, max_size=3))
    
    return ParsedData(mood=mood, inspirations=inspirations, todos=todos)


@st.composite
def record_data_strategy(draw):
    """Generate valid RecordData instances."""
    record_id = draw(st.text(min_size=1, max_size=36))  # UUID-like length
    timestamp = draw(st.text(min_size=10, max_size=30))  # ISO timestamp-like
    input_type = draw(st.sampled_from(["audio", "text"]))
    original_text = draw(st.text(min_size=1, max_size=200))
    parsed_data = draw(parsed_data_strategy())
    
    return RecordData(
        record_id=record_id,
        timestamp=timestamp,
        input_type=input_type,
        original_text=original_text,
        parsed_data=parsed_data
    )


class TestStorageServiceProperties:
    """Property-based tests for StorageService.
    
    **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
    """
    
    @given(record=record_data_strategy())
    @settings(max_examples=100)
    def test_property_9_data_persistence_integrity(self, record):
        """
        Property 9: 数据持久化完整性
        
        For any successfully processed record, it should be saved in records.json,
        and if it contains mood/inspiration/todo data, it should also be appended
        to the corresponding moods.json, inspirations.json, todos.json files.
        
        **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
        """
        # Create a fresh temporary directory and storage service for each example
        temp_dir = tempfile.mkdtemp()
        try:
            storage_service = StorageService(temp_dir)
            
            # Save the complete record
            returned_record_id = storage_service.save_record(record)
            
            # Property 1: Record should be saved in records.json
            assert storage_service.records_file.exists()
            with open(storage_service.records_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            assert len(records) >= 1
            # Find the saved record
            saved_record = None
            for r in records:
                if r["record_id"] == returned_record_id:
                    saved_record = r
                    break
            
            assert saved_record is not None, "Record should be saved in records.json"
            assert saved_record["timestamp"] == record.timestamp
            assert saved_record["input_type"] == record.input_type
            assert saved_record["original_text"] == record.original_text
            
            # Property 2: If mood data exists, it should be in moods.json
            if record.parsed_data.mood is not None:
                storage_service.append_mood(
                    record.parsed_data.mood,
                    returned_record_id,
                    record.timestamp
                )
                
                assert storage_service.moods_file.exists()
                with open(storage_service.moods_file, 'r', encoding='utf-8') as f:
                    moods = json.load(f)
                
                # Find the mood entry for this record
                mood_entries = [m for m in moods if m["record_id"] == returned_record_id]
                assert len(mood_entries) >= 1, "Mood should be saved in moods.json"
                
                mood_entry = mood_entries[-1]  # Get the last one
                assert mood_entry["record_id"] == returned_record_id
                assert mood_entry["timestamp"] == record.timestamp
                assert mood_entry["type"] == record.parsed_data.mood.type
                assert mood_entry["intensity"] == record.parsed_data.mood.intensity
                assert mood_entry["keywords"] == record.parsed_data.mood.keywords
            
            # Property 3: If inspiration data exists, it should be in inspirations.json
            if record.parsed_data.inspirations:
                storage_service.append_inspirations(
                    record.parsed_data.inspirations,
                    returned_record_id,
                    record.timestamp
                )
                
                assert storage_service.inspirations_file.exists()
                with open(storage_service.inspirations_file, 'r', encoding='utf-8') as f:
                    inspirations = json.load(f)
                
                # Find inspiration entries for this record
                inspiration_entries = [i for i in inspirations if i["record_id"] == returned_record_id]
                assert len(inspiration_entries) == len(record.parsed_data.inspirations), \
                    "All inspirations should be saved in inspirations.json"
                
                # Verify each inspiration - use a copy to track matched entries
                remaining_entries = inspiration_entries.copy()
                for inspiration in record.parsed_data.inspirations:
                    # Find matching entry (may not be in same order)
                    matching_entry = None
                    for idx, entry in enumerate(remaining_entries):
                        if (entry["core_idea"] == inspiration.core_idea and
                            entry["category"] == inspiration.category and
                            entry["tags"] == inspiration.tags):
                            matching_entry = entry
                            remaining_entries.pop(idx)
                            break
                    
                    assert matching_entry is not None, \
                        f"Could not find matching entry for inspiration: {inspiration}"
                    assert matching_entry["record_id"] == returned_record_id
                    assert matching_entry["timestamp"] == record.timestamp
            
            # Property 4: If todo data exists, it should be in todos.json
            if record.parsed_data.todos:
                storage_service.append_todos(
                    record.parsed_data.todos,
                    returned_record_id,
                    record.timestamp
                )
                
                assert storage_service.todos_file.exists()
                with open(storage_service.todos_file, 'r', encoding='utf-8') as f:
                    todos = json.load(f)
                
                # Find todo entries for this record
                todo_entries = [t for t in todos if t["record_id"] == returned_record_id]
                assert len(todo_entries) == len(record.parsed_data.todos), \
                    "All todos should be saved in todos.json"
                
                # Verify each todo - use a copy to track matched entries
                remaining_entries = todo_entries.copy()
                for todo in record.parsed_data.todos:
                    # Find matching entry (may not be in same order)
                    matching_entry = None
                    for idx, entry in enumerate(remaining_entries):
                        if (entry["task"] == todo.task and
                            entry["time"] == todo.time and
                            entry["location"] == todo.location and
                            entry["status"] == todo.status):
                            matching_entry = entry
                            remaining_entries.pop(idx)
                            break
                    
                    assert matching_entry is not None, \
                        f"Could not find matching entry for todo: {todo}"
                    assert matching_entry["record_id"] == returned_record_id
                    assert matching_entry["timestamp"] == record.timestamp
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
    
    @given(records=st.lists(record_data_strategy(), min_size=1, max_size=5))
    @settings(max_examples=100)
    def test_property_9_multiple_records_persistence(self, records):
        """
        Property 9: 数据持久化完整性 - Multiple Records
        
        For any list of successfully processed records, all records should be
        saved and retrievable from their respective JSON files.
        
        **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
        """
        # Create a fresh temporary directory and storage service for each example
        temp_dir = tempfile.mkdtemp()
        try:
            storage_service = StorageService(temp_dir)
            
            saved_record_ids = []
            
            # Save all records
            for record in records:
                record_id = storage_service.save_record(record)
                saved_record_ids.append(record_id)
                
                # Append mood if exists
                if record.parsed_data.mood is not None:
                    storage_service.append_mood(
                        record.parsed_data.mood,
                        record_id,
                        record.timestamp
                    )
                
                # Append inspirations if exist
                if record.parsed_data.inspirations:
                    storage_service.append_inspirations(
                        record.parsed_data.inspirations,
                        record_id,
                        record.timestamp
                    )
                
                # Append todos if exist
                if record.parsed_data.todos:
                    storage_service.append_todos(
                        record.parsed_data.todos,
                        record_id,
                        record.timestamp
                    )
            
            # Verify all records are saved
            with open(storage_service.records_file, 'r', encoding='utf-8') as f:
                saved_records = json.load(f)
            
            assert len(saved_records) >= len(records), \
                "All records should be saved in records.json"
            
            # Verify each record can be found
            for record_id in saved_record_ids:
                found = any(r["record_id"] == record_id for r in saved_records)
                assert found, f"Record {record_id} should be in records.json"
            
            # Count expected moods, inspirations, and todos
            expected_moods = sum(1 for r in records if r.parsed_data.mood is not None)
            expected_inspirations = sum(len(r.parsed_data.inspirations) for r in records)
            expected_todos = sum(len(r.parsed_data.todos) for r in records)
            
            # Verify moods count
            if expected_moods > 0:
                assert storage_service.moods_file.exists()
                with open(storage_service.moods_file, 'r', encoding='utf-8') as f:
                    moods = json.load(f)
                assert len(moods) >= expected_moods, \
                    f"Expected at least {expected_moods} moods, found {len(moods)}"
            
            # Verify inspirations count
            if expected_inspirations > 0:
                assert storage_service.inspirations_file.exists()
                with open(storage_service.inspirations_file, 'r', encoding='utf-8') as f:
                    inspirations = json.load(f)
                assert len(inspirations) >= expected_inspirations, \
                    f"Expected at least {expected_inspirations} inspirations, found {len(inspirations)}"
            
            # Verify todos count
            if expected_todos > 0:
                assert storage_service.todos_file.exists()
                with open(storage_service.todos_file, 'r', encoding='utf-8') as f:
                    todos = json.load(f)
                assert len(todos) >= expected_todos, \
                    f"Expected at least {expected_todos} todos, found {len(todos)}"
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
    
    @given(
        record=record_data_strategy(),
        has_mood=st.booleans(),
        has_inspirations=st.booleans(),
        has_todos=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_9_selective_data_persistence(
        self, record, has_mood, has_inspirations, has_todos
    ):
        """
        Property 9: 数据持久化完整性 - Selective Persistence
        
        For any record, only the data types that exist should be persisted
        to their respective files. Empty data should not create unnecessary entries.
        
        **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
        """
        # Create a fresh temporary directory and storage service for each example
        temp_dir = tempfile.mkdtemp()
        try:
            storage_service = StorageService(temp_dir)
            
            # Modify record based on flags
            if not has_mood:
                record.parsed_data.mood = None
            if not has_inspirations:
                record.parsed_data.inspirations = []
            if not has_todos:
                record.parsed_data.todos = []
            
            # Save the record
            record_id = storage_service.save_record(record)
            
            # Always save mood/inspirations/todos if they exist
            if record.parsed_data.mood is not None:
                storage_service.append_mood(
                    record.parsed_data.mood,
                    record_id,
                    record.timestamp
                )
            
            if record.parsed_data.inspirations:
                storage_service.append_inspirations(
                    record.parsed_data.inspirations,
                    record_id,
                    record.timestamp
                )
            
            if record.parsed_data.todos:
                storage_service.append_todos(
                    record.parsed_data.todos,
                    record_id,
                    record.timestamp
                )
            
            # Verify records.json always exists
            assert storage_service.records_file.exists()
            
            # Verify mood file existence matches data presence
            if has_mood and record.parsed_data.mood is not None:
                assert storage_service.moods_file.exists(), \
                    "moods.json should exist when mood data is present"
            
            # Verify inspirations file existence matches data presence
            if has_inspirations and record.parsed_data.inspirations:
                assert storage_service.inspirations_file.exists(), \
                    "inspirations.json should exist when inspiration data is present"
            
            # Verify todos file existence matches data presence
            if has_todos and record.parsed_data.todos:
                assert storage_service.todos_file.exists(), \
                    "todos.json should exist when todo data is present"
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)

    @given(
        file_type=st.sampled_from(["records", "moods", "inspirations", "todos"])
    )
    @settings(max_examples=100)
    def test_property_10_file_initialization(self, file_type):
        """
        Property 10: 文件初始化
        
        For any non-existent JSON file, when first written to, the system should
        create the file and initialize it as an empty array [].
        
        **Validates: Requirements 7.5**
        """
        # Create a fresh temporary directory and storage service for each example
        temp_dir = tempfile.mkdtemp()
        try:
            storage_service = StorageService(temp_dir)
            
            # Map file type to file path
            file_map = {
                "records": storage_service.records_file,
                "moods": storage_service.moods_file,
                "inspirations": storage_service.inspirations_file,
                "todos": storage_service.todos_file
            }
            
            target_file = file_map[file_type]
            
            # Verify file doesn't exist initially
            assert not target_file.exists(), \
                f"{file_type}.json should not exist initially"
            
            # Trigger file initialization by calling _ensure_file_exists
            storage_service._ensure_file_exists(target_file)
            
            # Property 1: File should now exist
            assert target_file.exists(), \
                f"{file_type}.json should be created"
            
            # Property 2: File should be initialized as empty array
            with open(target_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            assert isinstance(content, list), \
                f"{file_type}.json should contain a list"
            assert content == [], \
                f"{file_type}.json should be initialized as empty array []"
            
            # Property 3: File should be valid JSON
            # (already verified by json.load above, but let's be explicit)
            with open(target_file, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            # Should be able to parse without error
            parsed = json.loads(raw_content)
            assert parsed == []
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
    
    @given(
        operations=st.lists(
            st.sampled_from(["records", "moods", "inspirations", "todos"]),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=100)
    def test_property_10_file_initialization_idempotent(self, operations):
        """
        Property 10: 文件初始化 - Idempotency
        
        For any sequence of file initialization operations, calling _ensure_file_exists
        multiple times should be idempotent - it should not corrupt or overwrite
        existing data.
        
        **Validates: Requirements 7.5**
        """
        # Create a fresh temporary directory and storage service for each example
        temp_dir = tempfile.mkdtemp()
        try:
            storage_service = StorageService(temp_dir)
            
            file_map = {
                "records": storage_service.records_file,
                "moods": storage_service.moods_file,
                "inspirations": storage_service.inspirations_file,
                "todos": storage_service.todos_file
            }
            
            # Track which files have been initialized
            initialized_files = set()
            
            for file_type in operations:
                target_file = file_map[file_type]
                
                # Call _ensure_file_exists
                storage_service._ensure_file_exists(target_file)
                
                # File should exist
                assert target_file.exists()
                
                # Read current content
                with open(target_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                if file_type not in initialized_files:
                    # First time - should be empty array
                    assert content == [], \
                        f"First initialization of {file_type}.json should create empty array"
                    initialized_files.add(file_type)
                else:
                    # Subsequent calls - should preserve empty array
                    # (In real usage, data would be added between calls,
                    # but _ensure_file_exists should not overwrite)
                    assert isinstance(content, list), \
                        f"Subsequent calls should preserve list structure"
            
            # Verify all unique files were created
            unique_files = set(operations)
            for file_type in unique_files:
                target_file = file_map[file_type]
                assert target_file.exists(), \
                    f"{file_type}.json should exist after operations"
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
    
    @given(record=record_data_strategy())
    @settings(max_examples=100)
    def test_property_10_file_initialization_on_first_write(self, record):
        """
        Property 10: 文件初始化 - First Write
        
        For any record being saved, if the JSON files don't exist, they should
        be automatically created and initialized before writing data.
        
        **Validates: Requirements 7.5**
        """
        # Create a fresh temporary directory and storage service for each example
        temp_dir = tempfile.mkdtemp()
        try:
            storage_service = StorageService(temp_dir)
            
            # Verify no files exist initially
            assert not storage_service.records_file.exists()
            assert not storage_service.moods_file.exists()
            assert not storage_service.inspirations_file.exists()
            assert not storage_service.todos_file.exists()
            
            # Save a record (this should trigger file initialization)
            record_id = storage_service.save_record(record)
            
            # records.json should now exist and contain the record
            assert storage_service.records_file.exists()
            with open(storage_service.records_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            assert len(records) >= 1
            assert any(r["record_id"] == record_id for r in records)
            
            # If mood exists, save it and verify file initialization
            if record.parsed_data.mood is not None:
                storage_service.append_mood(
                    record.parsed_data.mood,
                    record_id,
                    record.timestamp
                )
                assert storage_service.moods_file.exists()
                with open(storage_service.moods_file, 'r', encoding='utf-8') as f:
                    moods = json.load(f)
                assert isinstance(moods, list)
                assert len(moods) >= 1
            
            # If inspirations exist, save them and verify file initialization
            if record.parsed_data.inspirations:
                storage_service.append_inspirations(
                    record.parsed_data.inspirations,
                    record_id,
                    record.timestamp
                )
                assert storage_service.inspirations_file.exists()
                with open(storage_service.inspirations_file, 'r', encoding='utf-8') as f:
                    inspirations = json.load(f)
                assert isinstance(inspirations, list)
                assert len(inspirations) >= len(record.parsed_data.inspirations)
            
            # If todos exist, save them and verify file initialization
            if record.parsed_data.todos:
                storage_service.append_todos(
                    record.parsed_data.todos,
                    record_id,
                    record.timestamp
                )
                assert storage_service.todos_file.exists()
                with open(storage_service.todos_file, 'r', encoding='utf-8') as f:
                    todos = json.load(f)
                assert isinstance(todos, list)
                assert len(todos) >= len(record.parsed_data.todos)
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)

    @given(records=st.lists(record_data_strategy(), min_size=2, max_size=20))
    @settings(max_examples=100)
    def test_property_11_unique_id_generation(self, records):
        """
        Property 11: 唯一 ID 生成
        
        For any two different records, the generated record_ids should be unique (non-repeating).
        
        **Validates: Requirements 7.7**
        """
        # Create a fresh temporary directory and storage service for each example
        temp_dir = tempfile.mkdtemp()
        try:
            storage_service = StorageService(temp_dir)
            
            generated_ids = []
            
            # Save all records and collect their IDs
            for record in records:
                # Clear the record_id to force generation of a new one
                record.record_id = ""
                
                # Save record and get the generated ID
                record_id = storage_service.save_record(record)
                generated_ids.append(record_id)
            
            # Property 1: All IDs should be non-empty strings
            for record_id in generated_ids:
                assert record_id, "Generated record_id should not be empty"
                assert isinstance(record_id, str), "Generated record_id should be a string"
            
            # Property 2: All IDs should be unique (no duplicates)
            unique_ids = set(generated_ids)
            assert len(unique_ids) == len(generated_ids), \
                f"All generated IDs should be unique. Generated {len(generated_ids)} IDs but only {len(unique_ids)} are unique. Duplicates found!"
            
            # Property 3: IDs should be valid UUIDs (format check)
            import uuid
            for record_id in generated_ids:
                try:
                    # Try to parse as UUID - this will raise ValueError if invalid
                    uuid.UUID(record_id)
                except ValueError:
                    pytest.fail(f"Generated ID '{record_id}' is not a valid UUID")
            
            # Property 4: Verify all records are saved with their unique IDs
            with open(storage_service.records_file, 'r', encoding='utf-8') as f:
                saved_records = json.load(f)
            
            saved_ids = [r["record_id"] for r in saved_records]
            
            # All generated IDs should be in the saved records
            for record_id in generated_ids:
                assert record_id in saved_ids, \
                    f"Generated ID {record_id} should be found in saved records"
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
    
    @given(
        num_records=st.integers(min_value=10, max_value=50)
    )
    @settings(max_examples=50, deadline=500)
    def test_property_11_unique_id_generation_stress(self, num_records):
        """
        Property 11: 唯一 ID 生成 - Stress Test
        
        For a large number of records saved in quick succession, all generated
        record_ids should still be unique. This tests the robustness of UUID generation.
        
        **Validates: Requirements 7.7**
        """
        # Create a fresh temporary directory and storage service for each example
        temp_dir = tempfile.mkdtemp()
        try:
            storage_service = StorageService(temp_dir)
            
            generated_ids = []
            
            # Generate and save many records quickly
            for i in range(num_records):
                # Create a minimal record
                record = RecordData(
                    record_id="",  # Force generation
                    timestamp=f"2024-01-01T00:00:{i:02d}Z",
                    input_type="text",
                    original_text=f"Test record {i}",
                    parsed_data=ParsedData(mood=None, inspirations=[], todos=[])
                )
                
                record_id = storage_service.save_record(record)
                generated_ids.append(record_id)
            
            # All IDs should be unique
            unique_ids = set(generated_ids)
            assert len(unique_ids) == num_records, \
                f"Expected {num_records} unique IDs, but got {len(unique_ids)}. " \
                f"Found {num_records - len(unique_ids)} duplicates!"
            
            # Verify all are valid UUIDs
            import uuid
            for record_id in generated_ids:
                try:
                    uuid.UUID(record_id)
                except ValueError:
                    pytest.fail(f"Generated ID '{record_id}' is not a valid UUID")
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
    
    @given(record=record_data_strategy())
    @settings(max_examples=100)
    def test_property_11_unique_id_generation_preserves_existing(self, record):
        """
        Property 11: 唯一 ID 生成 - Preserve Existing IDs
        
        If a record already has a record_id set, the save_record method should
        preserve it and not generate a new one.
        
        **Validates: Requirements 7.7**
        """
        # Create a fresh temporary directory and storage service for each example
        temp_dir = tempfile.mkdtemp()
        try:
            storage_service = StorageService(temp_dir)
            
            # Use the record's existing ID
            original_id = record.record_id
            
            # Save the record
            returned_id = storage_service.save_record(record)
            
            # The returned ID should match the original
            assert returned_id == original_id, \
                "save_record should preserve existing record_id"
            
            # Verify the record is saved with the original ID
            with open(storage_service.records_file, 'r', encoding='utf-8') as f:
                saved_records = json.load(f)
            
            found_record = None
            for r in saved_records:
                if r["record_id"] == original_id:
                    found_record = r
                    break
            
            assert found_record is not None, \
                "Record should be saved with its original ID"
            assert found_record["record_id"] == original_id
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
