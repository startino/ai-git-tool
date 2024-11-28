import logging
import logging.config
import yaml
import os
from pathlib import Path


def setup_logging():
    try:
        config_path = Path(__file__).parent.parent.parent / "logging.yaml"

        if os.path.exists(config_path):
            with open(config_path, "rt") as f:
                config = yaml.safe_load(f)
                logging.config.dictConfig(config)
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                handlers=[logging.StreamHandler()],
            )
            logging.warning(
                f"Logging config file not found at {config_path}, using basic configuration"
            )
    except Exception as e:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
        logging.error(f"Error setting up logging configuration: {str(e)}")
