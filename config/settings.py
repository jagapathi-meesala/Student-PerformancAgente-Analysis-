import os

class Settings:
    """Agent runtime configuration settings."""
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")

settings = Settings()
