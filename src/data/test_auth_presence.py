import os
from dotenv import load_dotenv

def safe_check():
    # 1. .env exists
    env_exists = os.path.exists('.env')
    
    # 2. MAP_KEY is loaded and non-empty
    load_dotenv()
    key = os.getenv('MAP_KEY')
    key_configured = key is not None and len(key.strip()) > 0
    
    print(f"MAP_KEY configured: {key_configured}")

if __name__ == "__main__":
    safe_check()
