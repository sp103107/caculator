import streamlit as st
import streamlit.components.v1 as components
from nutrient_calculator import NutrientCalculatorUI
import base64
from pathlib import Path
from strain_api import StrainAPI
from recipe_instructions import RecipeInstructions
from datetime import datetime
import os

# Ensure paths work in Streamlit Cloud
def get_project_root():
    return Path(__file__).parent

# Add this after the imports and before the functions
growth_stages = {
    "Seedling": "🌱",
    "Early Veg": "🌿",
    "Late Veg": "🌿",
    "Pre-Flower": "🌸",
    "Early Flower": "🌺",
    "Mid Flower": "🌺",
    "Late Flower": "🌺",
    "Flush": "💧"
}

def load_css():
    """Load CSS with error handling and fallback"""
    try:
        css_file = get_project_root() / "static" / "style.css"
        if css_file.exists():
            with open(css_file) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        else:
            # Fallback inline CSS
            st.markdown("""
                <style>
                    .calculator-section { padding: 1rem; }
                    .recipe-card { 
                        background: white;
                        padding: 1rem;
                        border-radius: 8px;
                        margin: 1rem 0;
                    }
                </style>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to load CSS: {str(e)}")

def add_logo():
    st.markdown(
        """
        <div style="text-align: center; padding: 20px;">
            <img src="https://your-logo-url.com/logo.png" width="200">
        </div>
        """,
        unsafe_allow_html=True
    )

def create_layout():
    st.set_page_config(
        page_title="Professional Hydroponic Calculator",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    load_css()
    
    # Sidebar for settings
    with st.sidebar:
        st.title("⚙️ Settings")
        theme = st.selectbox(
            "Color Theme",
            ["Professional", "High Contrast", "Dark Mode"],
            key="theme_selector"
        )
        
        st.divider()
        
        st.markdown("### Quick Links")
        st.markdown("""
        - [Documentation 📚](/)
        - [Support 🛟](/)
        - [About 🏢](/)
        """)
        
        st.divider()
        
        # Version info
        st.markdown("v1.0.0 | © 2024 Professional Hydro")

def display_troubleshooting_guide():
    st.markdown("""
    ### 🔧 Troubleshooting Guide
    
    <div class="troubleshooting-card">
        <table class="guide-table">
            <thead>
                <tr>
                    <th>Issue</th>
                    <th>Solution</th>
                </tr>
            </thead>
            <tbody>
                <tr class="guide-row warning">
                    <td>High EC</td>
                    <td>Dilute with fresh water, recheck after circulation</td>
                </tr>
                <tr class="guide-row warning">
                    <td>Low EC</td>
                    <td>Add nutrients proportionally to reach target</td>
                </tr>
                <tr class="guide-row caution">
                    <td>pH Fluctuation</td>
                    <td>Allow solution to stabilize before final adjustment</td>
                </tr>
                <tr class="guide-row danger">
                    <td>Precipitation</td>
                    <td>Mix more slowly, ensure proper order of addition</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Hydroponic Calculator",
        page_icon="🌱",
        layout="wide"
    )
    
    load_css()
    
    # Initialize strain API without requiring secrets
    strain_api = StrainAPI()
    
    create_layout()
    
    st.title("Professional Hydroponic Calculator")
    st.markdown("### Enterprise-Grade Nutrient Management System")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Calculator", "Strain Selection", "Recipe Instructions", "Calculation History"])
    
    with tab1:
        # Calculator inputs on top
        st.markdown('<div class="calculator-section">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            nutrient_line = st.selectbox(
                "Nutrient Line",
                ["Generic", "General Hydroponics", "Advanced Nutrients", "Athena"],
                help="Select your nutrient brand or use generic calculations"
            )
            
            unit_system = st.radio(
                "Unit System",
                ["US Gallons", "Liters"],
                horizontal=True
            )
        
        with col2:
            volume = st.number_input(
                f"Reservoir Size ({unit_system})",
                min_value=1.0,
                max_value=1000.0,
                value=50.0
            )
            
            strength = st.slider(
                "Nutrient Strength",
                min_value=25,
                max_value=125,
                value=100,
                help="Adjust overall nutrient strength"
            )
        
        with col3:
            stage = st.selectbox(
                "Growth Stage",
                list(growth_stages.keys()),
                format_func=lambda x: f"{growth_stages[x]} {x}"
            )
        
        if st.button("Calculate Recipe", type="primary"):
            with st.spinner("Calculating..."):
                try:
                    calculator = NutrientCalculatorUI()
                    recipe = calculator.calculate_recipe(
                        nutrient_line=nutrient_line,
                        volume=volume,
                        growth_stage=stage,
                        strength=strength/100,
                        unit_system=unit_system.split()[0]
                    )
                    
                    if recipe:
                        st.session_state.current_recipe = recipe
                        # Display recipe card...
                    else:
                        st.error("Failed to calculate recipe. Please check your inputs.")
                        
                except Exception as e:
                    st.error(f"Calculation error: {str(e)}")
    
    with tab2:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Strain search
            search_query = st.text_input(
                "Search Strains",
                help="Enter strain name to search"
            )
            
            if search_query:
                with st.spinner("Searching strains..."):
                    results = strain_api.search_strains(search_query)
                    
                if results:
                    selected_strain = st.selectbox(
                        "Select Strain",
                        options=[strain['name'] for strain in results],
                        key="strain_select"
                    )
                    
                    # Find the selected strain data
                    strain_data = next(
                        (strain for strain in results if strain['name'] == selected_strain),
                        None
                    )
                    
                    if strain_data:
                        # Display detailed strain information
                        strain_api.display_strain_info(strain_data)
                        
                        if st.button("Add Strain"):
                            if "selected_strains" not in st.session_state:
                                st.session_state.selected_strains = []
                            st.session_state.selected_strains.append(strain_data)
                            st.success(f"Added {selected_strain}")
                else:
                    st.warning("No strains found")
        
        with col2:
            # Strain generator
            st.markdown("### Strain Generator")
            categories = strain_api.get_categories()
            
            if categories:
                category = st.selectbox(
                    "Select Category",
                    options=categories,
                    key="category_select"
                )
                
                if st.button("Generate Random Strain"):
                    with st.spinner("Generating strain..."):
                        strain = strain_api.generate_strain(category)
                    
                    if strain:
                        # Display detailed strain information
                        strain_api.display_strain_info(strain)
                        
                        if st.button("Add Generated Strain"):
                            if "selected_strains" not in st.session_state:
                                st.session_state.selected_strains = []
                            st.session_state.selected_strains.append(strain)
                            st.success(f"Added {strain['name']}")
            
        # Display selected strains
        if "selected_strains" in st.session_state and st.session_state.selected_strains:
            st.markdown("### Selected Strains")
            for i, strain in enumerate(st.session_state.selected_strains):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class="strain-card">
                        <h4>{strain['name']}</h4>
                        <p>Category: {strain.get('category', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.selected_strains.pop(i)
                        st.rerun()
    
    with tab3:
        recipe_instructions = RecipeInstructions()
        
        # Example recipe data
        recipe = {
            "Cal-Mag": {
                "amount": "1 ml/gal",
                "order": 1,
                "notes": "Add first, allow to mix"
            },
            "Base A": {
                "amount": "3 ml/gal",
                "order": 2,
                "notes": "Add slowly while circulating"
            },
            "Base B": {
                "amount": "3 ml/gal",
                "order": 3,
                "notes": "Wait 5 minutes after Base A"
            },
            "Supplements": {
                "amount": "Varies",
                "order": 4,
                "notes": "Add last, one at a time"
            }
        }
        
        recipe_instructions.display_instructions(nutrient_line, recipe)
    
    with tab4:
        st.markdown("### Calculation History")
        # Add history tracking functionality here

if __name__ == "__main__":
    main() 