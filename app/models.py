"""Data models for Voice Text Processor.

This module defines all Pydantic data models used throughout the application
for data validation, serialization, and API request/response handling.

Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 6.4
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class MoodData(BaseModel):
    """Mood data structure.
    
    Represents the emotional state extracted from user input.
    
    Attributes:
        type: The type/name of the emotion (e.g., "开心", "焦虑")
        intensity: Emotion intensity on a scale of 1-10
        keywords: List of keywords associated with the emotion
    
    Requirements: 4.1, 4.2, 4.3
    """
    type: Optional[str] = None
    intensity: Optional[int] = Field(None, ge=1, le=10)
    keywords: List[str] = Field(default_factory=list)


class InspirationData(BaseModel):
    """Inspiration data structure.
    
    Represents an idea or inspiration extracted from user input.
    
    Attributes:
        core_idea: The core idea/concept (max 20 characters)
        tags: List of tags for categorization (max 5 tags)
        category: Category of the inspiration
    
    Requirements: 5.1, 5.2, 5.3
    """
    core_idea: str = Field(..., max_length=20)
    tags: List[str] = Field(default_factory=list, max_length=5)
    category: Literal["工作", "生活", "学习", "创意"]


class TodoData(BaseModel):
    """Todo item data structure.
    
    Represents a task/todo item extracted from user input.
    
    Attributes:
        task: Description of the task
        time: Time information (preserved as original expression)
        location: Location information
        status: Task status (defaults to "pending")
    
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    task: str
    time: Optional[str] = None
    location: Optional[str] = None
    status: str = "pending"


class ParsedData(BaseModel):
    """Parsed data structure.
    
    Contains all structured data extracted from semantic parsing.
    
    Attributes:
        mood: Extracted mood data (optional)
        inspirations: List of extracted inspirations
        todos: List of extracted todo items
    """
    mood: Optional[MoodData] = None
    inspirations: List[InspirationData] = Field(default_factory=list)
    todos: List[TodoData] = Field(default_factory=list)


class RecordData(BaseModel):
    """Complete record data structure.
    
    Represents a complete user input record with all metadata and parsed data.
    
    Attributes:
        record_id: Unique identifier for the record
        timestamp: ISO 8601 timestamp of when the record was created
        input_type: Type of input (audio or text)
        original_text: The original or transcribed text
        parsed_data: Structured data extracted from the text
    """
    record_id: str
    timestamp: str
    input_type: Literal["audio", "text"]
    original_text: str
    parsed_data: ParsedData


class ProcessResponse(BaseModel):
    """API response model for /api/process endpoint.
    
    Represents the response returned to clients after processing input.
    
    Attributes:
        record_id: Unique identifier for the processed record
        timestamp: ISO 8601 timestamp of when processing completed
        mood: Extracted mood data (optional)
        inspirations: List of extracted inspirations
        todos: List of extracted todo items
        error: Error message if processing failed (optional)
    """
    record_id: str
    timestamp: str
    mood: Optional[MoodData] = None
    inspirations: List[InspirationData] = Field(default_factory=list)
    todos: List[TodoData] = Field(default_factory=list)
    error: Optional[str] = None
