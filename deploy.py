import os
import json
import subprocess
from pathlib import Path
from getpass import getpass
import requests
from datetime import datetime

class HuggingFaceDeployer:
    def __init__(self):
        self.config_dir = Path.home() / '.huggingface'
        self.config_file = self.config_dir / 'config.json'
        self.space_name = "sp103107/canna_calc"
        self.api_url = f"https://huggingface.co/spaces/{self.space_name}"
        self.token = self._get_token()

    def _get_token(self):
        """Get token from cache or user input"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('token')
        
        # If no cached token, ask user
        token = getpass("Enter your Hugging Face token: ")
        self._cache_token(token)
        return token

    def _cache_token(self, token):
        """Cache the token for future use"""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump({'token': token, 'last_updated': str(datetime.now())}, f)
        
        # Secure the config file
        os.chmod(self.config_file, 0o600)

    def _check_git_repo(self):
        """Initialize git repo if not exists"""
        if not Path('.git').exists():
            subprocess.run(['git', 'init'])
            subprocess.run(['git', 'remote', 'add', 'origin', 
                          f'https://huggingface.co/spaces/{self.space_name}'])

    def _check_files_exist(self):
        """Verify all required files exist"""
        required_files = [
            'app.py',
            'nutrient_calculator.py',
            'requirements.txt',
            'README.md'
        ]
        
        missing_files = [f for f in required_files if not Path(f).exists()]
        if missing_files:
            raise FileNotFoundError(f"Missing required files: {', '.join(missing_files)}")

    def deploy(self):
        """Deploy to Hugging Face Spaces"""
        try:
            print("🚀 Starting deployment process...")
            
            # Verify files
            self._check_files_exist()
            print("✅ Required files verified")
            
            # Setup git
            self._check_git_repo()
            print("✅ Git repository configured")
            
            # Configure git credentials
            subprocess.run(['git', 'config', '--global', 'credential.helper', 'store'])
            
            # Add files
            subprocess.run(['git', 'add', '.'])
            
            # Commit
            commit_msg = f"Update deployment {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_msg])
            
            # Push to Hugging Face
            push_command = [
                'git', 'push',
                f'https://{self.token}@huggingface.co/spaces/{self.space_name}',
                'main'
            ]
            result = subprocess.run(push_command, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Deployment successful!")
                print(f"🌐 Visit your space at: {self.api_url}")
            else:
                print("❌ Deployment failed!")
                print(f"Error: {result.stderr}")
            
        except Exception as e:
            print(f"❌ Deployment failed: {str(e)}")
            raise

    def check_status(self):
        """Check deployment status"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{self.api_url}/api/status", headers=headers)
            
            if response.status_code == 200:
                status = response.json()
                print(f"Space Status: {status.get('status', 'Unknown')}")
                return status
            else:
                print(f"Failed to get status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error checking status: {str(e)}")
            return None

if __name__ == "__main__":
    deployer = HuggingFaceDeployer()
    
    print("🌱 Hydroponic Calculator Deployer")
    print("=================================")
    
    while True:
        print("\nOptions:")
        print("1. Deploy to Hugging Face")
        print("2. Check deployment status")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            deployer.deploy()
        elif choice == '2':
            deployer.check_status()
        elif choice == '3':
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please try again.") 