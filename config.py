import os
import json

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        with open('config.json', 'r') as f:
            self._config = json.load(f)
        
        for key in self._config:
            env_value = os.environ.get(key.upper())
            if env_value:
                self._config[key] = env_value

    def get(self, key, default=None):
        return self._config.get(key, default)

config = Config()
