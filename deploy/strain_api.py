import requests
from typing import Dict, List, Optional

class StrainAPI:
    def __init__(self):
        self.base_url = "YOUR_API_BASE_URL"  # Replace with your actual API base URL
        
    def search_strains(self, query: str) -> List[Dict]:
        """Search strains using the API"""
        try:
            response = requests.get(f"{self.base_url}/api/search", params={"q": query})
            if response.status_code == 200:
                return response.json().get("results", [])
            return []
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return []
    
    def get_categories(self) -> List[str]:
        """Get available strain categories"""
        try:
            response = requests.get(f"{self.base_url}/api/categories")
            if response.status_code == 200:
                return response.json().get("categories", [])
            return []
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return []
    
    def generate_strain(self, category: str) -> Optional[Dict]:
        """Generate a random strain based on category"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"category": category}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None 