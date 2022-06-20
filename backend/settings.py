import pathlib
import yaml
import os

BASE_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

config_file = os.environ.get("CONFIG_FILE", "develop.yaml")
config_path = BASE_DIR / 'config' / config_file


def get_config(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    return config


config = get_config(config_path)
