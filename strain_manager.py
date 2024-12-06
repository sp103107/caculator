import requests
from typing import Optional, List, Dict
import json

class StrainManager:
    def __init__(self):
        self.base_url = "YOUR_API_BASE_URL"
        self.categories = self._fetch_categories()
        
    def _fetch_categories(self) -> List[str]:
        """Fetch available strain categories"""
        try:
            response = requests.get(f"{self.base_url}/api/categories")
            return response.json().get("categories", [])
        except:
            return ["Flavor Focused", "High THC", "Medical", 
                   "Balanced Hybrid", "Autoflower", "High Yield"]
    
    def search_strains(self, query: str) -> List[Dict]:
        """Search strains by name"""
        try:
            response = requests.get(f"{self.base_url}/api/search", 
                                  params={"q": query})
            return response.json().get("results", [])
        except:
            return []
    
    def generate_strain(self, category: str) -> Optional[Dict]:
        """Generate a random strain based on category"""
        try:
            response = requests.post(f"{self.base_url}/api/generate",
                                   json={"category": category})
            return response.json()
        except:
            return None 