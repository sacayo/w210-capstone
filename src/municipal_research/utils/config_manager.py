"""Configuration management for the municipal research system."""

import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration for the municipal research system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or os.path.join('config', 'config.json')
        self.config = self._load_default_config()
        
        # Load configuration from file if it exists
        if os.path.exists(self.config_path):
            self.load_config(self.config_path)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            'data_collection': {
                'rate_limit': 1.0,
                'max_retries': 3,
                'timeout': 30,
                'max_jurisdictions_per_state': 5,
                'max_codes_per_jurisdiction': 10
            },
            'analysis': {
                'generate_visualizations': True,
                'create_word_clouds': True,
                'calculate_readability': True,
                'max_keywords': 20
            },
            'output': {
                'data_dir': 'data',
                'visualization_dir': 'visualizations',
                'reports_dir': 'reports',
                'log_dir': 'logs'
            },
            'logging': {
                'level': 'INFO',
                'log_to_file': True,
                'log_file': 'logs/municipal_research.log'
            },
            'agents': {
                'enable_parallel_processing': False,
                'max_workers': 4
            }
        }
    
    def load_config(self, config_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
            
            # Merge with default config
            self._deep_merge(self.config, file_config)
            self.config_path = config_path
            
            logger.info(f"Configuration loaded from {config_path}")
            
        except FileNotFoundError:
            logger.warning(f"Configuration file {config_path} not found, using defaults")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file {config_path}: {e}")
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
    
    def save_config(self, config_path: Optional[str] = None) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            config_path: Path to save configuration file
        """
        save_path = config_path or self.config_path
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Configuration saved to {save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {save_path}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'data_collection.rate_limit')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        logger.info(f"Configuration updated: {key} = {value}")
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Configuration section as dictionary
        """
        return self.config.get(section, {})
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary to merge into
            update: Dictionary to merge from
        """
        for key, value in update.items():
            if (key in base and 
                isinstance(base[key], dict) and 
                isinstance(value, dict)):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def create_directories(self) -> None:
        """Create all configured directories."""
        directories = [
            self.get('output.data_dir'),
            self.get('output.visualization_dir'),
            self.get('output.reports_dir'),
            self.get('output.log_dir')
        ]
        
        for directory in directories:
            if directory:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
    
    def validate_config(self) -> bool:
        """
        Validate the configuration.
        
        Returns:
            True if configuration is valid
        """
        required_sections = ['data_collection', 'analysis', 'output', 'logging']
        
        for section in required_sections:
            if section not in self.config:
                logger.error(f"Missing required configuration section: {section}")
                return False
        
        # Validate specific settings
        rate_limit = self.get('data_collection.rate_limit')
        if not isinstance(rate_limit, (int, float)) or rate_limit < 0:
            logger.error("Invalid rate_limit configuration")
            return False
        
        return True