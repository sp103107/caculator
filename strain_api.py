import streamlit as st
from typing import Dict, List, Optional
import json
from pathlib import Path
import random
from datetime import datetime
import requests

class StrainAPI:
    def __init__(self):
        # Initialize with default data, no API connection required
        self.categories = [
            "Flavor Focused",
            "High THC",
            "Medical",
            "Balanced Hybrid",
            "Autoflower",
            "High Yield"
        ]
        
        # Load local database
        self.strains_db = self._load_local_database()
        
        # Initialize cache in session state if not exists
        if 'strain_cache' not in st.session_state:
            st.session_state.strain_cache = {}

    def _load_local_database(self) -> Dict:
        """Load local strain database"""
        default_strains = {
            "Northern Lights": {
                "name": "Northern Lights",
                "category": "Indica Dominant",
                "thc_range": "16-21%",
                "cbd_range": "0.1-0.3%",
                "flowering_time": "7-8 weeks",
                "difficulty": "Easy",
                "feeding_schedule": {
                    "veg": "Light",
                    "flower": "Medium",
                    "notes": "Hardy and forgiving"
                },
                "nutrient_sensitivity": "Low",
                "optimal_ec": {
                    "early_veg": "0.6-1.0",
                    "late_veg": "1.0-1.4",
                    "early_flower": "1.2-1.6",
                    "mid_flower": "1.4-1.8",
                    "late_flower": "1.0-1.4"
                },
                "optimal_ph": "5.8-6.3"
            },
            "Gorilla Glue #4": {
                "name": "Gorilla Glue #4",
                "category": "Hybrid",
                "thc_range": "25-30%",
                # ... other strain details ...
            }
        }
        return default_strains

    def search_strains(self, query: str) -> List[Dict]:
        """Search strains by name"""
        if not query:
            return list(self.strains_db.values())
            
        query = query.lower()
        return [
            strain for strain in self.strains_db.values()
            if query in strain['name'].lower()
        ]

    def get_categories(self) -> List[str]:
        """Get available strain categories"""
        return self.categories
    
    def generate_strain(self, category: str) -> Optional[Dict]:
        """Generate a random strain based on category"""
        try:
            response = requests.post(
                f"{self.api_base_url}/generate",
                json={"category": category}
            )
            
            if response.status_code == 200:
                return response.json()
            
            # Fallback to local generation
            return self._generate_local_strain(category)
            
        except Exception as e:
            st.warning(f"Using local generation: {str(e)}")
            return self._generate_local_strain(category)

    def _generate_local_strain(self, category: str) -> Optional[Dict]:
        """Generate a random strain locally"""
        matching_strains = [
            strain for strain in self.strains_db.values()
            if strain['category'] == category
        ]
        return random.choice(matching_strains) if matching_strains else None

    def get_strain_details(self, strain_name: str) -> Optional[Dict]:
        """Get detailed information about a specific strain"""
        return self.strains_db.get(strain_name)
    
    def _is_cache_valid(self, timestamp: str) -> bool:
        """Check if cached data is still valid"""
        if not timestamp:
            return False
        cached_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        time_diff = (datetime.now() - cached_time).total_seconds() / 60
        return time_diff < self.cache_timeout
    
    def _get_default_strains(self) -> Dict:
        """Return built-in default strains"""
        return {
            "OG Kush": {
                "name": "OG Kush",
                "category": "Hybrid",
                "thc_range": "20-25%",
                "cbd_range": "0.1-0.3%",
                "flowering_time": "8-9 weeks",
                "difficulty": "Moderate",
                "feeding_schedule": {
                    "veg": "Medium",
                    "flower": "Heavy",
                    "notes": "Cal-Mag sensitive"
                },
                "nutrient_sensitivity": "Medium-High",
                "optimal_ec": {
                    "early_veg": "0.8-1.2",
                    "late_veg": "1.2-1.6",
                    "early_flower": "1.4-1.8",
                    "mid_flower": "1.6-2.0",
                    "late_flower": "1.2-1.6"
                },
                "optimal_ph": "6.0-6.3"
            },
            "Blue Dream": {
                "name": "Blue Dream",
                "category": "Hybrid",
                "thc_range": "17-24%",
                "cbd_range": "0.1-0.2%",
                "flowering_time": "9-10 weeks",
                "difficulty": "Easy",
                "feeding_schedule": {
                    "veg": "Medium",
                    "flower": "Medium",
                    "notes": "Well-balanced feeder"
                },
                "nutrient_sensitivity": "Low",
                "optimal_ec": {
                    "early_veg": "0.6-1.0",
                    "late_veg": "1.0-1.4",
                    "early_flower": "1.2-1.6",
                    "mid_flower": "1.4-1.8",
                    "late_flower": "1.0-1.4"
                },
                "optimal_ph": "5.8-6.2"
            },
            "Girl Scout Cookies": {
                "name": "Girl Scout Cookies",
                "category": "Hybrid",
                "thc_range": "25-28%",
                "cbd_range": "0.1-0.2%",
                "flowering_time": "9-10 weeks",
                "difficulty": "Moderate",
                "feeding_schedule": {
                    "veg": "Light",
                    "flower": "Medium-Heavy",
                    "notes": "Sensitive to nitrogen"
                },
                "nutrient_sensitivity": "High",
                "optimal_ec": {
                    "early_veg": "0.6-1.0",
                    "late_veg": "1.0-1.4",
                    "early_flower": "1.2-1.6",
                    "mid_flower": "1.4-1.8",
                    "late_flower": "1.0-1.4"
                },
                "optimal_ph": "6.0-6.5"
            }
        }
    
    def display_strain_info(self, strain: Dict):
        """Display strain information in a formatted way"""
        st.markdown(f"""
        <div class="strain-card detailed">
            <h3>{strain['name']}</h3>
            <div class="strain-details">
                <p><strong>Category:</strong> {strain['category']}</p>
                <p><strong>THC Range:</strong> {strain['thc_range']}</p>
                <p><strong>CBD Range:</strong> {strain['cbd_range']}</p>
                <p><strong>Flowering Time:</strong> {strain['flowering_time']}</p>
                <p><strong>Difficulty:</strong> {strain['difficulty']}</p>
                <p><strong>Nutrient Sensitivity:</strong> {strain['nutrient_sensitivity']}</p>
                <p><strong>Optimal pH:</strong> {strain['optimal_ph']}</p>
            </div>
            
            <div class="feeding-schedule">
                <h4>Feeding Schedule</h4>
                <p><strong>Vegetative:</strong> {strain['feeding_schedule']['veg']}</p>
                <p><strong>Flowering:</strong> {strain['feeding_schedule']['flower']}</p>
                <p><strong>Notes:</strong> {strain['feeding_schedule']['notes']}</p>
            </div>
            
            <div class="ec-ranges">
                <h4>EC Ranges</h4>
                <table class="ec-table">
                    <tr>
                        <td><strong>Early Veg:</strong></td>
                        <td>{strain['optimal_ec']['early_veg']}</td>
                    </tr>
                    <tr>
                        <td><strong>Late Veg:</strong></td>
                        <td>{strain['optimal_ec']['late_veg']}</td>
                    </tr>
                    <tr>
                        <td><strong>Early Flower:</strong></td>
                        <td>{strain['optimal_ec']['early_flower']}</td>
                    </tr>
                    <tr>
                        <td><strong>Mid Flower:</strong></td>
                        <td>{strain['optimal_ec']['mid_flower']}</td>
                    </tr>
                    <tr>
                        <td><strong>Late Flower:</strong></td>
                        <td>{strain['optimal_ec']['late_flower']}</td>
                    </tr>
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def get_nutrient_recommendations(self, strain_name: str, growth_stage: str) -> Dict:
        """Get nutrient recommendations for a specific strain and growth stage"""
        strain = self.strains_db.get(strain_name)
        if not strain:
            return {}
            
        # Map growth stage to EC ranges
        stage_map = {
            "Seedling": "early_veg",
            "Early Veg": "early_veg",
            "Late Veg": "late_veg",
            "Pre-Flower": "early_flower",
            "Early Flower": "early_flower",
            "Mid Flower": "mid_flower",
            "Late Flower": "late_flower",
            "Flush": "late_flower"
        }
        
        mapped_stage = stage_map.get(growth_stage, "mid_flower")
        ec_range = strain['optimal_ec'][mapped_stage]
        
        return {
            "ec_range": ec_range,
            "ph_range": strain['optimal_ph'],
            "feeding_level": strain['feeding_schedule']['flower' if 'Flower' in growth_stage else 'veg'],
            "sensitivity": strain['nutrient_sensitivity']
        } 