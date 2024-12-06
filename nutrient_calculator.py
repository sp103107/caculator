import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from pathlib import Path
import json
import logging
from utils.debugger import create_debugger, debugger

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecipeManager:
    def __init__(self):
        # Simplified initialization
        self.recipes = {}
        self.load_default_nutrient_lines()

    def load_default_nutrient_lines(self):
        """Load the top 5 nutrient lines plus generic options"""
        self.nutrient_lines = {
            'General Hydroponics': {
                'description': 'Industry standard 3-part system with comprehensive supplements',
                'base_nutrients': {
                    'Flora Micro': {
                        'type': 'micro',
                        'max_strength': 4.0,
                        'description': 'Concentrated micronutrients and calcium',
                        'npk': '5-0-1'
                    },
                    'Flora Grow': {
                        'type': 'grow',
                        'max_strength': 4.0,  # ml per gallon
                        'npk': '2-1-6',
                        'description': 'Promotes structural and vegetative growth',
                        'when_to_use': 'Heavy in veg, reduced in flower',
                        'benefits': ['Promotes leaf growth', 'Enhances node spacing', 'Builds structure'],
                        'cautions': ['Add after Flora Micro', 'Reduce during flowering'],
                        'ec_impact': 'Medium',
                        'ph_impact': 'Slight decrease'
                    },
                    'Flora Bloom': {
                        'type': 'bloom',
                        'max_strength': 4.0,  # ml per gallon
                        'npk': '0-5-4',
                        'description': 'Promotes flower development and fruiting',
                        'when_to_use': 'During flowering phase',
                        'benefits': ['Enhances flower development', 'Improves yield', 'Boosts essential oils'],
                        'cautions': ['Add last of base nutrients', 'Monitor EC levels']
                    }
                },
                'supplements': {
                    'CaliMagic': {
                        'type': 'calmag',
                        'max_strength': 5.0,  # ml per gallon
                        'description': 'GH\'s calcium and magnesium supplement',
                        'when_to_use': 'Throughout grow cycle, essential with RO water',
                        'benefits': [
                            'Prevents calcium deficiency',
                            'Strengthens cell walls',
                            'Improves nutrient uptake',
                            'Prevents magnesium deficiency'
                        ],
                        'npk': '1-0-0',
                        'contains': {'Ca': '5%', 'Mg': '1.5%'},
                        'cautions': ['Check water hardness first', 'Can raise pH']
                    },
                    'Rapid Start': {
                        'type': 'root',
                        'max_strength': 2.0,  # ml per gallon
                        'description': 'GH\'s root development enhancer',
                        'when_to_use': 'Early growth and transplanting',
                        'benefits': [
                            'Accelerates root development',
                            'Improves nutrient uptake',
                            'Reduces transplant shock',
                            'Enhances stress tolerance'
                        ],
                        'contains': {'Vitamins': 'B1, B2', 'Hormones': 'IBA, NAA'},
                        'cautions': ['Reduce after established roots', 'Monitor pH']
                    },
                    'Diamond Nectar': {
                        'type': 'humic',
                        'max_strength': 2.0,  # ml per gallon
                        'description': 'GH\'s premium humic acid supplement',
                        'when_to_use': 'Throughout grow cycle',
                        'benefits': [
                            'Improves nutrient uptake',
                            'Enhances root development',
                            'Increases chelation',
                            'Improves soil structure'
                        ],
                        'contains': {'Humic acid': '6%', 'Fulvic acid': '3%'},
                        'cautions': ['Can darken solution', 'Monitor pH']
                    },
                    'Armor Si': {
                        'type': 'silica',
                        'max_strength': 2.0,  # ml per gallon
                        'description': 'GH\'s silica supplement',
                        'when_to_use': 'Throughout grow cycle',
                        'benefits': [
                            'Strengthens cell walls',
                            'Improves heat tolerance',
                            'Enhances pest resistance',
                            'Supports heavy flowers'
                        ],
                        'contains': {'Si': '0.5%'},
                        'cautions': [
                            'Must be added FIRST to nutrient solution',
                            'Raises pH significantly',
                            'Don\'t mix directly with concentrated nutrients'
                        ]
                    },
                    'Liquid KoolBloom': {
                        'type': 'pk_boost',
                        'max_strength': 2.5,  # ml per gallon
                        'description': 'GH\'s liquid P-K booster',
                        'when_to_use': 'Early to mid flowering',
                        'benefits': [
                            'Enhances flower formation',
                            'Improves flower size',
                            'Boosts essential oil production'
                        ],
                        'npk': '0-10-10',
                        'cautions': ['Monitor EC', 'Can build up salts']
                    },
                    'Dry KoolBloom': {
                        'type': 'ripening',
                        'max_strength': 1.5,  # grams per gallon
                        'description': 'GH\'s flowering finisher powder',
                        'when_to_use': 'Last 2-3 weeks of flower',
                        'benefits': [
                            'Triggers ripening',
                            'Increases resin production',
                            'Enhances flower density',
                            'Improves essential oil content'
                        ],
                        'npk': '0-27-27',
                        'cautions': [
                            'Use only in late flower',
                            'Monitor EC carefully',
                            'Can cause lockout if overused',
                            'Dissolve completely before adding other nutrients'
                        ]
                    },
                    'Floralicious Plus': {
                        'type': 'enzyme',
                        'max_strength': 1.0,  # ml per gallon
                        'description': 'GH\'s organic bioactivator',
                        'when_to_use': 'Throughout grow cycle',
                        'benefits': [
                            'Enhances nutrient uptake',
                            'Improves flavor profiles',
                            'Boosts terpene production',
                            'Supports beneficial microbes'
                        ],
                        'contains': {
                            'Enzymes': 'Multiple',
                            'Amino acids': 'Complete profile',
                            'Vitamins': 'B1, B2, B6, B12'
                        },
                        'cautions': [
                            'Shake well before use',
                            'Can cloud reservoir',
                            'Add last to nutrient solution'
                        ]
                    },
                    'Florablend': {
                        'type': 'biostimulant',
                        'max_strength': 2.0,  # ml per gallon
                        'description': 'GH\'s organic vegan supplement',
                        'when_to_use': 'Throughout grow cycle',
                        'benefits': [
                            'Enhances nutrient uptake',
                            'Improves plant vigor',
                            'Supports beneficial microbes',
                            'Adds trace elements'
                        ],
                        'contains': {
                            'Seaweed': 'Multiple species',
                            'Minerals': 'Trace elements',
                            'Vitamins': 'Natural blend'
                        },
                        'cautions': [
                            'Shake well before use',
                            'Can settle in reservoir',
                            'Add after base nutrients'
                        ]
                    }
                }
            },
            'Advanced Nutrients': {
                'description': 'pH Perfect technology with premium supplements',
                'base_nutrients': {
                    'pH Perfect Micro': {
                        'type': 'micro',
                        'max_strength': 4.0,
                        'description': 'Self-adjusting pH micronutrient formula',
                        'npk': '5-0-1'
                    },
                    'pH Perfect Grow': {
                        'type': 'grow',
                        'max_strength': 4.0,
                        'description': 'Vegetative growth formula',
                        'npk': '4-0-1'
                    },
                    'pH Perfect Bloom': {
                        'type': 'bloom',
                        'max_strength': 4.0,
                        'description': 'Flowering phase formula',
                        'npk': '0-5-4'
                    }
                }
            },
            'Athena': {
                'description': 'Professional grade blended nutrient system',
                'base_nutrients': {
                    'Core': {
                        'type': 'base',
                        'max_strength': 3.0,
                        'description': 'Complete nutrient solution',
                        'npk': '4-0-1'
                    },
                    'Bloom': {
                        'type': 'bloom',
                        'max_strength': 3.0,
                        'description': 'Flower enhancer',
                        'npk': '0-5-4'
                    }
                }
            },
            'House & Garden': {
                'description': 'Premium Dutch nutrients with specialized additives',
                'base_nutrients': {
                    'Aqua Flakes A': {
                        'type': 'base_a',
                        'max_strength': 3.0,
                        'description': 'Part A base nutrient',
                        'npk': '5-0-3'
                    },
                    'Aqua Flakes B': {
                        'type': 'base_b',
                        'max_strength': 3.0,
                        'description': 'Part B base nutrient',
                        'npk': '1-4-5'
                    }
                }
            },
            'Canna': {
                'description': 'Research-based nutrients optimized for various media',
                'base_nutrients': {
                    'Canna A': {
                        'type': 'base_a',
                        'max_strength': 3.0,
                        'description': 'Part A complete nutrient',
                        'npk': '5-0-1'
                    },
                    'Canna B': {
                        'type': 'base_b',
                        'max_strength': 3.0,
                        'description': 'Part B complete nutrient',
                        'npk': '0-4-2'
                    }
                }
            },
            'Generic': {
                'description': 'Custom nutrient formulations using raw salts',
                'base_nutrients': {
                    'Calcium Nitrate': {
                        'type': 'macro',
                        'max_strength': 1.0,
                        'description': 'Ca(NO3)2 - Primary calcium source',
                        'unit': 'g/L'
                    },
                    'Potassium Nitrate': {
                        'type': 'macro',
                        'max_strength': 0.6,
                        'description': 'KNO3 - Nitrogen and potassium source',
                        'unit': 'g/L'
                    },
                    # ... add more generic compounds ...
                }
            }
        }

    def load_recipes(self):
        """Load saved recipes from session state"""
        if 'saved_recipes' not in st.session_state:
            st.session_state.saved_recipes = {}
        return st.session_state.saved_recipes

    def save_recipe(self, name, recipe_data):
        """Save a new recipe with validation and mixing instructions"""
        try:
            if not name or not recipe_data:
                raise ValueError("Recipe name and data are required")
                
            # Add mixing instructions and metadata
            recipe_data.update({
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'mixing_instructions': self.generate_mixing_instructions(recipe_data),
                'recipe_id': st.session_state.recipe_count + 1
            })
            
            self.recipes[name] = recipe_data
            st.session_state.saved_recipes = self.recipes
            st.session_state.recipe_count += 1
            
            logger.info(f"Recipe saved successfully: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save recipe: {str(e)}")
            return False

    def generate_mixing_instructions(self, recipe_data):
        """Generate comprehensive mixing instructions"""
        try:
            instructions = []
            nutrients = recipe_data.get('nutrients', {})
            
            # Step 1: Environment and Equipment Preparation
            instructions.append({
                'step': 1,
                'title': 'Preparation',
                'description': "Prepare your mixing environment and equipment",
                'tips': [
                    'Clean all mixing equipment thoroughly',
                    'Calibrate pH and EC meters',
                    'Prepare measuring syringes/cups',
                    'Have paper towels ready for spills',
                    'Wear protective gloves if needed'
                ],
                'equipment_needed': [
                    'Clean mixing container',
                    'Measuring syringes/cups',
                    'Stirring tool',
                    'pH meter',
                    'EC/PPM meter',
                    'Thermometer'
                ]
            })
            
            # Step 2: Water Preparation
            instructions.append({
                'step': 2,
                'title': 'Water Preparation',
                'description': f"Fill container with {recipe_data.get('size', 0)} gallons of water at room temperature",
                'tips': [
                    'Use RO or filtered water if possible',
                    'Check water temperature (65-75°F ideal)',
                    'Measure initial EC/PPM of water',
                    'Record initial pH reading',
                    'Let chlorinated water sit for 24h or use dechlorinator'
                ],
                'measurements': {
                    'Target Temperature': '68-72°F',
                    'Starting EC': '<0.1 for RO, <0.5 for tap',
                    'Starting pH': 'Record initial reading'
                }
            })
            
            # Step 3: Initial pH Adjustment
            instructions.append({
                'step': 3,
                'title': 'Initial pH Adjustment',
                'description': "Adjust water pH if needed before adding nutrients",
                'tips': [
                    'Target pH: 5.5-6.0 for initial mix',
                    'Add pH adjusters slowly (1ml at a time)',
                    'Mix thoroughly between additions',
                    'Wait 30 seconds before retesting',
                    'Consider water source (RO vs Tap)'
                ],
                'measurements': {
                    'Target pH': '5.5-6.0',
                    'Wait Time': '30 seconds between adjustments'
                }
            })
            
            # Step 4: Add Silica (if present)
            if any(n.get('type') == 'silica' for n in nutrients.values()):
                silica_nutrients = [n for n in nutrients.items() if n[1].get('type') == 'silica']
                instructions.append({
                    'step': 4,
                    'title': 'Add Silica',
                    'description': "Add silica supplement first and mix thoroughly",
                    'tips': [
                        'Add silica FIRST before other nutrients',
                        'Mix thoroughly for 2 minutes',
                        'Wait 15 minutes before next addition',
                        'Check pH after mixing (silica raises pH)',
                        'Do not mix directly with concentrated nutrients'
                    ],
                    'amounts': {n[0]: f"{n[1]['amount']} {n[1].get('unit', 'ml')}" 
                              for n in silica_nutrients},
                    'wait_time': '15 minutes',
                    'ph_impact': 'Increases pH significantly'
                })
            
            # Step 5: Add CalMag (if present)
            if any(n.get('type') == 'calmag' for n in nutrients.values()):
                calmag_nutrients = [n for n in nutrients.items() if n[1].get('type') == 'calmag']
                instructions.append({
                    'step': 5,
                    'title': 'Add CalMag',
                    'description': "Add calcium/magnesium supplements",
                    'tips': [
                        'Add CalMag before base nutrients',
                        'Mix thoroughly for 1 minute',
                        'Wait 5 minutes before next addition',
                        'Check for any precipitation',
                        'Monitor solution clarity'
                    ],
                    'amounts': {n[0]: f"{n[1]['amount']} {n[1].get('unit', 'ml')}" 
                              for n in calmag_nutrients},
                    'wait_time': '5 minutes',
                    'ph_impact': 'May slightly affect pH'
                })
            
            # Step 6: Add Base Nutrients
            base_nutrients = [n for n in nutrients.items() if n[1].get('type') in ['micro', 'grow', 'bloom']]
            if base_nutrients:
                instructions.append({
                    'step': 6,
                    'title': 'Add Base Nutrients',
                    'description': "Add base nutrients in specific order",
                    'tips': [
                        'Always add in order: Micro → Grow → Bloom',
                        'Mix thoroughly between each addition',
                        'Wait 60 seconds between each nutrient',
                        'Check EC after each addition',
                        'Watch for any reactions or precipitation'
                    ],
                    'sequence': [
                        {'nutrient': 'Micro', 'wait': '60 seconds', 'mix_time': '30 seconds'},
                        {'nutrient': 'Grow', 'wait': '60 seconds', 'mix_time': '30 seconds'},
                        {'nutrient': 'Bloom', 'wait': '60 seconds', 'mix_time': '30 seconds'}
                    ],
                    'amounts': {n[0]: f"{n[1]['amount']} {n[1].get('unit', 'ml')}" 
                              for n in base_nutrients},
                    'target_ec': recipe_data.get('target_ec', 'See feeding chart')
                })
            
            # Step 7: Add Supplements
            supplements = [n for n in nutrients.items() 
                         if n[1].get('type') not in ['micro', 'grow', 'bloom', 'silica', 'calmag']]
            if supplements:
                instructions.append({
                    'step': 7,
                    'title': 'Add Supplements',
                    'description': "Add remaining supplements in optimal order",
                    'tips': [
                        'Add one supplement at a time',
                        'Mix thoroughly between additions',
                        'Monitor EC changes closely',
                        'Watch for any reactions',
                        'Check pH after each addition'
                    ],
                    'recommended_order': [
                        'Root enhancers',
                        'Humic/Fulvic acids',
                        'PK boosters',
                        'Enzymes',
                        'Beneficial bacteria'
                    ],
                    'amounts': {n[0]: f"{n[1]['amount']} {n[1].get('unit', 'ml')}" 
                              for n in supplements},
                    'wait_time': '60 seconds between each'
                })
            
            # Step 8: Final Adjustments
            instructions.append({
                'step': 8,
                'title': 'Final Adjustments',
                'description': "Make final pH and EC adjustments",
                'tips': [
                    'Adjust pH to target range',
                    'Verify final EC/PPM',
                    'Let solution sit for 15 minutes',
                    'Take final readings',
                    'Document all measurements'
                ],
                'target_measurements': {
                    'Final pH': recipe_data.get('target_ph', '5.8-6.2'),
                    'Final EC': recipe_data.get('target_ec', 'See feeding chart'),
                    'Solution Temp': '65-75°F'
                },
                'verification_steps': [
                    'Check solution clarity',
                    'Verify no precipitation',
                    'Confirm all nutrients dissolved',
                    'Record final measurements'
                ]
            })
            
            return instructions
            
        except Exception as e:
            logger.error(f"Failed to generate mixing instructions: {str(e)}")
            return []

    def display_recipe(self, name):
        """Display recipe with detailed mixing instructions"""
        try:
            recipe = self.recipes.get(name)
            if recipe:
                st.subheader(f"Recipe: {name}")
                
                # Display basic info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Size", f"{recipe.get('size', 0)} gallons")
                with col2:
                    st.metric("Strength", f"{recipe.get('strength', 0)}%")
                with col3:
                    st.metric("Growth Stage", recipe.get('growth_stage', 'N/A'))
                
                # Display mixing instructions
                st.subheader("Mixing Instructions")
                for instruction in recipe.get('mixing_instructions', []):
                    with st.expander(f"Step {instruction['step']}: {instruction['title']}"):
                        st.write(instruction['description'])
                        if instruction.get('tips'):
                            st.write("Tips:")
                            for tip in instruction['tips']:
                                st.write(f"• {tip}")
                        if instruction.get('warnings'):
                            st.warning("Warnings:")
                            for warning in instruction['warnings']:
                                st.write(f"⚠️ {warning}")
                
                # Display nutrient amounts
                st.subheader("Nutrient Amounts")
                nutrients = recipe.get('nutrients', {})
                cols = st.columns(3)
                for idx, (nutrient, details) in enumerate(nutrients.items()):
                    with cols[idx % 3]:
                        st.metric(
                            nutrient,
                            f"{details['amount']} {details.get('unit', 'ml')}",
                            help=details.get('description', '')
                        )
                
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to display recipe: {str(e)}")
            return False

    def get_recipe(self, name):
        """Get a specific recipe"""
        return self.recipes.get(name)

    def list_recipes(self):
        """List all saved recipes"""
        return list(self.recipes.keys())

    def delete_recipe(self, name):
        """Delete a recipe"""
        if name in self.recipes:
            del self.recipes[name]
            st.session_state.saved_recipes = self.recipes
            return True
        return False

    def get_all_strains(self):
        """Get list of all strains used in recipes"""
        try:
            strains = set()
            for recipe in self.recipes.values():
                if 'strain' in recipe:
                    strains.add(recipe['strain'])
            return sorted(list(strains))
        except Exception as e:
            logger.error(f"Failed to get strains: {str(e)}")
            return []

    def get_all_tags(self):
        """Get list of all tags used in recipes"""
        try:
            tags = set()
            for recipe in self.recipes.values():
                if 'tags' in recipe:
                    tags.update(recipe.get('tags', []))
            return sorted(list(tags))
        except Exception as e:
            logger.error(f"Failed to get tags: {str(e)}")
            return []

    def get_recipe_history(self, strain=None, growth_phase=None, tags=None):
        """Get filtered recipe history"""
        try:
            filtered_recipes = []
            for name, recipe in self.recipes.items():
                # Apply filters
                if strain and recipe.get('strain') != strain:
                    continue
                if growth_phase and recipe.get('growth_phase') != growth_phase:
                    continue
                if tags and not all(tag in recipe.get('tags', []) for tag in tags):
                    continue
                
                # Add recipe to filtered list with name
                recipe_copy = recipe.copy()
                recipe_copy['name'] = name
                filtered_recipes.append(recipe_copy)
            
            # Sort by creation date
            return sorted(filtered_recipes, 
                        key=lambda x: x.get('created_at', ''), 
                        reverse=True)
        except Exception as e:
            logger.error(f"Failed to get recipe history: {str(e)}")
            return []

    def save_recipe_with_metadata(self, name, recipe_data, strain=None, tags=None):
        """Save recipe with additional metadata"""
        try:
            if not name or not recipe_data:
                raise ValueError("Recipe name and data are required")
            
            # Add metadata
            recipe_data.update({
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'recipe_id': st.session_state.recipe_count + 1,
                'strain': strain,
                'tags': tags or [],
                'mixing_instructions': self.generate_mixing_instructions(recipe_data),
                'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'version': 1,
                'results': []
            })
            
            self.recipes[name] = recipe_data
            st.session_state.saved_recipes = self.recipes
            st.session_state.recipe_count += 1
            
            logger.info(f"Recipe saved successfully: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save recipe: {str(e)}")
            return False

    def add_recipe_result(self, name, result_data):
        """Add result data to existing recipe"""
        try:
            if name not in self.recipes:
                raise ValueError(f"Recipe '{name}' not found")
            
            if 'results' not in self.recipes[name]:
                self.recipes[name]['results'] = []
            
            result_data['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.recipes[name]['results'].append(result_data)
            st.session_state.saved_recipes = self.recipes
            
            logger.info(f"Result added to recipe: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add recipe result: {str(e)}")
            return False

    def export_recipe(self, name):
        """Export recipe as JSON"""
        try:
            if name not in self.recipes:
                raise ValueError(f"Recipe '{name}' not found")
            
            recipe_data = self.recipes[name].copy()
            recipe_data['exported_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return json.dumps(recipe_data, indent=2)
        except Exception as e:
            logger.error(f"Failed to export recipe: {str(e)}")
            return None

    def import_recipe(self, name, recipe_json):
        """Import recipe from JSON"""
        try:
            recipe_data = json.loads(recipe_json)
            recipe_data['imported_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            recipe_data['version'] = recipe_data.get('version', 1)
            
            return self.save_recipe(name, recipe_data)
        except Exception as e:
            logger.error(f"Failed to import recipe: {str(e)}")
            return False

    def duplicate_recipe(self, name, new_name):
        """Duplicate an existing recipe"""
        try:
            if name not in self.recipes:
                raise ValueError(f"Recipe '{name}' not found")
            
            recipe_data = self.recipes[name].copy()
            recipe_data['duplicated_from'] = name
            recipe_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            recipe_data['version'] = 1
            recipe_data['results'] = []  # Don't copy results
            
            return self.save_recipe(new_name, recipe_data)
        except Exception as e:
            logger.error(f"Failed to duplicate recipe: {str(e)}")
            return False

class NutrientCalculatorUI:
    def __init__(self):
        # Initialize Streamlit session state first
        if 'saved_recipes' not in st.session_state:
            st.session_state.saved_recipes = {}
            st.session_state.recipe_count = 0
        
        self.debugger = create_debugger()
        
        # Initialize data first
        self.load_data()
        
        # Initialize RecipeManager
        try:
            self.recipe_manager = RecipeManager()
            logger.info("Recipe Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Recipe Manager: {str(e)}")
            st.error("Failed to initialize Recipe Manager")
            self.recipe_manager = None

    def load_data(self):
        """Load nutrient profiles and strain data"""
        try:
            # Initialize nutrient lines with detailed information
            self.nutrient_lines = {
                'General Hydroponics': {
                    'base_nutrients': {
                        'Flora Micro': {
                            'type': 'micro',
                            'max_strength': 4.0,  # ml per gallon
                            'npk': '5-0-1',
                            'description': 'Concentrated micronutrients and calcium',
                            'when_to_use': 'Throughout entire grow cycle',
                            'benefits': ['Essential micronutrients', 'Calcium source', 'Iron source'],
                            'cautions': ['Add before Flora Grow and Flora Bloom', 'Can stain', 'Required for all stages'],
                            'ec_impact': 'Medium',
                            'ph_impact': 'Slight decrease'
                        },
                        'Flora Grow': {
                            'type': 'grow',
                            'max_strength': 4.0,  # ml per gallon
                            'npk': '2-1-6',
                            'description': 'Promotes structural and vegetative growth',
                            'when_to_use': 'Heavy in veg, reduced in flower',
                            'benefits': ['Promotes leaf growth', 'Enhances node spacing', 'Builds structure'],
                            'cautions': ['Add after Flora Micro', 'Reduce during flowering'],
                            'ec_impact': 'Medium',
                            'ph_impact': 'Slight decrease'
                        },
                        'Flora Bloom': {
                            'type': 'bloom',
                            'max_strength': 4.0,  # ml per gallon
                            'npk': '0-5-4',
                            'description': 'Promotes flower development and fruiting',
                            'when_to_use': 'During flowering phase',
                            'benefits': ['Enhances flower development', 'Improves yield', 'Boosts essential oils'],
                            'cautions': ['Add last of base nutrients', 'Monitor EC levels']
                        }
                    },
                    'supplements': {
                        'CaliMagic': {
                            'type': 'calmag',
                            'max_strength': 5.0,  # ml per gallon
                            'description': 'GH\'s calcium and magnesium supplement',
                            'when_to_use': 'Throughout grow cycle, essential with RO water',
                            'benefits': [
                                'Prevents calcium deficiency',
                                'Strengthens cell walls',
                                'Improves nutrient uptake',
                                'Prevents magnesium deficiency'
                            ],
                            'npk': '1-0-0',
                            'contains': {'Ca': '5%', 'Mg': '1.5%'},
                            'cautions': ['Check water hardness first', 'Can raise pH']
                        },
                        'Rapid Start': {
                            'type': 'root',
                            'max_strength': 2.0,  # ml per gallon
                            'description': 'GH\'s root development enhancer',
                            'when_to_use': 'Early growth and transplanting',
                            'benefits': [
                                'Accelerates root development',
                                'Improves nutrient uptake',
                                'Reduces transplant shock',
                                'Enhances stress tolerance'
                            ],
                            'contains': {'Vitamins': 'B1, B2', 'Hormones': 'IBA, NAA'},
                            'cautions': ['Reduce after established roots', 'Monitor pH']
                        },
                        'Diamond Nectar': {
                            'type': 'humic',
                            'max_strength': 2.0,  # ml per gallon
                            'description': 'GH\'s premium humic acid supplement',
                            'when_to_use': 'Throughout grow cycle',
                            'benefits': [
                                'Improves nutrient uptake',
                                'Enhances root development',
                                'Increases chelation',
                                'Improves soil structure'
                            ],
                            'contains': {'Humic acid': '6%', 'Fulvic acid': '3%'},
                            'cautions': ['Can darken solution', 'Monitor pH']
                        },
                        'Armor Si': {
                            'type': 'silica',
                            'max_strength': 2.0,  # ml per gallon
                            'description': 'GH\'s silica supplement',
                            'when_to_use': 'Throughout grow cycle',
                            'benefits': [
                                'Strengthens cell walls',
                                'Improves heat tolerance',
                                'Enhances pest resistance',
                                'Supports heavy flowers'
                            ],
                            'contains': {'Si': '0.5%'},
                            'cautions': [
                                'Must be added FIRST to nutrient solution',
                                'Raises pH significantly',
                                'Don\'t mix directly with concentrated nutrients'
                            ]
                        },
                        'Liquid KoolBloom': {
                            'type': 'pk_boost',
                            'max_strength': 2.5,  # ml per gallon
                            'description': 'GH\'s liquid P-K booster',
                            'when_to_use': 'Early to mid flowering',
                            'benefits': [
                                'Enhances flower formation',
                                'Improves flower size',
                                'Boosts essential oil production'
                            ],
                            'npk': '0-10-10',
                            'cautions': ['Monitor EC', 'Can build up salts']
                        },
                        'Dry KoolBloom': {
                            'type': 'ripening',
                            'max_strength': 1.5,  # grams per gallon
                            'description': 'GH\'s flowering finisher powder',
                            'when_to_use': 'Last 2-3 weeks of flower',
                            'benefits': [
                                'Triggers ripening',
                                'Increases resin production',
                                'Enhances flower density',
                                'Improves essential oil content'
                            ],
                            'npk': '0-27-27',
                            'cautions': [
                                'Use only in late flower',
                                'Monitor EC carefully',
                                'Can cause lockout if overused',
                                'Dissolve completely before adding other nutrients'
                            ]
                        },
                        'Floralicious Plus': {
                            'type': 'enzyme',
                            'max_strength': 1.0,  # ml per gallon
                            'description': 'GH\'s organic bioactivator',
                            'when_to_use': 'Throughout grow cycle',
                            'benefits': [
                                'Enhances nutrient uptake',
                                'Improves flavor profiles',
                                'Boosts terpene production',
                                'Supports beneficial microbes'
                            ],
                            'contains': {
                                'Enzymes': 'Multiple',
                                'Amino acids': 'Complete profile',
                                'Vitamins': 'B1, B2, B6, B12'
                            },
                            'cautions': [
                                'Shake well before use',
                                'Can cloud reservoir',
                                'Add last to nutrient solution'
                            ]
                        },
                        'Florablend': {
                            'type': 'biostimulant',
                            'max_strength': 2.0,  # ml per gallon
                            'description': 'GH\'s organic vegan supplement',
                            'when_to_use': 'Throughout grow cycle',
                            'benefits': [
                                'Enhances nutrient uptake',
                                'Improves plant vigor',
                                'Supports beneficial microbes',
                                'Adds trace elements'
                            ],
                            'contains': {
                                'Seaweed': 'Multiple species',
                                'Minerals': 'Trace elements',
                                'Vitamins': 'Natural blend'
                            },
                            'cautions': [
                                'Shake well before use',
                                'Can settle in reservoir',
                                'Add after base nutrients'
                            ]
                        }
                    }
                }
                # Can add other nutrient lines here (Advanced Nutrients, Fox Farm, etc.)
            }
            logger.info("Nutrient data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            raise

    def apply_custom_styles(self):
        """Apply custom CSS styles"""
        try:
            st.markdown("""
                <style>
                .stButton>button {
                    width: 100%;
                }
                .stSelectbox {
                    margin-bottom: 1rem;
                }
                </style>
                """, unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"Failed to apply custom styles: {str(e)}")

    def load_strain_data(self):
        """Load strain database"""
        try:
            # Initialize with default strains if no database exists
            self.strain_database = {
                'Default': {
                    'feeding_type': 'Medium Feeders',
                    'flowering_time': '8-9 weeks',
                    'nutrient_sensitivity': 'Medium'
                }
            }
            logger.info("Strain data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load strain data: {str(e)}")
            raise

    def render(self):
        """Main render method"""
        try:
            st.title("Nutrient Calculator")
            
            # Create tabs for different sections
            tab1, tab2, tab3 = st.tabs(["Calculator", "Recipe Library", "Analysis"])
            
            with tab1:
                self.render_calculator()
            
            with tab2:
                if self.recipe_manager:
                    self.render_recipe_library()
                else:
                    st.error("Recipe Manager not available")
            
            with tab3:
                self.render_analysis()
                
        except Exception as e:
            logger.error(f"Failed to render UI: {str(e)}")
            st.error(f"Failed to render UI: {str(e)}")

    def render_recipe_library(self):
        """Render the recipe library section"""
        try:
            st.subheader("Recipe Library")
            recipes = self.recipe_manager.list_recipes()
            
            if recipes:
                for recipe_name in recipes:
                    with st.expander(recipe_name):
                        recipe = self.recipe_manager.get_recipe(recipe_name)
                        if recipe:
                            st.json(recipe)
                            if st.button(f"Load {recipe_name}"):
                                # Load recipe into calculator
                                pass
            else:
                st.info("No saved recipes yet")
                
        except Exception as e:
            logger.error(f"Failed to render recipe library: {str(e)}")
            st.error("Failed to render recipe library")

    def get_strain_ec_range(self, strain_info, growth_stage):
        """Get EC range based on strain and growth stage"""
        stage_mapping = {
            'Seedling': ('veg', 0.5),
            'Early Veg': ('veg', 0.8),
            'Late Veg': ('veg', 1.0),
            'Pre-Flower': ('flower', 0.9),
            'Early Flower': ('flower', 1.0),
            'Mid Flower': ('flower', 1.0),
            'Late Flower': ('flower', 0.8),
            'Flush': ('flower', 0.0)
        }
        
        period, multiplier = stage_mapping[growth_stage]
        base_range = strain_info['optimal_ec'][period]
        
        return [round(base_range[0] * multiplier, 1), 
                round(base_range[1] * multiplier, 1)]

    def get_default_strength(self, growth_stage, strain_info):
        """Calculate default strength based on strain and stage"""
        base_strength = {
            'Light': 0.8,
            'Medium': 1.0,
            'Heavy': 1.2
        }.get(strain_info['feeding_type'], 1.0)
        
        stage_multiplier = {
            'Seedling': 0.25,
            'Early Veg': 0.5,
            'Late Veg': 0.75,
            'Pre-Flower': 0.8,
            'Early Flower': 0.9,
            'Mid Flower': 1.0,
            'Late Flower': 0.8,
            'Flush': 0.0
        }.get(growth_stage, 1.0)
        
        return min(100, int(100 * base_strength * stage_multiplier))

    def format_growth_characteristics(self, characteristics):
        """Format growth characteristics for display"""
        formatted = []
        for key, value in characteristics.items():
            formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
        return "\n".join(formatted)

    def display_brand_calculations(self, line, stage, strain, size, strength):
        """Display nutrient calculations and mixing instructions for brand products"""
        st.header("Nutrient Mix Recipe")
        
        # Get nutrient profiles
        base_nutrients = self.nutrient_lines[line]['base_nutrients']
        supplements = self.nutrient_lines[line]['supplements']
        strain_multiplier = self.strain_profiles[strain]['nutrient_multiplier']
        
        # Display calculations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Base Nutrients")
            for name, details in base_nutrients.items():
                amount = details['max_strength'] * size * (strength/100) * strain_multiplier
                st.metric(
                    name,
                    f"{amount:.1f} ml",
                    f"{amount/size:.1f} ml/gal"
                )
        
        with col2:
            st.subheader("Supplements")
            for name, details in supplements.items():
                amount = details['max_strength'] * size * (strength/100) * strain_multiplier
                st.metric(
                    name,
                    f"{amount:.1f} ml",
                    f"{amount/size:.1f} ml/gal"
                )
        
        # Mixing instructions
        st.header("Mixing Instructions")
        self.display_mixing_instructions()
        
        # Target ranges
        st.header("Target Ranges")
        self.display_target_ranges(stage, strain)

    def display_generic_calculations(self, size, strength, selected_nutrients):
        """Display calculations for generic nutrients"""
        st.subheader("Calculated Amounts")
        
        # Create DataFrame for results
        results = []
        
        # Calculate amounts for selected nutrients
        for nutrient, is_selected in selected_nutrients.items():
            if is_selected:  # Only calculate for selected nutrients
                if nutrient in self.nutrient_lines['General Hydroponics']['base_nutrients']:
                    details = self.nutrient_lines['General Hydroponics']['base_nutrients'][nutrient]
                    amount = details['max_strength'] * size * (strength/100)
                    results.append({
                        'Nutrient': nutrient,
                        'Amount (ml)': f"{amount:.1f}",
                        'ml/L': f"{amount/size:.2f}"
                    })
                elif nutrient in self.nutrient_lines['General Hydroponics']['supplements']:
                    details = self.nutrient_lines['General Hydroponics']['supplements'][nutrient]
                    amount = details['max_strength'] * size * (strength/100)
                    results.append({
                        'Nutrient': nutrient,
                        'Amount (ml)': f"{amount:.1f}",
                        'ml/L': f"{amount/size:.2f}"
                    })
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df)
        else:
            st.info("Select nutrients to see calculations")

    def calculate_nutrient_amounts(self, volume_liters, stage, strain_type, nutrient_line):
        """Calculate nutrient amounts based on selected parameters"""
        # Get base multiplier from strain profile
        base_multiplier = self.strain_profiles[strain_type]['nutrient_multiplier']
        
        # Get nutrients from selected line
        base_nutrients = self.nutrient_lines[nutrient_line]['base_nutrients']
        supplements = self.nutrient_lines[nutrient_line]['supplements']
        
        # Stage-based multipliers
        stage_multipliers = {
            "Seedling": 0.25,
            "Vegetative": 1.0,
            "Early Flower": 1.0,
            "Mid Flower": 1.2,
            "Late Flower": 1.0
        }
        
        # Calculate amounts
        base_amounts = {}
        for nutrient, info in base_nutrients.items():
            amount = (info['max_strength'] * 
                     stage_multipliers[stage] * 
                     base_multiplier * 
                     volume_liters)
            base_amounts[nutrient] = round(amount, 1)
            
        supplement_amounts = {}
        for supp, info in supplements.items():
            amount = (info['max_strength'] * 
                     stage_multipliers[stage] * 
                     base_multiplier * 
                     volume_liters)
            supplement_amounts[supp] = round(amount, 1)
            
        return base_amounts, supplement_amounts

    def display_mixing_instructions(self):
        """Display mixing instructions"""
        st.markdown("""
        1. **Prepare Water**
           - Fill reservoir to 75% capacity
           - Ensure proper temperature (65-75°F)
           - Allow chlorine to dissipate if using tap water
        
        2. **Add Silicon** (if using)
           - Add silicon first
           - Mix thoroughly
           - Wait 15 minutes
        
        3. **Add CalMag** (if using)
           - Add CalMag second
           - Mix thoroughly
           - Wait 15 minutes
        
        4. **Add Base Nutrients**
           - Add in this order:
             1. Micro
             2. Grow
             3. Bloom
           - Mix thoroughly between each
        
        5. **Add Supplements**
           - Add remaining supplements
           - Mix thoroughly between each
        
        6. **Final Steps**
           - Top off reservoir
           - Check EC
           - Adjust pH
           - Record measurements
        """)

    def display_target_ranges(self, stage, strain):
        """Display detailed target ranges with charts"""
        strain_data = self.strain_profiles[strain]
        
        st.header("Target Ranges & Analysis")
        
        # Create tabs for different metrics
        tabs = st.tabs(["EC/PPM", "pH", "Temperature", "VPD"])
        
        with tabs[0]:
            target_ec = self.get_target_ec(stage, strain)
            
            # Create EC gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = target_ec,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Target EC (mS/cm)"},
                gauge = {
                    'axis': {'range': [0, 3]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 1], 'color': "lightgray"},
                        {'range': [1, 2], 'color': "gray"},
                        {'range': [2, 3], 'color': "darkgray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': target_ec
                    }
                }
            ))
            st.plotly_chart(fig)
            
            # Add PPM conversion
            st.info(f"""
            PPM Conversions (approximate):
            - 500 scale: {target_ec * 500:.0f} PPM
            - 700 scale: {target_ec * 700:.0f} PPM
            """)
        
        with tabs[1]:
            # pH Range
            ph_range = strain_data['recommended_ph']
            st.metric("Target pH Range", f"{ph_range[0]} - {ph_range[1]}")
            
            # Create pH gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = (ph_range[0] + ph_range[1]) / 2,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Target pH"},
                gauge = {
                    'axis': {'range': [0, 14]},
                    'bar': {'color': "green"},
                    'steps': [
                        {'range': [0, 5], 'color': "red"},
                        {'range': [5, 6], 'color': "yellow"},
                        {'range': [6, 7], 'color': "green"},
                        {'range': [7, 14], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': (ph_range[0] + ph_range[1]) / 2
                    }
                }
            ))
            st.plotly_chart(fig)
        
        with tabs[2]:
            # Temperature ranges
            st.metric("Target Temperature", "72-78°F / 22-26°C")
            st.markdown("""
            **Temperature Guidelines:**
            - Day: 75-80°F (24-27°C)
            - Night: 65-75°F (18-24°C)
            - Root Zone: 68-72°F (20-22°C)
            """)
        
        with tabs[3]:
            # VPD Chart
            st.markdown("""
            **Vapor Pressure Deficit (VPD) Targets:**
            - Clones/Seedlings: 0.4-0.8 kPa
            - Vegetative: 0.8-1.2 kPa
            - Early Flower: 1.0-1.4 kPa
            - Late Flower: 1.2-1.6 kPa
            """)
            
            # Add basic VPD chart
            vpd_data = pd.DataFrame({
                'Temperature (°F)': list(range(65, 85, 5)),
                '40% RH': [0.8, 1.0, 1.2, 1.4],
                '50% RH': [0.6, 0.8, 1.0, 1.2],
                '60% RH': [0.4, 0.6, 0.8, 1.0]
            })
            
            st.line_chart(vpd_data.set_index('Temperature (°F)'))

    def calculate_nutrient_ratios(self, npk_values, stage):
        """Calculate optimal nutrient ratios based on growth stage"""
        ratios = {
            "Seedling": {"N": 1, "P": 0.5, "K": 1},
            "Vegetative": {"N": 3, "P": 1, "K": 2},
            "Early Flower": {"N": 2, "P": 2, "K": 3},
            "Mid Flower": {"N": 1, "P": 2, "K": 3},
            "Late Flower": {"N": 0.5, "P": 2, "K": 4},
            "Flush": {"N": 0, "P": 0, "K": 0}
        }
        
        stage_ratio = ratios[stage]
        return {
            "N": npk_values["N"] * stage_ratio["N"],
            "P": npk_values["P"] * stage_ratio["P"],
            "K": npk_values["K"] * stage_ratio["K"]
        }

    def save_recipe(self, recipe_data):
        """Save nutrient recipe to JSON file"""
        try:
            recipes_file = Path("saved_recipes.json")
            existing_recipes = []
            
            if recipes_file.exists():
                with open(recipes_file, 'r') as f:
                    existing_recipes = json.load(f)
            
            # Add timestamp and name to recipe
            recipe_data['timestamp'] = datetime.now().isoformat()
            recipe_data['name'] = st.text_input("Recipe Name", 
                                              value=f"Recipe {len(existing_recipes) + 1}")
            
            existing_recipes.append(recipe_data)
            
            with open(recipes_file, 'w') as f:
                json.dump(existing_recipes, f, indent=4)
                
            st.success("Recipe saved successfully!")
            
        except Exception as e:
            st.error(f"Error saving recipe: {str(e)}")

    def load_recipe(self):
        """Load saved nutrient recipe"""
        try:
            recipes_file = Path("saved_recipes.json")
            if recipes_file.exists():
                with open(recipes_file, 'r') as f:
                    recipes = json.load(f)
                
                recipe_names = [r['name'] for r in recipes]
                selected_recipe = st.selectbox("Load Saved Recipe", recipe_names)
                
                if selected_recipe:
                    recipe = next(r for r in recipes if r['name'] == selected_recipe)
                    return recipe
                    
        except Exception as e:
            st.error(f"Error loading recipe: {str(e)}")
            return None

    def display_mixing_instructions(self, recipe_data):
        """Display detailed mixing instructions with timing and tips"""
        st.header("Detailed Mixing Instructions")
        
        # Calculate total mix time
        total_time = 0
        
        with st.expander("1. Water Preparation", expanded=True):
            st.markdown("""
            - Fill reservoir to 75% capacity
            - Ensure water temperature is between 65-75°F (18-24°C)
            - If using tap water:
                - Let stand for 24 hours to dechlorinate OR
                - Use dechlorinator according to product instructions
            - Test and record starting pH and EC
            """)
            total_time += 5
            st.info(f"⏱️ Time: 5 minutes | Running Total: {total_time} minutes")

        with st.expander("2. Silicon Addition (If Using)", expanded=True):
            st.markdown("""
            - Add silicon product first
            - Mix thoroughly for 2-3 minutes
            - **Critical**: Wait 15 minutes before next addition
            - Silicon can react with other nutrients if not properly mixed
            """)
            total_time += 20
            st.info(f"⏱️ Time: 20 minutes | Running Total: {total_time} minutes")

        with st.expander("3. CalMag Addition (If Using)", expanded=True):
            st.markdown("""
            - Add CalMag or calcium/magnesium supplement
            - Mix thoroughly for 2-3 minutes
            - Wait 10 minutes before next addition
            - Monitor for any precipitation
            """)
            total_time += 15
            st.info(f"⏱️ Time: 15 minutes | Running Total: {total_time} minutes")

        with st.expander("4. Base Nutrient Addition", expanded=True):
            st.markdown("""
            1. **Micro** nutrients first:
                - Add slowly while stirring
                - Mix for 2-3 minutes
            2. **Grow** nutrients second:
                - Add slowly while stirring
                - Mix for 2-3 minutes
            3. **Bloom** nutrients last:
                - Add slowly while stirring
                - Mix for 2-3 minutes
            
            ⚠️ **Important**: Always follow this order to prevent nutrient lockout
            """)
            total_time += 15
            st.info(f"⏱️ Time: 15 minutes | Running Total: {total_time} minutes")

        with st.expander("5. Supplement Addition", expanded=True):
            st.markdown("""
            Add supplements in this order:
            1. Humic/Fulvic acids
            2. Enzymes
            3. Beneficial bacteria
            4. Mycorrhizae
            
            - Mix for 1-2 minutes between each addition
            - Some supplements may reduce effectiveness if mixed together
            """)
            total_time += 15
            st.info(f"⏱️ Time: 15 minutes | Running Total: {total_time} minutes")

        with st.expander("6. Final Steps", expanded=True):
            st.markdown("""
            1. Top off reservoir to final volume
            2. Final mixing for 5 minutes
            3. Test and record:
                - EC/PPM
                - pH
                - Temperature
            4. Adjust pH if needed:
                - Add pH up/down in small increments
                - Mix and wait 2-3 minutes between adjustments
            5. Document final measurements
            """)
            total_time += 10
            st.info(f"⏱️ Time: 10 minutes | Running Total: {total_time} minutes")

        st.success(f"Total Mix Time: {total_time} minutes")
        
        # Add recipe saving option
        if st.button("Save This Recipe"):
            self.save_recipe(recipe_data)

    def get_target_ec(self, stage, strain_type):
        """Get target EC range based on growth stage and strain type"""
        base_ec = {
            "Seedling": 0.5,
            "Vegetative": 1.2,
            "Early Flower": 1.6,
            "Mid Flower": 1.8,
            "Late Flower": 1.4
        }
        
        # Adjust based on strain type
        multipliers = {
            "Heavy Feeders": 1.2,
            "Medium Feeders": 1.0,
            "Light Feeders": 0.8
        }
        
        return base_ec[stage] * multipliers[strain_type]

    def get_product_details(self, line, product):
        """Get detailed information about a nutrient product"""
        product_details = {
            'General Hydroponics': {
                'Flora Micro': {
                    'description': 'Concentrated micronutrients and secondary minerals. Contains nitrogen and calcium.',
                    'usage_notes': 'Always add first to prevent nutrient lockout. Mix well before adding other nutrients.',
                    'key_elements': 'N, Ca, Mg, Fe, Mn, Zn, B, Cu, Mo',
                    'features': [
                        'Highly concentrated formula',
                        'Essential for photosynthesis',
                        'Supports vegetative and flowering growth',
                        'Contains stabilized micronutrients'
                    ]
                },
                'Flora Grow': {
                    'description': 'Nitrogen-rich formula optimized for vegetative growth.',
                    'usage_notes': 'Add after Micro. Increase during vegetative phase, reduce in flowering.',
                    'key_elements': 'N, K, P, B, Mn',
                    'features': [
                        'Promotes vigorous growth',
                        'Supports strong stem development',
                        'Enhances chlorophyll production',
                        'Balanced NPK ratio for vegetation'
                    ]
                },
                'Flora Bloom': {
                    'description': 'Phosphorus and potassium rich formula for flowering phase.',
                    'usage_notes': 'Add last in mixing order. Increase during flowering phase.',
                    'key_elements': 'P, K, Mg, S',
                    'features': [
                        'Promotes flower development',
                        'Enhances essential oil production',
                        'Supports fruit/flower maturation',
                        'Improves trichome development'
                    ]
                },
                'CaliMagic': {
                    'description': 'Calcium and magnesium supplement with iron.',
                    'usage_notes': 'Add early in mixing process, after silica but before base nutrients.',
                    'key_elements': 'Ca, Mg, Fe',
                    'features': [
                        'Prevents calcium deficiency',
                        'Strengthens cell walls',
                        'Improves nutrient uptake',
                        'Essential for LED grows'
                    ]
                },
                'Armor Si': {
                    'description': 'Potassium silicate supplement for stronger plants.',
                    'usage_notes': 'Always add first to fresh water. Wait 15 minutes before other nutrients.',
                    'key_elements': 'Si, K',
                    'features': [
                        'Strengthens cell walls',
                        'Improves heat tolerance',
                        'Enhances pest resistance',
                        'Supports stronger stems'
                    ]
                }
            },
            'Advanced Nutrients': {
                'Micro': {
                    'description': 'pH Perfect micronutrient formula with chelated elements.',
                    'usage_notes': 'Part of 3-part base system. Add first in mixing order.',
                    'key_elements': 'N, Ca, Mg, Fe, Mn, Zn, B, Cu, Mo',
                    'features': [
                        'pH Perfect Technology',
                        'Chelated micronutrients',
                        'Enhanced bioavailability',
                        'Supports all growth phases'
                    ]
                },
                'Big Bud': {
                    'description': 'Phosphorus and potassium bloom booster with L-amino acids.',
                    'usage_notes': 'Use during mid to late flowering. Compatible with all base nutrients.',
                    'key_elements': 'P, K, Mg, L-amino acids',
                    'features': [
                        'Increases bud size',
                        'Enhances essential oil production',
                        'Improves flower density',
                        'Contains L-amino acids'
                    ]
                }
            }
            # Add more product details as needed
        }
        
        try:
            return product_details[line][product]
        except KeyError:
            return {
                'description': 'Detailed information not available.',
                'usage_notes': 'Follow manufacturer recommendations.',
                'key_elements': 'Information not available',
                'features': ['Information not available']
            }

    def display_product_info(self, line, product):
        """Display detailed product information in the UI"""
        details = self.get_product_details(line, product)
        
        with st.expander(f"ℹ️ {product} Details"):
            st.markdown(f"**Description**\n{details['description']}")
            
            st.markdown("**Key Elements**")
            st.code(details['key_elements'])
            
            st.markdown("**Usage Notes**")
            st.info(details['usage_notes'])
            
            st.markdown("**Key Features**")
            for feature in details['features']:
                st.markdown(f"• {feature}")

    def calculate_combined_nutrients(self, size, strength, selected_nutrients, growth_stage):
        """Calculate combined nutrients including both brand and generic products"""
        results = []
        total_ec = 0
        total_n = 0
        total_p = 0
        total_k = 0
        
        # Calculate brand nutrients
        if selected_nutrients.get('brand_nutrients'):
            brand = selected_nutrients['brand_nutrients']
            base_amounts, supplement_amounts = self.calculate_nutrient_amounts(
                size, 
                growth_stage,
                brand.get('strain_type', 'Medium Feeders'),
                brand.get('nutrient_line', 'General Hydroponics')
            )
            
            # Add base nutrients to results
            for nutrient, amount in base_amounts.items():
                details = self.nutrient_lines[brand['nutrient_line']]['base_nutrients'][nutrient]
                results.append({
                    'Nutrient': f"{brand['nutrient_line']} {nutrient}",
                    'Amount (ml)': f"{amount:.1f}",
                    'ml/L': f"{amount/size:.2f}",
                    'Type': 'Brand Base',
                    'EC Impact': details.get('ec_impact', 0.2)
                })
                total_ec += details.get('ec_impact', 0.2) * (amount/size)
                
                # Track NPK
                if 'npk' in details:
                    n, p, k = map(float, details['npk'].split('-'))
                    total_n += n * (amount/size)
                    total_p += p * (amount/size)
                    total_k += k * (amount/size)
            
            # Add supplements to results
            for supp, amount in supplement_amounts.items():
                details = self.nutrient_lines[brand['nutrient_line']]['supplements'][supp]
                results.append({
                    'Nutrient': f"{brand['nutrient_line']} {supp}",
                    'Amount (ml)': f"{amount:.1f}",
                    'ml/L': f"{amount/size:.2f}",
                    'Type': 'Brand Supplement',
                    'EC Impact': details.get('ec_impact', 0.1)
                })
                total_ec += details.get('ec_impact', 0.1) * (amount/size)
        
        # Calculate generic compounds
        generic_compounds = {
            'Calcium Nitrate': {'ec_impact': 0.12, 'npk': '15.5-0-0'},
            'Potassium Nitrate': {'ec_impact': 0.13, 'npk': '13-0-46'},
            'Magnesium Sulfate': {'ec_impact': 0.06, 'npk': '0-0-0'},
            'Monopotassium Phosphate': {'ec_impact': 0.08, 'npk': '0-52-34'},
            'Iron DTPA': {'ec_impact': 0.02, 'npk': '0-0-0'},
            'Manganese EDTA': {'ec_impact': 0.01, 'npk': '0-0-0'},
            'Zinc EDTA': {'ec_impact': 0.01, 'npk': '0-0-0'},
            'Boric Acid': {'ec_impact': 0.01, 'npk': '0-0-0'},
            'Copper EDTA': {'ec_impact': 0.01, 'npk': '0-0-0'},
            'Sodium Molybdate': {'ec_impact': 0.01, 'npk': '0-0-0'}
        }
        
        for compound, is_selected in selected_nutrients.get('generic_compounds', {}).items():
            if is_selected and compound in generic_compounds:
                # Calculate amount based on standard rates
                amount = size * (strength/100) * generic_compounds[compound]['ec_impact'] * 10
                results.append({
                    'Nutrient': compound,
                    'Amount (g)': f"{amount:.1f}",
                    'g/L': f"{amount/size:.3f}",
                    'Type': 'Generic',
                    'EC Impact': generic_compounds[compound]['ec_impact']
                })
                total_ec += generic_compounds[compound]['ec_impact'] * (amount/size)
                
                # Track NPK for generic compounds
                if 'npk' in generic_compounds[compound]:
                    n, p, k = map(float, generic_compounds[compound]['npk'].split('-'))
                    total_n += n * (amount/size)
                    total_p += p * (amount/size)
                    total_k += k * (amount/size)
        
        # Add totals and analysis
        analysis = {
            'Total EC': f"{total_ec:.2f}",
            'Total N': f"{total_n:.1f}",
            'Total P': f"{total_p:.1f}",
            'Total K': f"{total_k:.1f}",
            'Target EC Range': self.get_target_ec_range(growth_stage),
            'NPK Ratio': f"{total_n:.1f}-{total_p:.1f}-{total_k:.1f}"
        }
        
        return results, analysis

    def get_target_ec_range(self, growth_stage):
        """Get target EC range based on growth stage"""
        ranges = {
            'Seedling': '0.4-0.8',
            'Early Veg': '0.8-1.2',
            'Late Veg': '1.2-1.6',
            'Pre-Flower': '1.4-1.8',
            'Early Flower': '1.6-2.0',
            'Mid Flower': '1.8-2.2',
            'Late Flower': '1.4-1.8',
            'Flush': '0.0-0.2'
        }
        return ranges.get(growth_stage, '1.0-1.4')

    def display_nutrient_analysis(self, analysis):
        """Display detailed nutrient analysis"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Solution Analysis")
            st.metric("Total EC", analysis['Total EC'])
            st.metric("NPK Ratio", analysis['NPK Ratio'])
            
            # Create EC gauge
            target_range = analysis['Target EC Range'].split('-')
            target_min, target_max = map(float, target_range)
            current_ec = float(analysis['Total EC'])
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = current_ec,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "EC Level"},
                gauge = {
                    'axis': {'range': [0, 3]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, target_min], 'color': "lightgray"},
                        {'range': [target_min, target_max], 'color': "green"},
                        {'range': [target_max, 3], 'color': "lightgray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': current_ec
                    }
                }
            ))
            st.plotly_chart(fig)
        
        with col2:
            st.subheader("Nutrient Balance")
            # Create NPK bar chart
            npk_data = {
                'Nutrient': ['N', 'P', 'K'],
                'Value': [
                    float(analysis['Total N']),
                    float(analysis['Total P']),
                    float(analysis['Total K'])
                ]
            }
            fig = px.bar(npk_data, x='Nutrient', y='Value', title='NPK Distribution')
            st.plotly_chart(fig)

    def calculate_generic_nutrients(self, size, strength, selected_compounds, growth_stage):
        """Calculate amounts for generic compounds"""
        results = []
        total_ec = 0
        total_n = 0
        total_p = 0
        total_k = 0
        
        # Generic compound properties
        compounds = {
            'Calcium Nitrate': {
                'ec_impact': 0.12,
                'npk': '15.5-0-0',
                'base_rate': 0.8,  # g/L
                'stages': {
                    'Seedling': 0.5,
                    'Early Veg': 0.7,
                    'Late Veg': 0.9,
                    'Early Flower': 1.0,
                    'Mid Flower': 0.8,
                    'Late Flower': 0.6
                }
            },
            'Potassium Nitrate': {
                'ec_impact': 0.13,
                'npk': '13-0-46',
                'base_rate': 0.6,
                'stages': {
                    'Seedling': 0.3,
                    'Early Veg': 0.5,
                    'Late Veg': 0.7,
                    'Early Flower': 1.0,
                    'Mid Flower': 1.2,
                    'Late Flower': 0.8
                }
            },
            'Magnesium Sulfate': {
                'ec_impact': 0.06,
                'npk': '0-0-0',
                'base_rate': 0.5,
                'stages': {
                    'Seedling': 0.5,
                    'Early Veg': 0.7,
                    'Late Veg': 0.8,
                    'Early Flower': 1.0,
                    'Mid Flower': 1.0,
                    'Late Flower': 0.8
                }
            },
            'Monopotassium Phosphate': {
                'ec_impact': 0.08,
                'npk': '0-52-34',
                'base_rate': 0.4,
                'stages': {
                    'Seedling': 0.3,
                    'Early Veg': 0.5,
                    'Late Veg': 0.7,
                    'Early Flower': 1.0,
                    'Mid Flower': 1.2,
                    'Late Flower': 0.8
                }
            }
        }
        
        for compound, selected in selected_compounds.items():
            if selected and compound in compounds:
                details = compounds[compound]
                stage_multiplier = details['stages'].get(growth_stage, 1.0)
                amount = details['base_rate'] * stage_multiplier * (strength / 100) * size
                
                # Calculate NPK contribution
                if 'npk' in details:
                    n, p, k = map(float, details['npk'].split('-'))
                    total_n += n * (amount/size)
                    total_p += p * (amount/size)
                    total_k += k * (amount/size)
                
                # Add to results
                results.append({
                    'Nutrient': compound,
                    'Amount (g)': f"{amount:.1f}",
                    'g/L': f"{amount/size:.3f}",
                    'Type': 'Generic',
                    'EC Impact': details['ec_impact'] * stage_multiplier
                })
                total_ec += details['ec_impact'] * stage_multiplier
        
        return results, {
            'Total EC': f"{total_ec:.2f}",
            'Total N': f"{total_n:.1f}",
            'Total P': f"{total_p:.1f}",
            'Total K': f"{total_k:.1f}",
            'NPK Ratio': f"{total_n:.1f}-{total_p:.1f}-{total_k:.1f}",
            'Target EC Range': self.get_target_ec_range(growth_stage)
        }

    def get_mixing_instructions(self, results):
        """Generate mixing instructions based on calculations"""
        instructions = []
        
        # Sort nutrients by type and mixing order
        base_nutrients = [r for r in results if r['Type'] == 'Brand Base']
        supplements = [r for r in results if r['Type'] == 'Brand Supplement']
        generic_compounds = [r for r in results if r['Type'] == 'Generic']
        
        instructions.append("Mixing Instructions:")
        instructions.append("1. Fill reservoir with 80% of final water volume")
        instructions.append("2. Start air stone / circulation pump")
        
        if generic_compounds:
            instructions.append("\nGeneric Compounds (mix in order):")
            for compound in generic_compounds:
                instructions.append(f"- Add {compound['Amount (g)']}g of {compound['Nutrient']}")
                instructions.append("  Wait 2-3 minutes between additions")
        
        if base_nutrients:
            instructions.append("\nBase Nutrients:")
            for base in base_nutrients:
                instructions.append(f"- Add {base['Amount (ml)']}ml of {base['Nutrient']}")
                instructions.append("  Mix thoroughly")
        
        if supplements:
            instructions.append("\nSupplements:")
            for supp in supplements:
                instructions.append(f"- Add {supp['Amount (ml)']}ml of {supp['Nutrient']}")
        
        instructions.append("\nFinal Steps:")
        instructions.append("1. Top off to final volume with water")
        instructions.append("2. Check and adjust pH")
        instructions.append("3. Wait 15 minutes and check EC")
        
        return "\n".join(instructions)

    def update_instructions_by_stage(self, growth_stage):
        """Update mixing instructions based on growth stage"""
        stage_instructions = {
            'Seedling': {
                'ec_range': '0.4-0.8',
                'ph_range': '5.8-6.2',
                'notes': 'Use 1/4 to 1/2 strength nutrients'
            },
            'Early Veg': {
                'ec_range': '0.8-1.2',
                'ph_range': '5.8-6.2',
                'notes': 'Increase nitrogen ratio'
            },
            'Late Veg': {
                'ec_range': '1.2-1.6',
                'ph_range': '5.8-6.2',
                'notes': 'Maximum vegetative growth'
            },
            'Pre-Flower': {
                'ec_range': '1.4-1.8',
                'ph_range': '5.8-6.2',
                'notes': 'Transition to bloom nutrients'
            },
            'Early Flower': {
                'ec_range': '1.6-2.0',
                'ph_range': '5.8-6.2',
                'notes': 'Peak bloom feeding'
            },
            'Mid Flower': {
                'ec_range': '1.2-1.6',
                'ph_range': '5.8-6.2',
                'notes': 'Begin reducing nutrients'
            }
        }
        
        return stage_instructions.get(growth_stage, {
            'ec_range': '1.0-1.4',
            'ph_range': '5.8-6.2',
            'notes': 'Standard feeding'
        })

    def load_strain_data(self):
        """Load strain profiles and organize them alphabetically"""
        try:
            strain_data_path = Path("chunks/strains")
            self.strain_database = {}
            
            # Default strains as fallback
            default_strains = {
                'Runtz': {
                    'name': 'Runtz',
                    'feeding_type': 'Heavy',
                    'nutrient_preferences': {
                        'veg': {'N': 'high', 'P': 'medium', 'K': 'medium'},
                        'flower': {'N': 'medium', 'P': 'high', 'K': 'high'}
                    },
                    'optimal_ec': {'veg': [1.2, 1.6], 'flower': [1.6, 2.2]},
                    'optimal_ph': [5.8, 6.3],
                    'growth_characteristics': {
                        'height': 'Medium',
                        'stretch': 'High',
                        'feeding_needs': 'Heavy'
                    },
                    'terpene_profile': ['Gelato', 'Zkittlez', 'Cookies'],
                    'genetic_lineage': {'parents': 'Gelato x Zkittlez'}
                },
                'Girl Scout Cookies': {
                    'name': 'Girl Scout Cookies',
                    'feeding_type': 'Medium',
                    'nutrient_preferences': {
                        'veg': {'N': 'medium', 'P': 'medium', 'K': 'medium'},
                        'flower': {'N': 'medium', 'P': 'high', 'K': 'high'}
                    },
                    'optimal_ec': {'veg': [1.0, 1.4], 'flower': [1.4, 1.8]},
                    'optimal_ph': [5.8, 6.2],
                    'growth_characteristics': {
                        'height': 'Medium',
                        'stretch': 'Medium',
                        'feeding_needs': 'Medium'
                    },
                    'terpene_profile': ['Cookies', 'Mint', 'Cherry'],
                    'genetic_lineage': {'parents': 'OG Kush x Durban Poison'}
                },
                'Blue Dream': {
                    'name': 'Blue Dream',
                    'feeding_type': 'Heavy',
                    'nutrient_preferences': {
                        'veg': {'N': 'high', 'P': 'medium', 'K': 'medium'},
                        'flower': {'N': 'medium', 'P': 'high', 'K': 'high'}
                    },
                    'optimal_ec': {'veg': [1.2, 1.6], 'flower': [1.6, 2.0]},
                    'optimal_ph': [5.8, 6.2],
                    'growth_characteristics': {
                        'height': 'Tall',
                        'stretch': 'High',
                        'feeding_needs': 'Heavy'
                    },
                    'terpene_profile': ['Blueberry', 'Haze', 'Sweet'],
                    'genetic_lineage': {'parents': 'Blueberry x Haze'}
                }
            }
            
            # Try to load strain data from files
            if strain_data_path.exists():
                for strain_file in strain_data_path.glob("*.json"):
                    with open(strain_file, 'r') as f:
                        strain_info = json.load(f)
                        self.strain_database[strain_info['name']] = strain_info
            else:
                self.strain_database = default_strains
                logger.warning("Using default strain profiles - could not load strain database")
                
        except Exception as e:
            logger.error(f"Error loading strain data: {e}")
            self.strain_database = default_strains

    def get_target_ph_range(self, strain_type):
        """Get target pH range based on strain type"""
        ph_ranges = {
            'Light Feeders': (5.5, 6.0),
            'Medium Feeders': (5.8, 6.2),
            'Heavy Feeders': (5.8, 6.3)
        }
        return f"{ph_ranges.get(strain_type, (5.8, 6.2))[0]}-{ph_ranges.get(strain_type, (5.8, 6.2))[1]}"

    def get_target_ec_range(self, growth_stage):
        """Get target EC range based on growth stage"""
        ec_ranges = {
            'Seedling': '0.4-0.8',
            'Early Veg': '0.8-1.2',
            'Late Veg': '1.2-1.6',
            'Pre-Flower': '1.4-1.8',
            'Early Flower': '1.6-2.0',
            'Mid Flower': '1.8-2.2',
            'Late Flower': '1.4-1.8',
            'Flush': '0.0-0.2'
        }
        return ec_ranges.get(growth_stage, '1.0-1.4')

    def get_temp_range(self, growth_stage):
        """Get target temperature range based on growth stage"""
        temp_ranges = {
            'Seedling': '72-78°F',
            'Early Veg': '70-78°F',
            'Late Veg': '70-80°F',
            'Pre-Flower': '70-78°F',
            'Early Flower': '70-78°F',
            'Mid Flower': '68-76°F',
            'Late Flower': '65-75°F',
            'Flush': '65-75°F'
        }
        return temp_ranges.get(growth_stage, '70-78°F')

    def get_humidity_range(self, growth_stage):
        """Get target humidity range based on growth stage"""
        humidity_ranges = {
            'Seedling': '65-70%',
            'Early Veg': '60-70%',
            'Late Veg': '55-65%',
            'Pre-Flower': '50-60%',
            'Early Flower': '45-55%',
            'Mid Flower': '40-50%',
            'Late Flower': '35-45%',
            'Flush': '35-45%'
        }
        return humidity_ranges.get(growth_stage, '50-60%')

    def get_vpd_range(self, growth_stage):
        """Get target VPD range based on growth stage"""
        vpd_ranges = {
            'Seedling': '0.4-0.8',
            'Early Veg': '0.8-1.0',
            'Late Veg': '1.0-1.2',
            'Pre-Flower': '1.0-1.2',
            'Early Flower': '1.1-1.3',
            'Mid Flower': '1.2-1.4',
            'Late Flower': '1.2-1.4',
            'Flush': '1.0-1.2'
        }
        return vpd_ranges.get(growth_stage, '1.0-1.2')

    def get_stage_tips(self, stage):
        """Get growing tips for each stage"""
        tips = {
            "Seedling": """
                • Minimal nutrients needed (25-50% strength)
                • Focus on root development
                • Keep EC low (0.4-0.8)
                • Maintain high humidity (65-70%)
                • Light feeding with emphasis on root development
            """,
            "Early Veg": """
                • Increase nitrogen levels gradually
                • Watch for rapid growth
                • Maintain higher humidity (60-70%)
                • Good time to start training
                • Focus on building strong stems
            """,
            "Late Veg": """
                • Peak vegetative feeding
                • Strong nitrogen and CalMag
                • Perfect for training techniques
                • Maximum growth phase
                • Watch for any deficiencies
            """,
            "Pre-Flower": """
                • Transition phase
                • Begin reducing nitrogen
                • Increase P and K levels
                • Watch for gender signs
                • Prepare for stretch
            """,
            "Early Flower": """
                • Stretch phase management
                • Support strong growth
                • Balanced feeding important
                • Increase bloom nutrients
                • Monitor plant spacing
            """,
            "Mid Flower": """
                • Peak flower production
                • Maximum PK levels
                • Watch for deficiencies
                • Monitor trichome development
                • Focus on bud development
            """,
            "Late Flower": """
                • Reduce nitrogen further
                • Focus on terpene production
                • Watch for ripeness
                • Monitor trichomes
                • Prepare for harvest
            """,
            "Flush": """
                • Clear salt buildup
                • Use plain pH'd water
                • Monitor runoff EC
                • Watch for natural fade
                • Prepare for harvest
            """
        }
        return tips.get(stage, "Maintain balanced nutrition and monitor plant response.")

    def get_feeding_schedule(self, nutrient_line, growth_stage, strain_type='Medium Feeders'):
        """Get detailed feeding schedule with adjustments"""
        try:
            base_schedules = {
                'General Hydroponics': {
                    'Seedling': {
                        'Flora Micro': 0.25, 'Flora Grow': 0.25, 'Flora Bloom': 0.25, 
                        'CaliMagic': 0.5, 'Rapid Start': 0.5
                    },
                    'Early Veg': {
                        'Flora Micro': 1.0, 'Flora Grow': 1.5, 'Flora Bloom': 0.5, 
                        'CaliMagic': 1.0, 'Rapid Start': 1.0, 'Armor Si': 0.5
                    },
                    'Late Veg': {
                        'Flora Micro': 2.0, 'Flora Grow': 2.0, 'Flora Bloom': 1.0, 
                        'CaliMagic': 1.5, 'Armor Si': 1.0, 'Diamond Nectar': 1.0
                    },
                    'Pre-Flower': {
                        'Flora Micro': 2.0, 'Flora Grow': 1.5, 'Flora Bloom': 2.0, 
                        'CaliMagic': 2.0, 'Armor Si': 1.0, 'Liquid KoolBloom': 0.5
                    },
                    'Early Flower': {
                        'Flora Micro': 2.0, 'Flora Grow': 1.0, 'Flora Bloom': 2.5, 
                        'CaliMagic': 2.0, 'Liquid KoolBloom': 1.0
                    },
                    'Mid Flower': {
                        'Flora Micro': 2.0, 'Flora Grow': 0.5, 'Flora Bloom': 3.0, 
                        'CaliMagic': 2.0, 'Liquid KoolBloom': 2.0, 'Dry KoolBloom': 0.5
                    },
                    'Late Flower': {
                        'Flora Micro': 1.5, 'Flora Grow': 0, 'Flora Bloom': 2.5, 
                        'CaliMagic': 1.5, 'Dry KoolBloom': 1.0
                    },
                    'Flush': {'Flora Micro': 0, 'Flora Grow': 0, 'Flora Bloom': 0}
                }
                # Add other nutrient lines here...
            }
            
            # Get base schedule
            schedule = base_schedules.get(nutrient_line, {}).get(growth_stage, {})
            
            # Apply strain type multiplier
            strain_multipliers = {
                'Heavy Feeders': 1.2,
                'Medium Feeders': 1.0,
                'Light Feeders': 0.8
            }
            multiplier = strain_multipliers.get(strain_type, 1.0)
            
            # Adjust amounts based on strain type
            adjusted_schedule = {
                nutrient: round(amount * multiplier, 2)
                for nutrient, amount in schedule.items()
            }
            
            return adjusted_schedule
            
        except Exception as e:
            self.debugger.track_error(e, {
                'method': 'get_feeding_schedule',
                'nutrient_line': nutrient_line,
                'growth_stage': growth_stage,
                'strain_type': strain_type
            })
            return {}

    def display_feeding_schedule(self, nutrient_line, growth_stage, strain_type='Medium Feeders'):
        """Display enhanced feeding schedule with additional information"""
        try:
            schedule = self.get_feeding_schedule(nutrient_line, growth_stage, strain_type)
            
            if schedule:
                # Create columns for better organization
                cols = st.columns(3)
                
                for idx, (nutrient, amount) in enumerate(schedule.items()):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        # Get nutrient type and color
                        nutrient_type = self.get_nutrient_type(nutrient_line, nutrient)
                        color = self.get_nutrient_color(nutrient_type)
                        
                        # Display metric with color and tooltip
                        st.metric(
                            label=f":{color}[{nutrient}]",
                            value=f"{amount} ml/gal",
                            help=f"""
                            Type: {nutrient_type}
                            Stage: {growth_stage}
                            Strain Type: {strain_type}
                            """
                        )
            else:
                st.info("No specific schedule available for this combination")
                
        except Exception as e:
            self.debugger.track_error(e, {
                'method': 'display_feeding_schedule',
                'nutrient_line': nutrient_line,
                'growth_stage': growth_stage,
                'strain_type': strain_type
            })
            st.error("Error displaying feeding schedule")

    def get_nutrient_type(self, nutrient_line, nutrient_name):
        """Get the type of nutrient"""
        try:
            line_data = self.nutrient_lines.get(nutrient_line, {})
            if nutrient_name in line_data.get('base_nutrients', {}):
                return line_data['base_nutrients'][nutrient_name].get('type', 'base')
            elif nutrient_name in line_data.get('supplements', {}):
                return line_data['supplements'][nutrient_name].get('type', 'supplement')
            return 'unknown'
        except Exception:
            return 'unknown'

    def get_nutrient_color(self, nutrient_type):
        """Get color for nutrient type"""
        colors = {
            'micro': 'blue',
            'grow': 'green',
            'bloom': 'red',
            'calmag': 'orange',
            'root': 'violet',
            'pk_boost': 'yellow',
            'supplement': 'gray'
        }
        return colors.get(nutrient_type, 'white')

    @debugger.monitor_performance("calculate_nutrients")
    def calculate_nutrients(self, size, strength, selected_nutrients, growth_stage, strain_info):
        """Calculate nutrient amounts based on inputs"""
        try:
            results = {}
            base_multiplier = float(strength) / 100.0  # Convert percentage to decimal
            
            # Adjust multiplier based on growth stage
            stage_multipliers = {
                'Seedling': 0.25,
                'Early Veg': 0.5,
                'Late Veg': 0.75,
                'Pre-Flower': 0.8,
                'Early Flower': 1.0,
                'Mid Flower': 1.0,
                'Late Flower': 0.75,
                'Flush': 0.0
            }
            stage_multiplier = stage_multipliers.get(growth_stage, 1.0)
            
            # Adjust for strain feeding type
            strain_multipliers = {
                'Heavy Feeders': 1.2,
                'Medium Feeders': 1.0,
                'Light Feeders': 0.8
            }
            strain_multiplier = strain_multipliers.get(strain_info.get('feeding_type', 'Medium'), 1.0)
            
            # Calculate final multiplier
            final_multiplier = base_multiplier * stage_multiplier * strain_multiplier
            
            # Calculate amounts for each selected nutrient
            for nutrient_name in selected_nutrients:
                for line, products in self.nutrient_lines.items():
                    if nutrient_name in products['base_nutrients']:
                        nutrient = products['base_nutrients'][nutrient_name]
                        max_strength = nutrient.get('max_strength', 4.0)  # Default to 4.0 if not specified
                        amount = round(max_strength * final_multiplier * float(size), 2)
                        results[nutrient_name] = {
                            'amount': amount,
                            'unit': 'ml',
                            'npk': nutrient.get('npk', 'N/A'),
                            'type': nutrient.get('type', 'base')
                        }
                    elif nutrient_name in products['supplements']:
                        supplement = products['supplements'][nutrient_name]
                        max_strength = supplement.get('max_strength', 2.0)  # Default to 2.0 for supplements
                        amount = round(max_strength * final_multiplier * float(size), 2)
                        results[nutrient_name] = {
                            'amount': amount,
                            'unit': 'ml',
                            'type': supplement.get('type', 'supplement')
                        }
            
            return results
            
        except Exception as e:
            self.debugger.track_error(e, {
                'method': 'calculate_nutrients',
                'size': size,
                'strength': strength,
                'growth_stage': growth_stage,
                'strain_info': strain_info
            })
            raise

    def render_calculator(self):
        """Render the nutrient calculator interface"""
        st.header("Nutrient Calculator")

        # Recipe Selection
        recipes = self.recipe_manager.list_recipes()
        selected_recipe = st.selectbox(
            "Base Recipe",
            options=["New Recipe"] + recipes,
            help="Select a base recipe or create new"
        )

        # Growth Phase
        growth_phase = st.select_slider(
            "Growth Phase",
            options=[
                "Seedling",
                "Early Veg",
                "Late Veg",
                "Pre-Flower",
                "Early Flower",
                "Mid Flower",
                "Late Flower",
                "Flush"
            ],
            help="Adjust nutrients based on growth phase"
        )

        # Quick Adjustments
        col1, col2 = st.columns(2)
        with col1:
            strength = st.slider("Recipe Strength (%)", 25, 150, 100)
            ph_target = st.slider("Target pH", 5.0, 7.0, 5.8, 0.1)

        with col2:
            ec_target = st.slider("Target EC (mS/cm)", 0.5, 3.0, 1.8, 0.1)
            size = st.number_input("Reservoir Size (gallons)", min_value=1, value=5)

        if st.button("Calculate Recipe"):
            if selected_recipe == "New Recipe":
                self.create_new_recipe(growth_phase, strength, ph_target, ec_target, size)
            else:
                self.modify_existing_recipe(selected_recipe, growth_phase, strength, ph_target, ec_target, size)

    def create_new_recipe(self, growth_phase, strength, ph_target, ec_target, size):
        """Create a new recipe with the given parameters"""
        recipe_data = {
            'growth_phase': growth_phase,
            'strength': strength,
            'ph_target': ph_target,
            'ec_target': ec_target,
            'size': size,
            'nutrients': self.calculate_nutrients(size, strength, {}, growth_phase, {})
        }

        # Show save dialog
        recipe_name = st.text_input("Recipe Name")
        if recipe_name and st.button("Save Recipe"):
            if self.recipe_manager.save_recipe(recipe_name, recipe_data):
                st.success(f"Recipe '{recipe_name}' saved successfully!")
            else:
                st.error("Failed to save recipe")

    def modify_existing_recipe(self, recipe_name, growth_phase, strength, ph_target, ec_target, size):
        """Modify an existing recipe with new parameters"""
        recipe = self.recipe_manager.get_recipe(recipe_name)
        if recipe:
            recipe.update({
                'growth_phase': growth_phase,
                'strength': strength,
                'ph_target': ph_target,
                'ec_target': ec_target,
                'size': size,
                'nutrients': self.calculate_nutrients(size, strength, {}, growth_phase, {}),
                'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            if self.recipe_manager.save_recipe(recipe_name, recipe):
                st.success(f"Recipe '{recipe_name}' updated successfully!")
            else:
                st.error("Failed to update recipe")

def create_nutrient_calculator():
    """Create and initialize the nutrient calculator"""
    try:
        # Initialize Streamlit session state
        if not hasattr(st, 'session_state'):
            st.session_state = {}
        
        calculator = NutrientCalculatorUI()
        logger.info("Nutrient Calculator initialized successfully")
        return calculator
    except Exception as e:
        logger.error(f"Failed to create Nutrient Calculator: {str(e)}")
        st.error(f"Failed to create Nutrient Calculator: {str(e)}")
        return None

if __name__ == "__main__":
    st.set_page_config(
        page_title="Nutrient Calculator",
        page_icon="🌱",
        layout="wide"
    )
    calculator = create_nutrient_calculator()
    if calculator:
        calculator.render()



