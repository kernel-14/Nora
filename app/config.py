"""Configuration management module for Voice Text Processor.

This module handles loading configuration from environment variables,
validating required settings, and providing configuration access throughout
the application.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Config(BaseModel):
    """Application configuration loaded from environment variables."""
    
    # API Keys
    zhipu_api_key: str = Field(
        ...,
        description="Zhipu AI API key for ASR and GLM-4-Flash services"
    )
    
    # Data storage paths
    data_dir: Path = Field(
        default=Path("data"),
        description="Directory for storing JSON data files"
    )
    
    # File size limits (in bytes)
    max_audio_size: int = Field(
        default=10 * 1024 * 1024,  # 10 MB default
        description="Maximum audio file size in bytes"
    )
    
    # Logging configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    log_file: Optional[Path] = Field(
        default=Path("logs/app.log"),
        description="Log file path"
    )
    
    # Server configuration
    host: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    
    port: int = Field(
        default=8000,
        description="Server port"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper
    
    @field_validator("max_audio_size")
    @classmethod
    def validate_max_audio_size(cls, v: int) -> int:
        """Validate max audio size is positive."""
        if v <= 0:
            raise ValueError("max_audio_size must be positive")
        return v
    
    @field_validator("data_dir", "log_file")
    @classmethod
    def convert_to_path(cls, v) -> Path:
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v
    
    class Config:
        """Pydantic configuration."""
        frozen = True  # Make config immutable


def load_config() -> Config:
    """Load configuration from environment variables.
    
    Returns:
        Config: Validated configuration object
        
    Raises:
        ValueError: If required configuration is missing or invalid
        
    Environment Variables:
        ZHIPU_API_KEY: Required. API key for Zhipu AI services
        DATA_DIR: Optional. Directory for data storage (default: data/)
        MAX_AUDIO_SIZE: Optional. Max audio file size in bytes (default: 10MB)
        LOG_LEVEL: Optional. Logging level (default: INFO)
        LOG_FILE: Optional. Log file path (default: logs/app.log)
        HOST: Optional. Server host (default: 0.0.0.0)
        PORT: Optional. Server port (default: 8000)
    """
    # Load from environment variables
    config_dict = {
        "zhipu_api_key": os.getenv("ZHIPU_API_KEY"),
        "data_dir": os.getenv("DATA_DIR", "data"),
        "max_audio_size": int(os.getenv("MAX_AUDIO_SIZE", str(10 * 1024 * 1024))),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "log_file": os.getenv("LOG_FILE", "logs/app.log"),
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8000")),
    }
    
    # Validate required fields
    if not config_dict["zhipu_api_key"]:
        raise ValueError(
            "ZHIPU_API_KEY environment variable is required. "
            "Please set it before starting the application."
        )
    
    # Create and validate config
    try:
        config = Config(**config_dict)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")
    
    # Ensure data directory exists
    config.data_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure log directory exists
    if config.log_file:
        config.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    return config


def validate_config(config: Config) -> None:
    """Validate configuration at startup.
    
    Args:
        config: Configuration object to validate
        
    Raises:
        ValueError: If configuration is invalid or required resources are unavailable
    """
    # Check data directory is writable
    if not os.access(config.data_dir, os.W_OK):
        raise ValueError(
            f"Data directory {config.data_dir} is not writable. "
            "Please check permissions."
        )
    
    # Check log directory is writable
    if config.log_file and not os.access(config.log_file.parent, os.W_OK):
        raise ValueError(
            f"Log directory {config.log_file.parent} is not writable. "
            "Please check permissions."
        )
    
    # Validate API key format (basic check)
    if len(config.zhipu_api_key) < 10:
        raise ValueError(
            "ZHIPU_API_KEY appears to be invalid (too short). "
            "Please check your API key."
        )


# Global config instance (loaded on import)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance.
    
    Returns:
        Config: The application configuration
        
    Raises:
        RuntimeError: If configuration has not been initialized
    """
    global _config
    if _config is None:
        raise RuntimeError(
            "Configuration not initialized. Call init_config() first."
        )
    return _config


def init_config() -> Config:
    """Initialize the global configuration.
    
    This should be called once at application startup.
    
    Returns:
        Config: The initialized configuration
        
    Raises:
        ValueError: If configuration is invalid
    """
    global _config
    _config = load_config()
    validate_config(_config)
    return _config
