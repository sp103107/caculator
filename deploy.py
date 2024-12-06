import os
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
import time

class HuggingFaceDeployer:
    def __init__(self):
        self.space_name = "sp103107/canna_calc"
        self.api_url = f"https://huggingface.co/spaces/{self.space_name}"
        print("\n🔑 Get your token from: https://huggingface.co/settings/tokens")
        self.token = input("Enter your Hugging Face token: ").strip()
        if not self.token:
            raise ValueError("Token cannot be empty")
        self.current_dir = Path.cwd()

    def _run_git(self, command, timeout=60, **kwargs):
        """Run git command with proper error handling"""
        try:
            print(f"Executing: git {' '.join(command)}")
            result = subprocess.run(
                ['git'] + command,
                cwd=str(self.current_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                **kwargs
            )
            if result.stdout:
                print("Output:", result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            return result
        except subprocess.TimeoutExpired:
            print(f"Command timed out after {timeout} seconds")
            raise
        except Exception as e:
            print(f"Command failed: git {' '.join(command)}")
            print(f"Error: {str(e)}")
            raise

    def deploy(self):
        """Deploy to Hugging Face Spaces"""
        try:
            print("\n🚀 Starting deployment...")

            # Remove git credentials
            print("\nRemoving git credentials...")
            self._run_git(['config', '--unset-all', 'credential.helper'])

            # Remove existing remote
            print("\nRemoving existing remote...")
            self._run_git(['remote', 'remove', 'origin'], check=False)

            # Add new remote with token
            print("\nAdding new remote...")
            remote_url = f"https://{self.token}@huggingface.co/spaces/{self.space_name}"
            self._run_git(['remote', 'add', 'origin', remote_url])

            # Verify remote
            print("\nVerifying remote...")
            self._run_git(['remote', '-v'])

            # Stage files
            print("\nStaging files...")
            self._run_git(['add', '-A'])
            
            # Show status
            print("\nChecking status...")
            self._run_git(['status'])

            # Commit
            print("\nCommitting changes...")
            commit_msg = f"Deployment {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self._run_git(['commit', '-m', commit_msg, '--allow-empty'])

            # Push with longer timeout
            print("\nPushing to Hugging Face (this may take a minute)...")
            try:
                push_result = self._run_git(['push', '-f', 'origin', 'main'], timeout=120)
                
                if push_result.returncode == 0:
                    print("\n✅ Deployment successful!")
                    print(f"🌐 Visit your space at: {self.api_url}")
                    return True
                else:
                    print("\n❌ Push failed!")
                    print("Error output:", push_result.stderr)
                    return False

            except subprocess.TimeoutExpired:
                print("\n⚠️ Push timed out, checking space status...")
                time.sleep(5)
                return self.check_status()

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
    
    try:
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
    
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled. Goodbye! 👋")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 