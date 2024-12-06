import streamlit as st
import streamlit.components.v1 as components
from nutrient_calculator import NutrientCalculatorUI
import base64
from pathlib import Path
from strain_api import StrainAPI
from recipe_instructions import RecipeInstructions

def load_css():
    css_file = Path("static/style.css")
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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

def main():
    create_layout()
    
    # Initialize strain API
    strain_api = StrainAPI()
    
    st.title("Professional Hydroponic Calculator")
    st.markdown("### Enterprise-Grade Nutrient Management System")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Calculator", "Strain Selection", "Recipe Instructions", "Calculation History"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.container():
                st.markdown('<div class="calculator-card">', unsafe_allow_html=True)
                
                # Nutrient Line Selection
                nutrient_line = st.selectbox(
                    "Select Nutrient Line",
                    ["General Hydroponics", "Advanced Nutrients", "Athena", "House & Garden", "Canna", "Generic"],
                    help="Choose your preferred nutrient manufacturer"
                )
                
                # Unit System with custom radio buttons
                st.markdown("""
                <div style="margin: 20px 0;">
                    <div class="unit-selector">
                        <input type="radio" id="us" name="unit" value="US">
                        <label for="us">US Gallons</label>
                        <input type="radio" id="metric" name="unit" value="Metric">
                        <label for="metric">Liters</label>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Volume input with validation
                volume = st.number_input(
                    "Reservoir Size",
                    min_value=1.0,
                    max_value=10000.0,
                    value=100.0,
                    help="Enter your reservoir size"
                )
                
                # Growth stage with visual indicators
                growth_stages = {
                    "Seedling": "🌱",
                    "Early Veg": "🌿",
                    "Late Veg": "🌳",
                    "Pre-Flower": "🌸",
                    "Early Flower": "🌺",
                    "Mid Flower": "🌻",
                    "Late Flower": "🌷",
                    "Flush": "💧"
                }
                
                stage = st.select_slider(
                    "Growth Stage",
                    options=list(growth_stages.keys()),
                    format_func=lambda x: f"{growth_stages[x]} {x}"
                )
                
                # Strength adjustment with color feedback
                strength = st.slider(
                    "Nutrient Strength (%)",
                    min_value=25,
                    max_value=150,
                    value=100,
                    help="Adjust the overall strength of your nutrient solution"
                )
                
                if st.button("Calculate", key="calc_button"):
                    # Show loading animation
                    with st.spinner("Calculating optimal nutrient ratios..."):
                        # Display strain-specific adjustments if strains are selected
                        if "selected_strains" in st.session_state and st.session_state.selected_strains:
                            st.markdown("### Strain-Specific Adjustments")
                            for strain in st.session_state.selected_strains:
                                st.markdown(f"""
                                <div class="strain-card">
                                    <h4>{strain['name']}</h4>
                                    <p>Category: {strain['category']}</p>
                                    <p>Recommended Strength: {strength}%</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Your existing calculation logic...
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Results display
            st.markdown('<div class="results-card">', unsafe_allow_html=True)
            st.subheader("Nutrient Recipe")
            
            # Example metrics (replace with actual calculations)
            metrics = {
                "Base A": "3.2 ml/gal",
                "Base B": "3.2 ml/gal",
                "Calcium": "1.5 ml/gal",
                "Magnesium": "0.8 ml/gal"
            }
            
            for nutrient, amount in metrics.items():
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{nutrient}</h4>
                    <p>{amount}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Add strain information display if selected
        if "selected_strains" in st.session_state:
            st.markdown("### Selected Strains")
            for strain in st.session_state.selected_strains:
                st.markdown(f"""
                <div class="strain-card">
                    <h4>{strain['name']}</h4>
                    <p>Category: {strain['category']}</p>
                    <p>Flowering Time: {strain.get('flowering_time', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
    
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
                    
                    if strain_data and st.button("Add Strain"):
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
                        st.markdown(f"""
                        <div class="strain-card">
                            <h4>{strain['name']}</h4>
                            <p>Category: {strain.get('category', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
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