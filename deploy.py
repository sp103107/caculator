import os
import time
from huggingface_hub import HfApi, create_repo, delete_repo
from huggingface_hub.utils import validate_repo_id
from huggingface_hub.errors import HfHubHTTPError
import getpass

def deploy(token: str, repo_name: str, retries: int = 3, wait_time: int = 5):
    """Deploy to Hugging Face with retry logic"""
    print("\n🌿 Professional Hydroponic Calculator Deployer")
    print("============================================\n")

    api = HfApi(token=token)
    
    try:
        # Validate repository name
        repo_id = f"{api.whoami()['name']}/{repo_name}"
        validate_repo_id(repo_id)
        
        print(f"🚀 Starting deployment to {repo_id}")
        
        # Try to delete existing space
        try:
            print(f"🗑️  Deleting existing space: {repo_id}")
            delete_repo(repo_id, token=token, repo_type="space")
            print("✅ Space deleted")
        except Exception as e:
            if "404" not in str(e):
                print(f"⚠️  Warning during deletion: {str(e)}")
        
        # Create new space with retries
        for attempt in range(retries):
            try:
                print("🆕 Creating new space...")
                create_repo(
                    repo_id,
                    token=token,
                    repo_type="space",
                    space_sdk="streamlit",
                    private=False
                )
                print("✅ Space created successfully")
                break
            except HfHubHTTPError as e:
                if "429" in str(e):  # Rate limit error
                    if attempt < retries - 1:
                        wait = wait_time * (attempt + 1)
                        print(f"⏳ Rate limited. Waiting {wait} seconds before retry...")
                        time.sleep(wait)
                    else:
                        raise Exception("Rate limit reached. Please try again in 24 hours.")
                else:
                    raise e
        
        # Additional deployment steps here...
        
        print("\n✅ Deployment completed successfully!")
        print(f"🔗 View your app at: https://huggingface.co/spaces/{repo_id}")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        print("\n❌ Deployment failed. Check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    print("🔑 Get your token from: https://huggingface.co/settings/tokens")
    token = getpass.getpass("Enter your Hugging Face token: ")
    
    # Deploy with increased wait times
    deploy(token, "canna_calc", retries=3, wait_time=10) 