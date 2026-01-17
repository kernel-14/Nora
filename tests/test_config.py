"""Tests for configuration management module.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from app.config import Config, load_config, validate_config, init_config


class TestConfig:
    """Test configuration loading and validation."""
    
    def test_config_with_all_fields(self):
        """Test creating config with all fields specified."""
        config = Config(
            zhipu_api_key="test_api_key_1234567890",
            data_dir=Path("test_data"),
            max_audio_size=5 * 1024 * 1024,
            log_level="DEBUG",
            log_file=Path("test_logs/test.log"),
            host="127.0.0.1",
            port=9000
        )
        
        assert config.zhipu_api_key == "test_api_key_1234567890"
        assert config.data_dir == Path("test_data")
        assert config.max_audio_size == 5 * 1024 * 1024
        assert config.log_level == "DEBUG"
        assert config.log_file == Path("test_logs/test.log")
        assert config.host == "127.0.0.1"
        assert config.port == 9000
    
    def test_config_with_defaults(self):
        """Test creating config with default values."""
        config = Config(zhipu_api_key="test_api_key_1234567890")
        
        assert config.zhipu_api_key == "test_api_key_1234567890"
        assert config.data_dir == Path("data")
        assert config.max_audio_size == 10 * 1024 * 1024
        assert config.log_level == "INFO"
        assert config.log_file == Path("logs/app.log")
        assert config.host == "0.0.0.0"
        assert config.port == 8000
    
    def test_config_missing_api_key(self):
        """Test that missing API key raises validation error."""
        with pytest.raises(Exception):  # Pydantic will raise validation error
            Config()
    
    def test_config_invalid_log_level(self):
        """Test that invalid log level raises validation error."""
        with pytest.raises(ValueError, match="log_level must be one of"):
            Config(
                zhipu_api_key="test_api_key_1234567890",
                log_level="INVALID"
            )
    
    def test_config_invalid_max_audio_size(self):
        """Test that invalid max audio size raises validation error."""
        with pytest.raises(ValueError, match="max_audio_size must be positive"):
            Config(
                zhipu_api_key="test_api_key_1234567890",
                max_audio_size=-1
            )
    
    def test_config_log_level_case_insensitive(self):
        """Test that log level is case insensitive."""
        config = Config(
            zhipu_api_key="test_api_key_1234567890",
            log_level="debug"
        )
        assert config.log_level == "DEBUG"
    
    def test_config_immutable(self):
        """Test that config is immutable (frozen)."""
        config = Config(zhipu_api_key="test_api_key_1234567890")
        
        with pytest.raises(Exception):  # Pydantic frozen model raises error
            config.zhipu_api_key = "new_key"


class TestLoadConfig:
    """Test loading configuration from environment variables."""
    
    @patch.dict(os.environ, {
        "ZHIPU_API_KEY": "test_key_1234567890",
        "DATA_DIR": "custom_data",
        "MAX_AUDIO_SIZE": "5242880",
        "LOG_LEVEL": "DEBUG",
        "LOG_FILE": "custom_logs/app.log",
        "HOST": "127.0.0.1",
        "PORT": "9000"
    })
    def test_load_config_from_env(self, tmp_path):
        """Test loading config from environment variables."""
        # Create temporary directories
        data_dir = tmp_path / "custom_data"
        data_dir.mkdir()
        log_dir = tmp_path / "custom_logs"
        log_dir.mkdir()
        
        with patch.dict(os.environ, {
            "DATA_DIR": str(data_dir),
            "LOG_FILE": str(log_dir / "app.log")
        }, clear=False):
            config = load_config()
        
        assert config.zhipu_api_key == "test_key_1234567890"
        assert config.data_dir == data_dir
        assert config.max_audio_size == 5242880
        assert config.log_level == "DEBUG"
        assert config.log_file == log_dir / "app.log"
        assert config.host == "127.0.0.1"
        assert config.port == 9000
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    def test_load_config_with_defaults(self, tmp_path):
        """Test loading config with default values."""
        # Use tmp_path for data directory
        with patch.dict(os.environ, {"DATA_DIR": str(tmp_path / "data")}, clear=False):
            config = load_config()
        
        assert config.zhipu_api_key == "test_key_1234567890"
        assert config.log_level == "INFO"
        assert config.host == "0.0.0.0"
        assert config.port == 8000
    
    @patch.dict(os.environ, {}, clear=True)
    def test_load_config_missing_api_key(self):
        """Test that missing API key raises ValueError.
        
        Requirement 10.4: Missing required config should cause startup failure.
        """
        with pytest.raises(ValueError, match="ZHIPU_API_KEY environment variable is required"):
            load_config()
    
    @patch.dict(os.environ, {
        "ZHIPU_API_KEY": "test_key_1234567890",
        "MAX_AUDIO_SIZE": "invalid"
    }, clear=True)
    def test_load_config_invalid_integer(self):
        """Test that invalid integer value raises ValueError."""
        with pytest.raises(ValueError):
            load_config()


class TestValidateConfig:
    """Test configuration validation at startup."""
    
    def test_validate_config_success(self, tmp_path):
        """Test successful config validation."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        
        config = Config(
            zhipu_api_key="test_key_1234567890",
            data_dir=data_dir,
            log_file=log_dir / "app.log"
        )
        
        # Should not raise any exception
        validate_config(config)
    
    def test_validate_config_data_dir_not_writable(self, tmp_path):
        """Test validation fails if data directory is not writable.
        
        Note: This test is skipped on Windows as chmod doesn't work the same way.
        """
        import platform
        if platform.system() == "Windows":
            pytest.skip("chmod doesn't work reliably on Windows")
        
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Make directory read-only
        data_dir.chmod(0o444)
        
        config = Config(
            zhipu_api_key="test_key_1234567890",
            data_dir=data_dir
        )
        
        try:
            with pytest.raises(ValueError, match="not writable"):
                validate_config(config)
        finally:
            # Restore permissions for cleanup
            data_dir.chmod(0o755)
    
    def test_validate_config_short_api_key(self, tmp_path):
        """Test validation fails if API key is too short."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        config = Config(
            zhipu_api_key="short",
            data_dir=data_dir
        )
        
        with pytest.raises(ValueError, match="ZHIPU_API_KEY appears to be invalid"):
            validate_config(config)


class TestInitConfig:
    """Test global config initialization."""
    
    @patch.dict(os.environ, {"ZHIPU_API_KEY": "test_key_1234567890"}, clear=True)
    def test_init_config(self, tmp_path):
        """Test initializing global config."""
        from app.config import _config, get_config
        
        # Reset global config
        import app.config
        app.config._config = None
        
        with patch.dict(os.environ, {"DATA_DIR": str(tmp_path / "data")}, clear=False):
            config = init_config()
        
        assert config is not None
        assert config.zhipu_api_key == "test_key_1234567890"
        
        # Should be able to get config
        assert get_config() == config
