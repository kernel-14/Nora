"""Storage service for JSON file persistence.

This module implements the StorageService class for managing JSON file storage
of records, moods, inspirations, and todos.

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
"""

import json
import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from app.models import RecordData, MoodData, InspirationData, TodoData


class StorageError(Exception):
    """Exception raised when storage operations fail.
    
    This exception is raised when file operations (read/write) fail,
    such as due to permission issues, disk space, or I/O errors.
    
    Requirements: 7.6
    """
    pass


class StorageService:
    """Service for managing JSON file storage.
    
    This service handles persistence of records, moods, inspirations, and todos
    to separate JSON files. It ensures file initialization, generates unique IDs,
    and handles errors appropriately.
    
    Attributes:
        data_dir: Directory path for storing JSON files
        records_file: Path to records.json
        moods_file: Path to moods.json
        inspirations_file: Path to inspirations.json
        todos_file: Path to todos.json
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
    """
    
    def __init__(self, data_dir: str):
        """Initialize the storage service.
        
        Args:
            data_dir: Directory path for storing JSON files
        """
        self.data_dir = Path(data_dir)
        self.records_file = self.data_dir / "records.json"
        self.moods_file = self.data_dir / "moods.json"
        self.inspirations_file = self.data_dir / "inspirations.json"
        self.todos_file = self.data_dir / "todos.json"
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _ensure_file_exists(self, file_path: Path) -> None:
        """Ensure a JSON file exists and is initialized as an empty array.
        
        If the file doesn't exist, creates it with an empty array [].
        
        Args:
            file_path: Path to the JSON file
            
        Raises:
            StorageError: If file creation fails
            
        Requirements: 7.5
        """
        if not file_path.exists():
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            except Exception as e:
                raise StorageError(
                    f"Failed to initialize file {file_path}: {str(e)}"
                )
    
    def _read_json_file(self, file_path: Path) -> List:
        """Read and parse a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of records from the JSON file
            
        Raises:
            StorageError: If file reading or parsing fails
        """
        self._ensure_file_exists(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(
                f"Failed to read file {file_path}: {str(e)}"
            )
    
    def _write_json_file(self, file_path: Path, data: List) -> None:
        """Write data to a JSON file.
        
        Args:
            file_path: Path to the JSON file
            data: List of records to write
            
        Raises:
            StorageError: If file writing fails
            
        Requirements: 7.6
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise StorageError(
                f"Failed to write file {file_path}: {str(e)}"
            )
    
    def save_record(self, record: RecordData) -> str:
        """Save a complete record to records.json.
        
        Generates a unique UUID for the record if not already set,
        and appends the record to the records.json file.
        
        Args:
            record: RecordData object to save
            
        Returns:
            The unique record_id (UUID string)
            
        Raises:
            StorageError: If file writing fails
            
        Requirements: 7.1, 7.7
        """
        # Generate unique UUID if not set
        if not record.record_id:
            record.record_id = str(uuid.uuid4())
        
        # Read existing records
        records = self._read_json_file(self.records_file)
        
        # Append new record
        records.append(record.model_dump())
        
        # Write back to file
        self._write_json_file(self.records_file, records)
        
        return record.record_id
    
    def append_mood(self, mood: MoodData, record_id: str, timestamp: str) -> None:
        """Append mood data to moods.json.
        
        Args:
            mood: MoodData object to append
            record_id: Associated record ID
            timestamp: ISO 8601 timestamp
            
        Raises:
            StorageError: If file writing fails
            
        Requirements: 7.2
        """
        # Read existing moods
        moods = self._read_json_file(self.moods_file)
        
        # Create mood entry with metadata
        mood_entry = {
            "record_id": record_id,
            "timestamp": timestamp,
            **mood.model_dump()
        }
        
        # Append new mood
        moods.append(mood_entry)
        
        # Write back to file
        self._write_json_file(self.moods_file, moods)
    
    def append_inspirations(
        self, 
        inspirations: List[InspirationData], 
        record_id: str, 
        timestamp: str
    ) -> None:
        """Append inspiration data to inspirations.json.
        
        Args:
            inspirations: List of InspirationData objects to append
            record_id: Associated record ID
            timestamp: ISO 8601 timestamp
            
        Raises:
            StorageError: If file writing fails
            
        Requirements: 7.3
        """
        if not inspirations:
            return
        
        # Read existing inspirations
        all_inspirations = self._read_json_file(self.inspirations_file)
        
        # Create inspiration entries with metadata
        for inspiration in inspirations:
            inspiration_entry = {
                "record_id": record_id,
                "timestamp": timestamp,
                **inspiration.model_dump()
            }
            all_inspirations.append(inspiration_entry)
        
        # Write back to file
        self._write_json_file(self.inspirations_file, all_inspirations)
    
    def append_todos(
        self, 
        todos: List[TodoData], 
        record_id: str, 
        timestamp: str
    ) -> None:
        """Append todo data to todos.json.
        
        Args:
            todos: List of TodoData objects to append
            record_id: Associated record ID
            timestamp: ISO 8601 timestamp
            
        Raises:
            StorageError: If file writing fails
            
        Requirements: 7.4
        """
        if not todos:
            return
        
        # Read existing todos
        all_todos = self._read_json_file(self.todos_file)
        
        # Create todo entries with metadata
        for todo in todos:
            todo_entry = {
                "record_id": record_id,
                "timestamp": timestamp,
                **todo.model_dump()
            }
            all_todos.append(todo_entry)
        
        # Write back to file
        self._write_json_file(self.todos_file, all_todos)
