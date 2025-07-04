"""
Configuration management for mesh generation parameters.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Try to import yaml for YAML support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigManager:
    """Manages loading and saving of configuration files."""
    
    @staticmethod
    def load_config(config_file):
        """Load parameters from JSON or YAML configuration file."""
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        # Determine file type
        if config_file.lower().endswith(('.yml', '.yaml')):
            if not YAML_AVAILABLE:
                raise ImportError("PyYAML not installed. Install with: pip install PyYAML")
            return ConfigManager._load_yaml(config_file)
        else:
            return ConfigManager._load_json(config_file)
    
    @staticmethod
    def _load_yaml(config_file):
        """Load YAML configuration file."""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def _load_json(config_file):
        """Load JSON configuration file."""
        with open(config_file, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def save_config(args, config_file):
        """Save current parameters to JSON or YAML configuration file."""
        config = {
            'ml': args.ml,
            'radius': args.radius,
            'layers': args.layers,
            'subdivisions': args.subdivisions,
            'layer_names': getattr(args, 'layer_names', None)
        }
        
        # Ensure directory exists
        Path(config_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Determine file type
        if config_file.lower().endswith(('.yml', '.yaml')):
            if not YAML_AVAILABLE:
                raise ImportError("PyYAML not installed. Install with: pip install PyYAML")
            ConfigManager._save_yaml(config, config_file)
        else:
            ConfigManager._save_json(config, config_file)
    
    @staticmethod
    def _save_yaml(config_dict: Dict[str, Any], config_file: str):
        """Save configuration as YAML."""
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    @staticmethod
    def _save_json(config_dict: Dict[str, Any], config_file: str):
        """Save configuration as JSON."""
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @staticmethod
    def apply_config_to_args(args, parser, config):
        """Apply configuration values to arguments, preserving command line overrides."""
        for key, value in config.items():
            if hasattr(args, key):
                # Apply config values if the argument wasn't provided via CLI
                if key == 'layers' and (not args.layers or args.layers is None):
                    setattr(args, key, value)
                elif key in ['ml', 'radius'] and getattr(args, key) is None:
                    setattr(args, key, value)
                elif key not in ['layers', 'ml', 'radius'] and hasattr(parser, 'get_default') and getattr(args, key) == parser.get_default(key):
                    setattr(args, key, value)
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration and return validation results.
        
        Returns:
            Dictionary with 'valid', 'errors', and 'warnings' keys
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Required fields
        required_fields = ['ml', 'radius', 'layers']
        for field in required_fields:
            if field not in config:
                result['errors'].append(f"Missing required field: {field}")
                result['valid'] = False
        
        if not result['valid']:
            return result
        
        # Type validation
        if not isinstance(config['ml'], (int, float)) or config['ml'] <= 0:
            result['errors'].append("'ml' must be a positive number")
            result['valid'] = False
        
        if not isinstance(config['radius'], (int, float)) or config['radius'] <= 0:
            result['errors'].append("'radius' must be a positive number")
            result['valid'] = False
        
        if not isinstance(config['layers'], list) or not config['layers']:
            result['errors'].append("'layers' must be a non-empty list")
            result['valid'] = False
        elif any(not isinstance(l, (int, float)) or l <= 0 for l in config['layers']):
            result['errors'].append("All layer thicknesses must be positive numbers")
            result['valid'] = False
        
        # Optional field validation
        if 'subdivisions' in config:
            subdivisions = config['subdivisions']
            if not isinstance(subdivisions, list):
                result['errors'].append("'subdivisions' must be a list")
                result['valid'] = False
            elif len(subdivisions) != len(config['layers']):
                result['errors'].append("'subdivisions' length must match 'layers' length")
                result['valid'] = False
        
        if 'layer_names' in config:
            layer_names = config['layer_names']
            if not isinstance(layer_names, list):
                result['errors'].append("'layer_names' must be a list")
                result['valid'] = False
            elif len(layer_names) != len(config['layers']):
                result['errors'].append("'layer_names' length must match 'layers' length")
                result['valid'] = False
        
        return result
