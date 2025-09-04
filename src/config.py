import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for RBC Direct Investing automation."""
    
    def __init__(self):
        self.username = os.getenv('RBC_USERNAME')
        self.password = os.getenv('RBC_PASSWORD')
        
        self.base_url = 'https://secure.royalbank.com'
        self.login_url = 'https://secure.royalbank.com/statics/login-service-ui/index#/full/signin?LANGUAGE=ENGLISH'
        
        self.download_path = Path(__file__).parent.parent / 'downloads'
        self.download_path.mkdir(exist_ok=True)
        
        self.browser_config = {
            'headless': os.getenv('HEADLESS', 'False').lower() == 'true',
            'timeout': int(os.getenv('TIMEOUT', '30000')),
            'viewport': {'width': 2560, 'height': 1664}
        }
        
        self.export_formats = ['csv', 'pdf', 'excel']
        
    def validate(self):
        """Validate that required configuration is present."""
        if not self.username or not self.password:
            raise ValueError("RBC_USERNAME and RBC_PASSWORD must be set in environment variables")
        
        return True

config = Config()