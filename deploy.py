import os
import json
import subprocess
from pathlib import Path
from getpass import getpass
import requests
from datetime import datetime
import shlex

class HuggingFaceDeployer:
    def __init__(self):
        self.config_dir = Path.home() / '.huggingface'
        self.config_file = self.config_dir / 'config.json'
        self.space_name = "sp103107/canna_calc"
        self.api_url = f"https://huggingface.co/spaces/{self.space_name}"
        self.token = self._get_token()
        self.current_dir = Path.cwd()

    def _get_token(self):
        """Get token from cache or user input"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                token = config.get('token')
                if token and token.strip():  # Verify token is not empty or whitespace
                    return token.strip()
        
        # If no valid cached token, ask user
        token = getpass("Enter your Hugging Face token: ").strip()
        if not token:
            raise ValueError("Token cannot be empty")
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

    def _run_command(self, command, **kwargs):
        """Run command with proper path handling"""
        if isinstance(command, str):
            command = shlex.split(command)
        return subprocess.run(command, cwd=str(self.current_dir), **kwargs)

    def deploy(self):
        try:
            print("🚀 Starting deployment process...")
            print(f"Working directory: {self.current_dir}")
            
            # Verify files
            self._check_files_exist()
            print("✅ Required files verified")
            
            # Setup git
            self._check_git_repo()
            print("✅ Git repository configured")
            
            # Force add all files
            add_result = self._run_command('git add -A', capture_output=True, text=True)
            print("Git add result:", add_result.stdout or add_result.stderr)
            
            # Force a commit even if nothing changed
            commit_msg = f"Force deployment {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            commit_result = self._run_command(
                ['git', 'commit', '-m', commit_msg, '--allow-empty'],
                capture_output=True,
                text=True
            )
            print("Git commit result:", commit_result.stdout or commit_result.stderr)
            
            # Force push to Hugging Face with proper URL encoding
            print("🔄 Pushing to Hugging Face...")
            
            # Debug: Print token length and first/last characters
            token_preview = f"{self.token[:4]}...{self.token[-4:]}"
            print(f"Using token (preview): {token_preview}")
            
            # Try direct git command
            push_url = f'https://{self.token}@huggingface.co/spaces/{self.space_name}'
            print("Attempting push with URL:", push_url.replace(self.token, "TOKEN_HIDDEN"))
            
            try:
                # First attempt: using git command directly
                push_result = subprocess.run(
                    ['git', 'push', '-f', '-v', push_url, 'main'],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self.current_dir)
                )
                print("Push attempt 1 output:", push_result.stdout)
                print("Push attempt 1 errors:", push_result.stderr)
                
                if push_result.returncode != 0:
                    print("First push attempt failed, trying alternative method...")
                    
                    # Second attempt: using git remote
                    self._run_command(['git', 'remote', 'remove', 'hf'])
                    self._run_command(['git', 'remote', 'add', 'hf', push_url])
                    
                    push_result = self._run_command(
                        ['git', 'push', '-f', 'hf', 'main'],
                        capture_output=True,
                        text=True
                    )
                    print("Push attempt 2 output:", push_result.stdout)
                    print("Push attempt 2 errors:", push_result.stderr)
            
            except subprocess.TimeoutExpired:
                print("❌ Push timed out after 30 seconds")
                raise
            
            if push_result.returncode == 0:
                print("✅ Deployment successful!")
                print(f"🌐 Visit your space at: {self.api_url}")
            else:
                print("❌ Deployment failed!")
                print(f"Error: {push_result.stderr}")
            
        except Exception as e:
            print(f"❌ Deployment failed: {str(e)}")
            print("Full error details:", str(e.__class__.__name__))
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

    def clear_token(self):
        """Clear the cached token"""
        try:
            if self.config_file.exists():
                os.remove(self.config_file)
                print("✅ Token cache cleared successfully")
            else:
                print("No cached token found")
        except Exception as e:
            print(f"❌ Error clearing token: {str(e)}")

if __name__ == "__main__":
    deployer = HuggingFaceDeployer()
    
    print("🌱 Hydroponic Calculator Deployer")
    print("=================================")
    
    while True:
        print("\nOptions:")
        print("1. Deploy to Hugging Face")
        print("2. Check deployment status")
        print("3. Clear cached token")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            deployer.deploy()
        elif choice == '2':
            deployer.check_status()
        elif choice == '3':
            deployer.clear_token()
            # Reinitialize deployer to force new token prompt
            deployer = HuggingFaceDeployer()
        elif choice == '4':
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please try again.") 