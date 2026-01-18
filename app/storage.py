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
        """Ensure a JSON file exists and is initialized with default data.
        
        If the file doesn't exist, creates it with sample Chinese data.
        
        Args:
            file_path: Path to the JSON file
            
        Raises:
            StorageError: If file creation fails
            
        Requirements: 7.5
        """
        if not file_path.exists():
            try:
                # 根据文件类型提供不同的默认数据
                default_data = []
                
                if file_path.name == 'records.json':
                    default_data = self._get_default_records()
                elif file_path.name == 'moods.json':
                    default_data = self._get_default_moods()
                elif file_path.name == 'inspirations.json':
                    default_data = self._get_default_inspirations()
                elif file_path.name == 'todos.json':
                    default_data = self._get_default_todos()
                elif file_path.name == 'user_config.json':
                    default_data = self._get_default_user_config()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                raise StorageError(
                    f"Failed to initialize file {file_path}: {str(e)}"
                )
    
    def _get_default_records(self) -> list:
        """获取默认的记录数据"""
        from datetime import datetime, timedelta
        now = datetime.now()
        
        return [
            {
                "record_id": "welcome-1",
                "timestamp": (now - timedelta(hours=2)).isoformat() + "Z",
                "input_type": "text",
                "original_text": "今天天气真好，阳光洒在窗台上，心情也跟着明朗起来。决定下午去公园散散步，感受一下大自然的美好。",
                "parsed_data": {
                    "mood": {
                        "type": "喜悦",
                        "intensity": 8,
                        "keywords": ["阳光", "明朗", "美好"]
                    },
                    "inspirations": [
                        {
                            "core_idea": "享受自然的美好时光",
                            "tags": ["自然", "散步", "放松"],
                            "category": "生活"
                        }
                    ],
                    "todos": [
                        {
                            "task": "去公园散步",
                            "time": "下午",
                            "location": "公园",
                            "status": "pending"
                        }
                    ]
                }
            },
            {
                "record_id": "welcome-2",
                "timestamp": (now - timedelta(hours=5)).isoformat() + "Z",
                "input_type": "text",
                "original_text": "刚看完一本很棒的书，书中的一句话让我印象深刻：'生活不是等待暴风雨过去，而是学会在雨中跳舞。'这句话给了我很多启发。",
                "parsed_data": {
                    "mood": {
                        "type": "平静",
                        "intensity": 7,
                        "keywords": ["启发", "思考", "感悟"]
                    },
                    "inspirations": [
                        {
                            "core_idea": "学会在困难中保持积极",
                            "tags": ["人生哲理", "积极心态", "成长"],
                            "category": "学习"
                        }
                    ],
                    "todos": []
                }
            },
            {
                "record_id": "welcome-3",
                "timestamp": (now - timedelta(days=1, hours=3)).isoformat() + "Z",
                "input_type": "text",
                "original_text": "和好朋友聊了很久，她分享了最近的生活和工作。虽然大家都很忙，但能抽时间见面真的很珍贵。友谊需要用心维护。",
                "parsed_data": {
                    "mood": {
                        "type": "温暖",
                        "intensity": 9,
                        "keywords": ["友谊", "珍贵", "陪伴"]
                    },
                    "inspirations": [
                        {
                            "core_idea": "珍惜身边的朋友",
                            "tags": ["友情", "陪伴", "珍惜"],
                            "category": "生活"
                        }
                    ],
                    "todos": [
                        {
                            "task": "定期和朋友联系",
                            "time": None,
                            "location": None,
                            "status": "pending"
                        }
                    ]
                }
            },
            {
                "record_id": "welcome-4",
                "timestamp": (now - timedelta(days=2)).isoformat() + "Z",
                "input_type": "text",
                "original_text": "今天完成了一个困扰我很久的项目，虽然过程很辛苦，但看到成果的那一刻，所有的付出都值得了。成就感满满！",
                "parsed_data": {
                    "mood": {
                        "type": "兴奋",
                        "intensity": 10,
                        "keywords": ["成就感", "完成", "满足"]
                    },
                    "inspirations": [],
                    "todos": []
                }
            },
            {
                "record_id": "welcome-5",
                "timestamp": (now - timedelta(days=3)).isoformat() + "Z",
                "input_type": "text",
                "original_text": "最近工作压力有点大，总是担心做不好。但转念一想，每个人都会遇到困难，重要的是保持积极的心态，一步一步来。",
                "parsed_data": {
                    "mood": {
                        "type": "焦虑",
                        "intensity": 6,
                        "keywords": ["压力", "担心", "积极"]
                    },
                    "inspirations": [
                        {
                            "core_idea": "保持积极心态面对压力",
                            "tags": ["心态", "压力管理", "成长"],
                            "category": "工作"
                        }
                    ],
                    "todos": []
                }
            }
        ]
    
    def _get_default_moods(self) -> list:
        """获取默认的心情数据"""
        from datetime import datetime, timedelta
        now = datetime.now()
        
        return [
            {
                "record_id": "welcome-1",
                "timestamp": (now - timedelta(hours=2)).isoformat() + "Z",
                "type": "喜悦",
                "intensity": 8,
                "keywords": ["阳光", "明朗", "美好"]
            },
            {
                "record_id": "welcome-2",
                "timestamp": (now - timedelta(hours=5)).isoformat() + "Z",
                "type": "平静",
                "intensity": 7,
                "keywords": ["启发", "思考", "感悟"]
            },
            {
                "record_id": "welcome-3",
                "timestamp": (now - timedelta(days=1, hours=3)).isoformat() + "Z",
                "type": "温暖",
                "intensity": 9,
                "keywords": ["友谊", "珍贵", "陪伴"]
            },
            {
                "record_id": "welcome-4",
                "timestamp": (now - timedelta(days=2)).isoformat() + "Z",
                "type": "兴奋",
                "intensity": 10,
                "keywords": ["成就感", "完成", "满足"]
            },
            {
                "record_id": "welcome-5",
                "timestamp": (now - timedelta(days=3)).isoformat() + "Z",
                "type": "焦虑",
                "intensity": 6,
                "keywords": ["压力", "担心", "积极"]
            }
        ]
    
    def _get_default_inspirations(self) -> list:
        """获取默认的灵感数据"""
        from datetime import datetime, timedelta
        now = datetime.now()
        
        return [
            {
                "record_id": "welcome-1",
                "timestamp": (now - timedelta(hours=2)).isoformat() + "Z",
                "core_idea": "享受自然的美好时光",
                "tags": ["自然", "散步", "放松"],
                "category": "生活"
            },
            {
                "record_id": "welcome-2",
                "timestamp": (now - timedelta(hours=5)).isoformat() + "Z",
                "core_idea": "学会在困难中保持积极",
                "tags": ["人生哲理", "积极心态", "成长"],
                "category": "学习"
            },
            {
                "record_id": "welcome-3",
                "timestamp": (now - timedelta(days=1, hours=3)).isoformat() + "Z",
                "core_idea": "珍惜身边的朋友",
                "tags": ["友情", "陪伴", "珍惜"],
                "category": "生活"
            },
            {
                "record_id": "welcome-5",
                "timestamp": (now - timedelta(days=3)).isoformat() + "Z",
                "core_idea": "保持积极心态面对压力",
                "tags": ["心态", "压力管理", "成长"],
                "category": "工作"
            }
        ]
    
    def _get_default_todos(self) -> list:
        """获取默认的待办数据"""
        from datetime import datetime, timedelta
        now = datetime.now()
        
        return [
            {
                "record_id": "welcome-1",
                "timestamp": (now - timedelta(hours=2)).isoformat() + "Z",
                "task": "去公园散步",
                "time": "下午",
                "location": "公园",
                "status": "pending"
            },
            {
                "record_id": "welcome-3",
                "timestamp": (now - timedelta(days=1, hours=3)).isoformat() + "Z",
                "task": "定期和朋友联系",
                "time": None,
                "location": None,
                "status": "pending"
            }
        ]
    
    def _get_default_user_config(self) -> dict:
        """获取默认的用户配置"""
        return {
            "character": {
                "image_url": "",  # 空字符串，前端会显示占位符
                "prompt": "默认形象：薰衣草紫色温柔猫咪",
                "preferences": {
                    "color": "薰衣草紫",
                    "personality": "温柔",
                    "appearance": "无配饰",
                    "role": "陪伴式朋友"
                }
            }
        }
    
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
