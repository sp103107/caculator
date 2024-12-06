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
        """Load nutrient lines including generic options"""
        self.nutrient_lines = {
            'Generic': {
                'description': 'Standard nutrient components for any brand',
                'base_nutrients': {
                    'Micro': {
                        'type': 'micro',
                        'max_strength': 3.0,
                        'description': 'Micronutrient blend',
                        'npk': '5-0-1'
                    },
                    'Grow': {
                        'type': 'grow',
                        'max_strength': 3.0,
                        'description': 'Vegetative growth nutrient',
                        'npk': '3-1-3'
                    },
                    'Bloom': {
                        'type': 'bloom',
                        'max_strength': 3.0,
                        'description': 'Flowering nutrient',
                        'npk': '0-5-4'
                    }
                },
                'supplements': {
                    'CalMag': {
                        'type': 'calmag',
                        'max_strength': 5.0,
                        'description': 'Calcium-Magnesium supplement',
                        'when_to_use': 'Throughout grow cycle'
                    },
                    'Silica': {
                        'type': 'silica',
                        'max_strength': 2.0,
                        'description': 'Silica supplement for strength',
                        'when_to_use': 'Add first, throughout cycle'
                    },
                    'PK Booster': {
                        'type': 'pk_boost',
                        'max_strength': 2.0,
                        'description': 'Phosphorus-Potassium boost',
                        'when_to_use': 'Mid to late flower'
                    }
                }
            },
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

    def calculate_nutrients(self, size: float, strength: float, selected_nutrients: list, growth_stage: str, strain_info: dict, unit_system: str = 'US'):
        """Calculate nutrient amounts based on parameters"""
        try:
            recipe = {}
            
            # Convert size to gallons if needed
            gallons = size if unit_system == 'US' else size * 0.264172
            
            # Get base strength multiplier based on growth stage
            stage_multipliers = {
                "Seedling": 0.25,
                "Early Veg": 0.5,
                "Late Veg": 0.75,
                "Pre-Flower": 0.8,
                "Early Flower": 1.0,
                "Mid Flower": 1.0,
                "Late Flower": 0.75,
                "Flush": 0.0
            }
            
            stage_multiplier = stage_multipliers.get(growth_stage, 1.0)
            final_strength = (strength / 100) * stage_multiplier
            
            # Calculate base nutrients
            for nutrient in selected_nutrients:
                if nutrient in self.nutrient_lines['General Hydroponics']['base_nutrients']:
                    nutrient_data = self.nutrient_lines['General Hydroponics']['base_nutrients'][nutrient]
                    base_amount = nutrient_data['max_strength'] * final_strength * gallons
                    
                    recipe[nutrient] = {
                        'amount': round(base_amount, 1),
                        'unit': 'ml',
                        'type': nutrient_data['type'],
                        'per_unit': f"{round(nutrient_data['max_strength'] * final_strength, 2)} ml/gal",
                        'notes': nutrient_data.get('description', ''),
                        'npk': nutrient_data.get('npk', 'N/A')
                    }
            
            # Calculate supplements
            supplement_data = self.nutrient_lines['General Hydroponics']['supplements']
            for supplement, data in supplement_data.items():
                if data['type'] in ['calmag', 'silica', 'pk_boost']:
                    amount = data['max_strength'] * final_strength * gallons
                    recipe[supplement] = {
                        'amount': round(amount, 1),
                        'unit': 'ml',
                        'type': data['type'],
                        'per_unit': f"{round(data['max_strength'] * final_strength, 2)} ml/gal",
                        'notes': data.get('description', ''),
                        'when_to_use': data.get('when_to_use', '')
                    }
            
            return recipe
            
        except Exception as e:
            logger.error(f"Failed to calculate nutrients: {str(e)}")
            raise ValueError(f"Nutrient calculation failed: {str(e)}")

class NutrientCalculatorUI:
    def __init__(self):
        self.recipe_manager = RecipeManager()
        # Initialize debugger as a class instance
        self.debugger = {
            'track_error': self._track_error,
            'name': 'nutrient_calculator'
        }
        
    def _track_error(self, error, context=None):
        """Internal error tracking method"""
        error_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(error),
            'context': context or {}
        }
        logger.error(f"Error tracked: {error_data}")
        return error_data
        
    def calculate_recipe(self, nutrient_line: str, volume: float, growth_stage: str, strength: float = 1.0, unit_system: str = 'US'):
        try:
            # Get recipe from recipe manager
            recipe = self.recipe_manager.calculate_nutrients(
                size=volume,
                strength=strength * 100,  # Convert to percentage
                selected_nutrients=list(self.recipe_manager.nutrient_lines[nutrient_line]['base_nutrients'].keys()),
                growth_stage=growth_stage,
                strain_info={'feeding_type': 'Medium'},  # Default to medium feeder
                unit_system=unit_system
            )
            
            # Add type information for recipe instructions
            for nutrient, details in recipe.items():
                if nutrient in self.recipe_manager.nutrient_lines[nutrient_line]['base_nutrients']:
                    details['type'] = self.recipe_manager.nutrient_lines[nutrient_line]['base_nutrients'][nutrient]['type']
                elif nutrient in self.recipe_manager.nutrient_lines[nutrient_line]['supplements']:
                    details['type'] = self.recipe_manager.nutrient_lines[nutrient_line]['supplements'][nutrient]['type']
            
            return recipe
            
        except Exception as e:
            logger.error(f"Recipe calculation failed: {str(e)}")
            st.error(f"Failed to calculate recipe: {str(e)}")
            return {}

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



