from typing import Dict, List
import streamlit as st

class RecipeInstructions:
    def __init__(self):
        self.mixing_phases = {
            "preparation": {
                "title": "🔍 Preparation Phase",
                "icon": "🧪",
                "importance": "critical",
                "steps": [
                    {
                        "action": "Clean all mixing equipment thoroughly",
                        "detail": "Use food-grade sanitizer, rinse 3x with RO water",
                        "warning": "Contamination can lead to root problems"
                    },
                    {
                        "action": "Calibrate pH and EC/PPM meters",
                        "detail": "Use fresh calibration solutions, verify accuracy",
                        "warning": "Inaccurate readings can lead to nutrient lockout"
                    },
                    {
                        "action": "Verify water temperature",
                        "detail": "Target: 65-75°F (18-24°C)",
                        "warning": "Temperature affects nutrient availability"
                    },
                    {
                        "action": "Record starting parameters",
                        "detail": "Log: pH, EC/PPM, temperature, date/time",
                        "warning": "Documentation required for compliance"
                    }
                ]
            },
            "primary_mix": {
                "title": "🌊 Primary Mixing Phase",
                "icon": "⚗️",
                "importance": "critical",
                "steps": [
                    {
                        "action": "Fill reservoir to 75% volume",
                        "detail": "Use filtered/RO water at correct temperature",
                        "warning": "Leave room for additives and final adjustment"
                    },
                    {
                        "action": "Start circulation system",
                        "detail": "Ensure proper aeration and mixing patterns",
                        "warning": "Minimum 800 GPH pump rate recommended"
                    },
                    {
                        "action": "Add Cal-Mag (if using)",
                        "detail": "Mix thoroughly for 15 minutes",
                        "warning": "Critical for preventing calcium lockout"
                    },
                    {
                        "action": "Add Part A nutrients",
                        "detail": "Mix slowly, monitor for precipitation",
                        "warning": "Never mix concentrates directly"
                    },
                    {
                        "action": "Add Part B nutrients",
                        "detail": "Wait minimum 5 minutes after Part A",
                        "warning": "Calcium/phosphate precipitation risk"
                    }
                ]
            },
            "supplements": {
                "title": "🧬 Supplement Addition",
                "icon": "🧪",
                "importance": "moderate",
                "steps": [
                    {
                        "action": "Add pH buffers if needed",
                        "detail": "Target pH range: 5.5-6.3",
                        "warning": "Add slowly, allow stabilization"
                    },
                    {
                        "action": "Add organic supplements",
                        "detail": "Follow manufacturer's order of addition",
                        "warning": "Some may affect pH/EC significantly"
                    },
                    {
                        "action": "Add beneficial microbes",
                        "detail": "Water temp must be below 75°F",
                        "warning": "Chlorine must be removed first"
                    }
                ]
            },
            "final": {
                "title": "✅ Final Verification",
                "icon": "📊",
                "importance": "critical",
                "steps": [
                    {
                        "action": "Top off to final volume",
                        "detail": "Use RO/filtered water only",
                        "warning": "Record final volume added"
                    },
                    {
                        "action": "Verify EC/PPM levels",
                        "detail": "Compare to target range for growth stage",
                        "warning": "Document any adjustments made"
                    },
                    {
                        "action": "Final pH adjustment",
                        "detail": "Adjust slowly, verify stability",
                        "warning": "Allow 15-30 minutes between adjustments"
                    },
                    {
                        "action": "Final documentation",
                        "detail": "Record all parameters and calculations",
                        "warning": "Required for compliance tracking"
                    }
                ]
            }
        }

        # Add CSS for styling
        self.add_custom_css()

    def add_custom_css(self):
        st.markdown("""
        <style>
        .instruction-phase {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid;
        }
        
        .phase-critical {
            border-color: #dc3545;
        }
        
        .phase-moderate {
            border-color: #ffc107;
        }
        
        .step-card {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
        }
        
        .step-action {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .step-detail {
            color: #34495e;
            margin: 5px 0;
        }
        
        .step-warning {
            color: #dc3545;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .parameter-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        .parameter-table th {
            background: #f8f9fa;
            padding: 10px;
            text-align: left;
        }
        
        .parameter-table td {
            padding: 8px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .verification-checklist {
            background: #e9ecef;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
        }
        
        .phase-icon {
            font-size: 1.5em;
            margin-right: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    def display_instructions(self, nutrient_line: str, recipe: Dict):
        """Display mixing instructions for the recipe"""
        if not recipe:
            st.warning("No recipe data available. Please calculate a recipe first.")
            return
        
        # Add print button
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("🖨️ Print"):
                st.markdown("""
                <script>
                    window.print()
                </script>
                """, unsafe_allow_html=True)
        
        st.markdown("## 📋 Professional Mixing Protocol")
        
        # Sort recipe items by mixing order
        def get_mixing_order(nutrient_type):
            order = {
                'silica': 1,
                'calmag': 2,
                'micro': 3,
                'grow': 4,
                'bloom': 5,
                'pk_boost': 6,
                'supplement': 7
            }
            return order.get(nutrient_type, 999)
        
        sorted_recipe = dict(sorted(
            recipe.items(),
            key=lambda x: get_mixing_order(x[1].get('type', 'supplement'))
        ))
        
        # Display preparation phase
        st.markdown("""
        <div class="instruction-phase phase-critical">
            <h3>
                <span class="phase-icon">🔍</span>
                Preparation Phase
            </h3>
        """, unsafe_allow_html=True)
        
        for step in self.mixing_phases['preparation']['steps']:
            st.markdown(self._create_step_card(step), unsafe_allow_html=True)
        
        # Display mixing instructions based on recipe
        st.markdown("""
        <div class="instruction-phase phase-critical">
            <h3>
                <span class="phase-icon">⚗️</span>
                Mixing Sequence
            </h3>
        """, unsafe_allow_html=True)
        
        for nutrient, details in sorted_recipe.items():
            step = {
                "action": f"Add {nutrient}",
                "detail": f"Amount: {details.get('amount', 'N/A')} {details.get('unit', 'ml')} - {details.get('notes', '')}",
                "warning": self._get_warning_for_nutrient(nutrient, details.get('type'))
            }
            st.markdown(self._create_step_card(step), unsafe_allow_html=True)
        
        # Display verification phase
        st.markdown("""
        <div class="instruction-phase phase-critical">
            <h3>
                <span class="phase-icon">✅</span>
                Final Verification
            </h3>
        """, unsafe_allow_html=True)
        
        for step in self.mixing_phases['final']['steps']:
            st.markdown(self._create_step_card(step), unsafe_allow_html=True)
        
        # Display target parameters
        st.markdown(f"""
        <div class="parameter-card">
            <h4>🎯 Target Parameters for {nutrient_line}</h4>
            <div class="parameter-grid">
                <div class="parameter">
                    <span class="label">EC Range</span>
                    <span class="value">{self._get_ec_range(recipe)}</span>
                </div>
                <div class="parameter">
                    <span class="label">pH Range</span>
                    <span class="value">5.8-6.2</span>
                </div>
                <div class="parameter">
                    <span class="label">Temperature</span>
                    <span class="value">65-75°F (18-24°C)</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _get_warning_for_nutrient(self, nutrient: str, nutrient_type: str = None) -> str:
        """Get specific warnings for each nutrient type"""
        # If type isn't provided, try to determine from nutrient name
        if nutrient_type is None:
            nutrient_type = self._determine_nutrient_type(nutrient)
        
        warnings = {
            'calmag': "Monitor pH, can increase significantly",
            'base': "Check for precipitation, ensure proper mixing",
            'micro': "Add first of base nutrients",
            'grow': "Add second, after micro",
            'bloom': "Add last of base nutrients",
            'supplement': "Add slowly, watch for reactions",
            'silica': "Must be added first, raises pH significantly",
            'enzyme': "Temperature sensitive, verify water temp",
            'pk_boost': "Monitor EC closely, can build up salts"
        }
        return warnings.get(nutrient_type, "Monitor solution for any reactions")

    def _determine_nutrient_type(self, nutrient: str) -> str:
        """Determine nutrient type from name if not provided"""
        nutrient = nutrient.lower()
        if 'cal' in nutrient and 'mag' in nutrient:
            return 'calmag'
        elif 'micro' in nutrient:
            return 'micro'
        elif 'grow' in nutrient:
            return 'grow'
        elif 'bloom' in nutrient:
            return 'bloom'
        elif 'silica' in nutrient:
            return 'silica'
        elif any(x in nutrient for x in ['pk', 'p/k', 'phosphorus']):
            return 'pk_boost'
        else:
            return 'supplement'

    def _get_ec_range(self, recipe: Dict) -> str:
        """Calculate target EC range based on recipe composition"""
        try:
            if not recipe:
                return "1.0-1.4"  # Default range
            
            base_count = sum(1 for details in recipe.values() 
                            if details.get('type') in ['micro', 'grow', 'bloom'])
            
            if base_count <= 2:
                return "1.0-1.4"
            elif base_count <= 3:
                return "1.2-1.8"
            else:
                return "1.4-2.0"
        except Exception as e:
            logger.error(f"Error calculating EC range: {str(e)}")
            return "1.0-1.4"  # Default range

    def _create_step_card(self, step: Dict) -> str:
        """Create a step card for a given step"""
        return f"""
        <div class="step-card">
            <div class="step-action">{step['action']}</div>
            <div class="step-detail">{step['detail']}</div>
            <div class="step-warning">⚠️ {step['warning']}</div>
        </div>
        """
 