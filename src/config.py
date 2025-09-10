import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for RBC Portfolio Management system."""
    
    def __init__(self):
        # MCP automation configuration
        self.mcp_config = {
            'base_url': 'https://www1.royalbank.com/cgi-bin/rbaccess/rbunxcgi?F22=4WN600S&7ASERVER=N601LD&LANGUAGE=ENGLISH&7ASCRIPT=/WebUI/Holdings/HoldingsHome#/currency',
            'home_url': 'https://www1.royalbank.com/sgw3/secureapp/N600/ReactUI/?LANGUAGE=ENGLISH#/Home',
            'export_button_ref': 's2e232'
        }
        
        # Data directories
        self.data_input_dir = Path(__file__).parent.parent / 'data' / 'input' / 'downloaded_files'
        self.data_output_dir = Path(__file__).parent.parent / 'data' / 'output'
        
        # Ensure directories exist
        self.data_input_dir.mkdir(parents=True, exist_ok=True)
        self.data_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Benefits configuration (optional)
        self.benefits_username = os.getenv('BENEFITS_USERNAME')
        self.benefits_password = os.getenv('BENEFITS_PASSWORD')
        
    def validate(self):
        """Validate that required configuration is present."""
        # MCP automation doesn't require credentials in config
        # Benefits are optional
        return True

config = Config()