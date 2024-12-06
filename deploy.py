import os
import json
import subprocess
from pathlib import Path
from getpass import getpass
import requests
from datetime import datetime

class HuggingFaceDeployer:
    def __init__(self):
        self.space_name = "sp103107/canna_calc"
        self.api_url = f"https://huggingface.co/spaces/{self.space_name}"
        self.token = self._get_token()
        self.current_dir = Path.cwd()

    def _get_token(self):
        """Get token from environment or user input"""
        token = os.getenv('HF_TOKEN') or getpass("Enter your Hugging Face token: ").strip()
        if not token:
            raise ValueError("Token cannot be empty")
        return token

    def _run_git(self, command, **kwargs):
        """Run git command with proper error handling"""
        try:
            result = subprocess.run(
                command,
                cwd=str(self.current_dir),
                capture_output=True,
                text=True,
                timeout=30,
                **kwargs
            )
            return result
        except subprocess.TimeoutExpired:
            print(f"Command timed out: {' '.join(command)}")
            raise
        except Exception as e:
            print(f"Command failed: {' '.join(command)}")
            print(f"Error: {str(e)}")
            raise

    def deploy(self):
        """Deploy to Hugging Face Spaces"""
        try:
            print("\n🚀 Starting deployment...")

            # Check what files are being tracked
            print("\nChecking git status...")
            status_result = self._run_git(['git', 'status'])
            print(status_result.stdout)

            # Stage specific files
            print("\nStaging files...")
            files_to_track = [
                'app.py',
                'deploy.py',
                'requirements.txt',
                'static/',
                'README.md',
                '.gitignore'
            ]
            
            for file in files_to_track:
                try:
                    self._run_git(['git', 'add', file])
                    print(f"Added {file}")
                except Exception as e:
                    print(f"Warning: Could not add {file}: {str(e)}")

            # Show what's being committed
            status_after = self._run_git(['git', 'status'])
            print("\nFiles to be committed:")
            print(status_after.stdout)

            # Commit changes
            print("\nCommitting changes...")
            commit_msg = f"Deployment {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            commit_result = self._run_git(['git', 'commit', '-m', commit_msg, '--allow-empty'])
            print(commit_result.stdout)

            # Push to Hugging Face
            print("\nPushing to Hugging Face...")
            push_result = self._run_git(
                ['git', 'push', '-f', 'origin', 'main'],
                check=True
            )
            print(push_result.stdout)

            if push_result.returncode == 0:
                print("\n✅ Deployment successful!")
                print(f"🌐 Visit your space at: {self.api_url}")
                return True
            else:
                print("\n❌ Push failed!")
                print("Error output:", push_result.stderr)
                return False

        except Exception as e:
            print(f"\n❌ Deployment failed: {str(e)}")
            return False

    def check_status(self):
        """Check space status"""
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{self.api_url}/api/status", headers=headers)
            
            if response.status_code == 200:
                status = response.json()
                print(f"\nSpace Status: {status.get('status', 'Unknown')}")
                return status
            else:
                print(f"\nFailed to get status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"\nError checking status: {str(e)}")
            return None

def main():
    print("🌱 Hugging Face Space Deployer")
    print("==============================")
    
    deployer = HuggingFaceDeployer()
    
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
            print("\nGoodbye! 👋")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main() 