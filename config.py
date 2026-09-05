import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # ScaleKit Configuration
    SCALEKIT_ENVIRONMENT_URL: str = os.environ.get("SCALEKIT_ENVIRONMENT_URL", "")
    SCALEKIT_CLIENT_ID: str = os.environ.get("SCALEKIT_CLIENT_ID", "")
    SCALEKIT_CLIENT_SECRET: str = os.environ.get("SCALEKIT_CLIENT_SECRET", "")
    SCALEKIT_RESOURCE_METADATA_URL: str = os.environ.get("SCALEKIT_RESOURCE_METADATA_URL", "")
    SCALEKIT_AUDIENCE_NAME: str = os.environ.get("SCALEKIT_AUDIENCE_NAME", "")
    METADATA_JSON_RESPONSE: str = os.environ.get("METADATA_JSON_RESPONSE", "")

    # Document Server API Key
    DOCUMENTS_API_KEY: str = os.environ.get("DOCUMENTS_API_KEY", "")

    # Server Port
    PORT: int = int(os.environ.get("PORT", 10000))

    def __init__(self):
        required = {
            "SCALEKIT_CLIENT_ID": self.SCALEKIT_CLIENT_ID,
            "SCALEKIT_CLIENT_SECRET": self.SCALEKIT_CLIENT_SECRET,
            "SCALEKIT_ENVIRONMENT_URL": self.SCALEKIT_ENVIRONMENT_URL,
            "SCALEKIT_RESOURCE_METADATA_URL": self.SCALEKIT_RESOURCE_METADATA_URL,
            "SCALEKIT_AUDIENCE_NAME": self.SCALEKIT_AUDIENCE_NAME,
            "DOCUMENTS_API_KEY": self.DOCUMENTS_API_KEY,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

settings = Settings()