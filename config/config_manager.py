import os
import toml
from dotenv import load_dotenv
import logging

class ConfigManager:
    def __init__(self, config_path="./config.toml"):
        load_dotenv()
        self.config_path = config_path
        self.lat = None
        self.lng = None
        self.load_config()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename='accident_detection.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_config(self):
        try:
            config = toml.load(self.config_path)
            self.lat = config.get('location', {}).get('lat')
            self.lng = config.get('location', {}).get('lng')
            if self.lat is None or self.lng is None:
                raise KeyError("Latitude or longitude not found in config.toml")
        except Exception as e:
            logging.error(f"Error loading config.toml: {str(e)}")
            self.lat, self.lng =  #Enter your coordinates here e.g. (12.9716, 77.5946) or (40.7128, -74.0060) (0, 0)  # Default to (0, 0) if error occurs

    def get_coordinates(self):
        return self.lat, self.lng
    
    if not os.getenv('GEMINI_API_KEY'):
        raise ValueError("Missing GEMINI_API_KEY in .env")

    @staticmethod
    def get_env_var(var_name):
        return os.getenv(var_name)