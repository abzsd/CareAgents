"""
Agent configuration loader
"""
import yaml
from pathlib import Path
from typing import Dict, Any


def load_prompts() -> Dict[str, Any]:
    """Load prompts from YAML configuration file"""
    config_path = Path(__file__).parent / "prompts.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """Get configuration for a specific agent"""
    prompts = load_prompts()
    return prompts.get(agent_name, {})


def get_system_prompt(agent_name: str) -> str:
    """Get system prompt for an agent"""
    config = get_agent_config(agent_name)
    return config.get('system_prompt', '')


def get_general_config() -> Dict[str, Any]:
    """Get general configuration"""
    prompts = load_prompts()
    return prompts.get('general', {})
