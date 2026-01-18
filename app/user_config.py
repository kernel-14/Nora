"""User configuration management for Voice Text Processor.

This module handles user-specific configurations, including
the generated cat character image settings.

Requirements: PRD - AI形象生成模块
"""

import json
import os
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserConfig:
    """User configuration manager.
    
    This class manages user-specific settings, particularly
    the generated cat character image configuration.
    
    Attributes:
        config_dir: Directory for storing user configurations
        config_file: Path to the user config JSON file
    """
    
    def __init__(self, config_dir: str = "data"):
        """Initialize user configuration manager.
        
        Args:
            config_dir: Directory for storing configurations
        """
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "user_config.json")
        
        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        
        # 初始化配置文件
        if not os.path.exists(self.config_file):
            self._init_config_file()
    
    def _init_config_file(self):
        """Initialize the configuration file with default values."""
        default_config = {
            "user_id": "default_user",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "character": {
                "image_url": "",  # 空字符串，前端会显示占位符
                "prompt": "默认治愈系小猫形象",
                "revised_prompt": "一只薰衣草紫色的温柔猫咪，治愈系风格，温暖的陪伴者",
                "preferences": {
                    "color": "薰衣草紫",
                    "personality": "温柔",
                    "appearance": "无配饰",
                    "role": "陪伴式朋友"
                },
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "generation_count": 0
            },
            "settings": {
                "theme": "light",
                "language": "zh-CN"
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Initialized user config file: {self.config_file}")
    
    def load_config(self) -> Dict:
        """Load user configuration from file.
        
        Returns:
            Dictionary containing user configuration
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"Failed to load user config: {str(e)}")
            # 返回默认配置
            self._init_config_file()
            return self.load_config()
    
    def save_config(self, config: Dict):
        """Save user configuration to file.
        
        Args:
            config: Configuration dictionary to save
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info("User config saved successfully")
        except Exception as e:
            logger.error(f"Failed to save user config: {str(e)}")
            raise
    
    def get_character_config(self) -> Dict:
        """Get character configuration.
        
        Returns:
            Dictionary containing character settings
        """
        config = self.load_config()
        return config.get("character", {})
    
    def save_character_image(
        self,
        image_url: str,
        prompt: str,
        revised_prompt: Optional[str] = None,
        preferences: Optional[Dict] = None
    ):
        """Save generated character image configuration.
        
        Args:
            image_url: URL of the generated image
            prompt: Prompt used for generation
            revised_prompt: AI-revised prompt (optional)
            preferences: User preferences used (optional)
        """
        config = self.load_config()
        
        # 更新角色配置
        config["character"]["image_url"] = image_url
        config["character"]["prompt"] = prompt
        config["character"]["revised_prompt"] = revised_prompt or prompt
        config["character"]["generated_at"] = datetime.utcnow().isoformat() + "Z"
        config["character"]["generation_count"] += 1
        
        if preferences:
            config["character"]["preferences"] = preferences
        
        self.save_config(config)
        logger.info(f"Character image saved: {image_url[:50]}...")
    
    def get_character_image_url(self) -> Optional[str]:
        """Get the current character image URL.
        
        Returns:
            Image URL or None if not set
        """
        character = self.get_character_config()
        return character.get("image_url")
    
    def get_character_preferences(self) -> Dict:
        """Get character generation preferences.
        
        Returns:
            Dictionary containing color, personality, appearance, role
        """
        character = self.get_character_config()
        return character.get("preferences", {
            "color": "温暖粉",
            "personality": "温柔",
            "appearance": "无配饰",
            "role": "陪伴式朋友"
        })
    
    def update_character_preferences(
        self,
        color: Optional[str] = None,
        personality: Optional[str] = None,
        appearance: Optional[str] = None,
        role: Optional[str] = None
    ):
        """Update character generation preferences.
        
        Args:
            color: Color preference (optional)
            personality: Personality trait (optional)
            appearance: Appearance feature (optional)
            role: Character role (optional)
        """
        config = self.load_config()
        preferences = config["character"]["preferences"]
        
        if color:
            preferences["color"] = color
        if personality:
            preferences["personality"] = personality
        if appearance:
            preferences["appearance"] = appearance
        if role:
            preferences["role"] = role
        
        self.save_config(config)
        logger.info("Character preferences updated")
    
    def get_generation_count(self) -> int:
        """Get the number of times character has been generated.
        
        Returns:
            Generation count
        """
        character = self.get_character_config()
        return character.get("generation_count", 0)
    
    def has_character_image(self) -> bool:
        """Check if user has a character image set.
        
        Returns:
            True if character image exists, False otherwise
        """
        return self.get_character_image_url() is not None
