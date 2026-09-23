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
            filename="accident_detection.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def load_config(self):
        try:
            config = toml.load(self.config_path)

            self.lat = config.get("location", {}).get("lat")
            self.lng = config.get("location", {}).get("lng")

            if self.lat is None or self.lng is None:
                raise KeyError(
                    "Latitude or longitude not found in config.toml"
                )

        except Exception as e:
            logging.error(
                f"Error loading config.toml: {str(e)}"
            )

            # Default coordinates
            # Replace these with your desired coordinates.
            self.lat = 28.6139
            self.lng = 77.2090

    def get_coordinates(self):
        return self.lat, self.lng

    @staticmethod
    def get_env_var(var_name):
        value = os.getenv(var_name)

        if not value:
            raise ValueError(
                f"Missing required environment variable: {var_name}"
            )

        return value
