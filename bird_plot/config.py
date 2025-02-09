import logging
from pathlib import Path
from typing import Dict

import tomli

logger = logging.getLogger(__name__)


def load_config(config_path: Path = Path("config.toml")) -> Dict:
    """Load configuration from TOML file."""
    try:
        with open(config_path, "rb") as f:
            return tomli.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise
