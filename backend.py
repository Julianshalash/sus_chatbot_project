import re
import logging
import math

class BuildingDataProcessor:
    def __init__(self, input_text: str):
        self.input_text = input_text.lower()
        self.patterns = {
            "building_type": r"(commercial|institutional|residential|retail)",
            "building_typee": r"(multi-residential|individual)",
            "occupants": r"(regular\s*building\s*occupants|people|residents)\s*=\s*(\d+)",
            "occupantss": r"(|people|residents)\s*=\s*(\d+)",
            "dwelling_units": r"number\s*of\s*dwelling\s*units\s*=\s*(\d+)",
            "peak_visitors": r"peak\svisitors\s*=\s*([\d.]+)",
            "peak_inpatients": r"peak\sinpatients\s*=\s*([\d.]+)",
            "qualifying_outpatients": r"qualifying\soutpatients\s*=\s*([\d.]+)",
            "unit": r"(foot|ft|feet|foot2|ft2|feet2|m|meter|meter2|m2)",
            "area": r"(?:floor\s*area|building\s*area|area)\s*=\s*([\d.]+)\s*(foot|ft|foot2|ft2|meter|m|meter2|m2)?",
            "areaa": r"(?:floor\s*area|building\s*area|area)\s*=\s*([\d.]+)\s*([a-zA-Z]+)?",
            "length_width": (
                    r"(?:(?:length\s*=\s*(?P<length>[\d.]+)\s*(?P<length_unit>foot|ft|meter|m))\s*(?:,|and)?\s*"
                    r"(?:width\s*=\s*(?P<width>[\d.]+)\s*(?P<width_unit>foot|ft|meter|m))|"
                    r"(?:width\s*=\s*(?P<width2>[\d.]+)\s*(?P<width_unit2>foot|ft|meter|m))\s*(?:,|and)?\s*"
                    r"(?:length\s*=\s*(?P<length2>[\d.]+)\s*(?P<length_unit2>foot|ft|meter|m)))"
                            ),

            "length_widthh": (
                    r"(?:length\s*=\s*(?P<length>[\d.]+)\s*(?P<length_unit>foot|ft|meter|m)\s*(?:,|and)?\s*"
                    r"width\s*=\s*(?P<width>[\d.]+)\s*(?P<width_unit>foot|ft|meter|m))|"
                    r"(?:width\s*=\s*(?P<width2>[\d.]+)\s*(?P<width_unit2>foot|ft|meter|m)\s*(?:,|and)?\s*"
                    r"length\s*=\s*(?P<length2>[\d.]+)\s*(?P<length_unit2>foot|ft|meter|m))"
                                 ),
            "area_with_unit": r"(?:area\s*=\s*([\d.]+)\s*(foot|ft|foot2|ft2|meter|m|meter2|m2))",
            "total_parking_space": r"(Total\s*parking\s*space|Total\s*space|Total\s*spaces|Total\s*parking\s*spaces)\s*=\s*(\d+)",
            "restoration_area": r"Restoration\s*area\s*=\s*([\d.]+)",
            "disturbed_area": r"Total\s*previously\s*disturbed\s*site\s*area\s*=\s*([\d.]+)",
            "total_site_area": r"Total\s*site\s*area\s*=\s*([\d.]+)",
            "required_open_space": r"(required\s*open\s*space|open\s*space)\s*=\s*([\d.]+)",
            "rainfall" : r"rainfall\s*=\s*([\d.]+)",
            "depression_storage" : r"depression\s*storage\s*=\s*([\d.]+)?",
            "infiltration" : r"infiltration\s*=\s*([\d.]+)",
            "fmin": r"fmin\s*=\s*([\d.]+)",
            "fmax": r"fmax\s*=\s*([\d.]+)",
            "k": r"k\s*=\s*([\d.]+)",
            "t": r"t\s*=\s*([\d.]+)",
            "previously_area": r"Area\s*of\s*previously\s*developed\s*land\s*=\s*([\d.]+)",
            "development_footprint": r"development\s*footprint\s*=\s*([\d.]+)",
            "long_term": r"long\s*term\s*=\s*([\d]+)",
            "short_term": r"short\s*term\s*=\s*([\d]+)",
            "area_racks": r"(area|floor|building)\s*=\s*([\d.]+)",
            "baseline_energy": r"(?i)\b(?:baseline\s+(?:annual\s+)?energy)\s*=\s*([\d.]+)",
            "proposed_energy": r"(?i)\b(?:proposed\s+(?:annual\s+)?energy)\s*=\s*([\d.]+)",
            "material_thickness": r"material\s*thickness\s*=\s*([\d.]+)",
            "thermal_conductivity": r"thermal\s*conductivity\s*=\s*([\d.]+)",
            "R_value": r"(?i)r\s*value\s*=\s*([\d.]+)",
            "shw_generated": r"annual\s*hot\s*water\s*generated\s*by\s*shw\s*=\s*([\d.]+)",
            "hot_water_demand": r"annual\s*hot\s*water\s*demand\s*=\s*([\d.]+)",
            "pv_energy_generated": r"energy\s*generated\s*by\s*pv\s*=\s*([\d.]+)",
            "proposed_energy_consumption": r"proposed\s*annual\s*energy\s*consumption\s*=\s*([\d.]+)",
            "annual_energy_generated": r"annual\s*energy\s*generated\s*=\s*([\d.]+)",
            "community_energy_consumed": r"community\s*energy\s*consumption\s*=\s*([\d.]+)",
            "designed_occupancy": r"designed\s*maximum\s*occupancy\s*=\s*(\d+)",
            "expected_occupancy": r"expected\s*occupancy\s*=\s*(\d+)",
            "total_occupancy": r"total\s*occupancy\s*=\s*(\d+)",
            "compliant_adhesives": r"weight\s*of\s*adhesives\s*and\s*sealants\s*not\s*exceeding\s*voc\s*=\s*([\d.]+)",
            "total_adhesives": r"total\s*weight\s*=\s*([\d.]+)",
            "recycled": r"(amount\s*of\s*recycled|recycled)\s*=\s*([\d.]+)",
            "reused": r"(amount\s*of\s*reused|reused)\s*=\s*([\d.]+)",
            "salvaged": r"(amount\s*of\s*salvaged|salvaged)\s*=\s*([\d.]+)",
            "donated": r"(amount\s*of\s*donated|donated)\s*=\s*([\d.]+)",
            "reclaimed": r"(amount\s*of\s*reclaimed|reclaimed)\s*=\s*([\d.]+)",
            "total_waste": r"(total\s*amount\s*of\s*waste\s*generated|total\s*waste)\s*=\s*([\d.]+)",
            "street_links": r"street\s*links\s*=\s*(\d+)",
            "nodes": r"nodes\s*=\s*(\d+)",
            "intersections": r"intersections\s*=\s*(\d+)",
            "continuous_walkway_on_both": r"linear\s*length\s*on\s*both\s*sides\s*=\s*([\d.]+)",
            "all_walkways": r"all\s*walkways\s*=\s*([\d.]+)",
            "gfa": r"(gross\s*(floor\s*)?area|gfa)\s*=\s*([\d.]+)",
            "site_area": r"total\s*site\s*area\s*=\s*([\d.]+)",
            "cooling_provided":r"cooling\s*provided\s*=\s*([\d.]+)",
            "energy_consumed" : r"energy\s*consumed\s*=\s*([\d.]+)",
            "compliant_paints":r"weight\s*not\s*exceeding\s*voc\s*=\s*([\d.]+)",
            "total_paints":r"total\s*weight\s*=\s*([\d.]+)",
            "Dwelling_building_size": r"(communal|private)"
        }
        self.matches = {}
        self.intents = {}
        self.extract_data()
        self.detect_intents()

    def extract_data(self):
        """Extract data based on regex patterns."""
        for key, pattern in self.patterns.items():
            match = re.search(pattern, self.input_text, re.IGNORECASE)
            if match:
                self.matches[key] = match.groups()
                logging.debug(f"Match for {key}: {self.matches[key]}")  # Log the matches for debugging purposes

    def detect_intents(self):
        """Detect intents from the input text."""
        self.intents['long_term_storage'] = "long-term bicycle storage" in self.input_text
        self.intents['short_term_storage'] = "short-term bicycle storage" in self.input_text
        self.intents['shower_facilities'] = any(phrase in self.input_text.lower() for phrase in ["shower facilities", "shower", "shower facility"])
        self.intents['preferred_spaces'] = any(phrase in self.input_text.lower() for phrase in ["preferred space", "preferred spaces", "required number of preferred spaces"])
        self.intents['fueling_stations'] = any(phrase in self.input_text.lower() for phrase in ["fueling stations", "fuel stations", "required number of fueling stations"])
        self.intents['restoration_area'] = any(phrase in self.input_text.lower() for phrase in ["percentage of restoration area", "restoration area percentage"])
        self.intents['open_space'] = any(phrase in self.input_text.lower() for phrase in ["required open space", "open space requirement"])
        self.intents['vegetated_space'] = "vegetated space" in self.input_text
        self.intents['outdoor_area'] = any(phrase in self.input_text.lower() for phrase in ["required outdoor area", "outdoor area requirement", "outdoor area"])
        self.intents['air_volume_before_occupancy'] = any(phrase in self.input_text.lower() for phrase in ["air volume before occupancy", "flush out before occupancy"])
        self.intents['air_volume_during_occupancy'] = any(phrase in self.input_text.lower() for phrase in ["air volume during occupancy", "flush out during occupancy"])
        self.intents['air_volume_to_complete'] = any(phrase in self.input_text.lower() for phrase in ["air volume to complete", "flush out to complete"])
        self.intents['Runoff'] = any(phrase in self.input_text.lower() for phrase in ["runoff", "Expected runoff","run off"])
        self.intents['Depression storage'] = "depression storage" in self.input_text.lower()
        self.intents['development_percentage'] = any(phrase in self.input_text.lower() for phrase in ["previously developed land", "percentage of previously developed land"]) 
        self.intents['bicycle_racks'] = any(phrase in self.input_text for phrase in ["number of bicycle racks required", "total of bicycle racks", "bicycle racks"])
        self.intents['energy_performance'] = any(phrase in self.input_text for phrase in ["energy performance", "energy improvement"])
        self.intents['r_value'] = any(phrase in self.input_text for phrase in ["r-value", "r value"])
        self.intents['u_value'] = any(phrase in self.input_text for phrase in ["u-value", "u value"])
        self.intents['shw'] = "hot water demand provided by shw" in self.input_text
        self.intents['renewable_energy'] = "renewable energy" in self.input_text
        self.intents['occupant_density'] = "occupant density" in self.input_text
        self.intents['size_of_outdoor_space'] = "size of outdoor space" in self.input_text
        self.intents['adhesives_sealants_intent'] = "compliant adhesives and sealants" in self.input_text
        self.intents['waste_diverted_intent'] = "waste diverted from landfill" in self.input_text
        self.intents['connectivity_index_intent'] = "connectivity index" in self.input_text
        self.intents['intersection_density_intent'] = "intersection density" in self.input_text
        self.intents['continuous_walkway_intent'] = any(phrase in self.input_text for phrase in ["continuous walkway", "cw"])
        self.intents['far']=any(phrase in self.input_text.lower() for phrase in["floor area ratio","far"])
        self.intents['seer']="seer" in self.input_text.lower()
        self.intents['compliant_paints']=any(phrase in self.input_text.lower() for phrase in ["compliant paints and coating", "compliant paints and coatings"])
        self.intents['dwelling_building_size'] = any(phrase in self.input_text for phrase in ["dwelling size","building size"])
        
    def process_long_term_storage(self):
        """Process long-term bicycle storage calculations."""
        building_type_match = self.matches.get('building_type')
        occupants_match = self.matches.get('occupants')
        dwelling_units_match = self.matches.get('dwelling_units')

        if not building_type_match and (occupants_match or dwelling_units_match):
            return "Building type is required for long-term bicycle storage."
        elif ( not occupants_match and not dwelling_units_match) and building_type_match :
            return "Regular building occupants or dwelling units is required for long-term bicycle storage."
        elif (not occupants_match and not dwelling_units_match) and not building_type_match:
            return "Please specify 'Regular Building occupants' or 'number of dwelling units' for residential buildings."
        
        building_type = building_type_match[0].lower()
        try:
            if building_type == 'residential':
                if occupants_match and dwelling_units_match:
                    regular_occupants = float(occupants_match[1])
                    dwelling_units = float(dwelling_units_match[0])
                    bikes_required = max(math.ceil(regular_occupants * 0.30), math.ceil(dwelling_units))
                    return f"{bikes_required} Bicycles required for long-term storage (residential)"
                elif occupants_match:
                    regular_occupants = float(occupants_match[1])
                    bikes_required = math.ceil(regular_occupants * 0.30)
                    return f"{bikes_required} Bicycles required for long-term storage (residential)"
                elif dwelling_units_match:
                    dwelling_units = float(dwelling_units_match[0])
                    bikes_required = math.ceil(dwelling_units)
                    return f"{bikes_required} Bicycles required for long-term storage (residential)"
                else:
                    return "Please specify 'Regular Building occupants' or 'number of dwelling units' for residential buildings."
            elif building_type in ['commercial', 'institutional']:
                if occupants_match:
                    regular_occupants = float(occupants_match[1])
                    bikes_required = math.ceil(regular_occupants * 0.05)
                    return f"{bikes_required} Bicycles required for long-term storage ({building_type})"
        except ValueError:
            logging.error("Error processing long-term storage")
            return "Invalid input for occupants or dwelling units."

    def process_short_term_storage(self):
        """Process short-term bicycle storage calculations."""
        peak_visitors_match = self.matches.get('peak_visitors')
        area_match = self.matches.get('area')
        length_width_match = self.matches.get('length_width')
        area_unit_match = self.matches.get('area_with_unit') 
        
        try:
            if peak_visitors_match:
                peak_visitors = float(peak_visitors_match[0])
                bikes_required = math.ceil(peak_visitors * 0.025)
                return f"{bikes_required} Bicycles required for short-term storage based on peak visitors"
        
            elif area_unit_match:
                # Check if unit is missing from the area
                if not area_unit_match[1]:
                    return "Specify the unit for required calculation"
            # Call the area-based calculation function if area is provided
                return self.process_short_term_storage_area()
                
            elif length_width_match:
                return self.process_short_term_storage_length_width()
            
            elif self.intents.get('short_term_storage'):
                if "area" in self.input_text or "length" in self.input_text or "width" in self.input_text:
                    return "Specify the unit for required calculation"
                elif not "area" in self.input_text or not "length" in self.input_text or not "width" in self.input_text:
                    return "Invalid input for peak visitors or area with unit or length and width with units"
            else:
                raise ValueError("Invalid input for peak visitors or area with unit or length and width with units.")
        except ValueError as e:
            logging.error(f"Error processing short-term storage: {e}")
            return str(e)  # Return the error message to the user
    
    def process_preferred_spaces(self):
        """Process the calculation of preferred parking spaces."""
        preferred_spaces_match = self.matches.get('total_parking_space')
        
        try:
            if preferred_spaces_match:
                total_parking_spaces = float(preferred_spaces_match[1])  # Extract total parking spaces
                preferred_spaces = math.ceil(total_parking_spaces * 0.05)  # Calculate 5% of total spaces
                return f"{preferred_spaces} preferred parking spaces required"
            else:
                return "Invalid input for Preferred space. Please specify 'Total parking spaces = <number>'."
        except ValueError:
            logging.error("Value error in Total parking spaces calculation.")
            return "Invalid input for Total parking spaces."

            
    def process_short_term_storage_area(self):
        """Process short-term bicycle storage calculations based on area."""
    # Extract area and unit together
        area_unit_match = self.matches.get('area_with_unit')

        try:
            if area_unit_match:
                area = float(area_unit_match[0])  # Extract area value
                unit = area_unit_match[1].lower() if area_unit_match[1] else None # Extract the matching unit from the text
            
            # If no unit is specified, return the error message
                if not unit:
                    return "Specify the unit for required calculation"

            # Calculate based on the unit (foot or meter)
                if unit in ['foot', 'ft', 'foot2', 'ft2']:
                    bikes_required = math.ceil(2 * (area / 5000))
                    logging.debug(f"Calculation for feet: {area} {unit}, Result: {bikes_required}")
                    return f"{bikes_required} Bicycles required for short-term storage based on area"
                elif unit in ['meter', 'm', 'meter2', 'm2']:
                    bikes_required = math.ceil(2 * (area / 465))
                    logging.debug(f"Calculation for meters: {area} {unit}, Result: {bikes_required}")
                    return f"{bikes_required} Bicycles required for short-term storage based on area"
                else:
                    raise ValueError("Invalid unit for area")
            else:
                return "Specify the unit for required calculation"  # No area or unit found
        except ValueError as e:
            logging.error(f"Error processing short-term storage: {e}")
            return str(e)  # Return the error message to the user

            
    def process_short_term_storage_length_width(self):
        """Process short-term bicycle storage calculations based on length and width."""
        length_width_match = self.matches.get('length_width')

        try:
            if length_width_match:
            # Extract length, width, and units from the match groups
                if length_width_match[0] and length_width_match[2]:
                    length = float(length_width_match[0])
                    width = float(length_width_match[2])
                    length_unit = length_width_match[1].lower()
                    width_unit = length_width_match[3].lower()
                elif length_width_match[6] and length_width_match[4]:
                    length = float(length_width_match[6])
                    width = float(length_width_match[4])
                    length_unit = length_width_match[5].lower()
                    width_unit = length_width_match[7].lower()
                else:
                    raise ValueError("Invalid length or width.")

            # Check if the units for length and width are inconsistent
                if (length_unit in ['foot', 'ft', 'foot2', 'ft2'] and width_unit in ['meter', 'm', 'meter2', 'm2']) or \
                   (length_unit in ['meter', 'm', 'meter2', 'm2'] and width_unit in ['foot', 'ft', 'foot2', 'ft2']):
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."

            # Calculate the area
                area = length * width

            # Calculate based on the unit (foot or meter)
                if length_unit in ['foot', 'ft', 'foot2', 'ft2']:
                    bikes_required = math.ceil(2 * (area / 5000))
                    return f"{bikes_required} Bicycles required for short-term storage based on length and width (area: {area} {length_unit})"
                elif length_unit in ['meter', 'm', 'meter2', 'm2']:
                    bikes_required = math.ceil(2 * (area / 465))
                    return f"{bikes_required} Bicycles required for short-term storage based on length and width (area: {area} {length_unit})"
                else:
                    raise ValueError("Invalid unit for length and width.")
            else:
                raise ValueError("Invalid input for length or width.")
        except ValueError as e:
            logging.error(f"Error processing short-term storage: {e}")
            return str(e)  # Return the error message to the user

   
    def process_shower_facilities(self):
        """Process shower facilities."""
        occupants_match = self.matches.get('occupants')
        try:
            if occupants_match:
                regular_occupants = float(occupants_match[1])
                if regular_occupants<=100:
                  showers_required = 1
        
                else:
                    showers_required = math.ceil((1 + (regular_occupants - 100)) / 150)
                return f"{showers_required} Showers required"
            else:
            # If no occupants are found, return error message
                return "Invalid input for regular building occupants. Please specify a correct number."
        
        except ValueError:
                logging.error("Value error in shower facilities calculation.")
                return "Invalid input for regular building occupants. Please specify a correct number."
            
    def process_preferred_spaces(self):
        """Process the calculation of preferred parking spaces."""
        preferred_spaces_match = self.matches.get('total_parking_space')
        
        try:
            if preferred_spaces_match:
                total_parking_spaces = float(preferred_spaces_match[1])  # Extract total parking spaces
                preferred_spaces = math.ceil(total_parking_spaces * 0.05)  # Calculate 5% of total spaces
                return f"{preferred_spaces} preferred parking spaces required"
            else:
                return "Invalid input for Preferred space. Please specify 'Total parking spaces = <number>'."
        except ValueError:
            logging.error("Value error in Total parking spaces calculation.")
            return "Invalid input for Total parking spaces."
            
    def process_fueling_stations(self):
        """Process the calculation of fueling stations."""
        fueling_stations_match = self.matches.get('total_parking_space')

        try:
            if fueling_stations_match:
                total_parking_spaces = float(fueling_stations_match[1])  # Extract total parking spaces
                fueling_stations = math.ceil(total_parking_spaces * 0.02)  # Calculate 2% of total spaces
                return f"{fueling_stations} fueling stations required"
            else:
                return "Invalid input for fueling stations. Please specify 'Total parking spaces = <number>'."
        except ValueError:
            logging.error("Value error in Total parking spaces calculation for fueling stations.")
            return "Invalid input for Total parking spaces."
    
    def process_restoration_area(self):
        """Process the calculation for percentage of restoration area."""
        restoration_area_match = self.matches.get('restoration_area')
        disturbed_area_match = self.matches.get('disturbed_area')

        try:
            if restoration_area_match and disturbed_area_match:
                restoration_area = float(restoration_area_match[0])  # Extract restoration area
                disturbed_area = float(disturbed_area_match[0])  # Extract previously disturbed area
                
                if disturbed_area == 0:
                    return "Total previously disturbed site area cannot be zero."

                # Calculate percentage of restoration area
                percentage_restoration = math.ceil((restoration_area / disturbed_area) * 100)
                return f"Percentage of restoration area = {percentage_restoration}%"
            else:
                return "Invalid input for restoration area. Please specify both 'Restoration area' and 'Total previously disturbed site area'."
        except ValueError:
            logging.error("Value error in restoration area calculation.")
            return "Invalid input for restoration area or previously disturbed site area."

    def process_vegetated_space(self):
        """Process the calculation for vegetated space."""
    # Try to match required open space directly from the input
        required_open_space_match = self.matches.get('required_open_space')

        try:
        # Case 1: If required open space is provided directly
            if required_open_space_match:
                required_open_space = float(required_open_space_match[1])  # Extract required open space from match
            else:
            # Case 2: Calculate required open space based on the total site area
                required_open_space = self.process_required_open_space()

            if required_open_space:
            # Calculate vegetated space as 25% of the required open space
                vegetated_space = math.ceil(required_open_space * 0.25)
                return f"Vegetated space ≥ {vegetated_space}% of required open space"
            else:
                return "Invalid input for vegetated space. Please specify 'Total site area' or 'Required open space'."

        except ValueError:
            logging.error("Value error in vegetated space calculation.")
            return "Invalid input for vegetated space."

    def process_required_open_space(self):
        """Process the calculation for required open space."""
        total_site_area_match = self.matches.get('total_site_area')
    
        try:
            if total_site_area_match:
                total_site_area = float(total_site_area_match[0])  # Extract total site area
                required_open_space = math.ceil(total_site_area * 0.30)  # Calculate 30% of total site area
                return required_open_space
            else:
                return None  # No input for total site area
        except ValueError:
            logging.error("Value error in total site area calculation.")
            return None  # Invalid input for total site area
            
    def process_outdoor_area(self):
        """Process the calculation for required outdoor area."""
        unit_match = self.matches.get('unit')
        peak_inpatients_match = self.matches.get('peak_inpatients')
        qualifying_outpatients_match = self.matches.get('qualifying_outpatients')

        try:
            # Check if any input is missing and return specific error message
            if not unit_match and  peak_inpatients_match and qualifying_outpatients_match:
                return "Invalid input for outdoor area. Please specify 'Area unit'."
            elif not peak_inpatients_match and unit_match and qualifying_outpatients_match:
                return "Invalid input for outdoor area. Please specify 'Peak inpatients'."
            elif not qualifying_outpatients_match and unit_match and  peak_inpatients_match :
                return "Invalid input for outdoor area. Please specify 'Qualifying outpatients'."
            elif not qualifying_outpatients_match and not unit_match and  peak_inpatients_match:
                return "Invalid input for outdoor area. Please specify 'Qualifying outpatients' and 'Area unit'."
            elif not qualifying_outpatients_match and not peak_inpatients_match and unit_match:
                return "Invalid input for outdoor area. Please specify 'Qualifying outpatients' and 'Peak inpatients'."
            elif not  peak_inpatients_match and not  unit_match and qualifying_outpatients_match:
                return "Invalid input for outdoor area. Please specify 'Peak inpatients' and 'Area unit'."

            elif unit_match and peak_inpatients_match and qualifying_outpatients_match:
                peak_inpatients = float(peak_inpatients_match[0])
                qualifying_outpatients = float(qualifying_outpatients_match[0])
                unit1 = unit_match[0].lower()

                if unit1 in ['meter', 'm', 'meter^2', 'm^2']:
                    # Calculate outdoor area in square meters
                    required_outdoor_area = math.ceil(0.5 * (0.75 * peak_inpatients) + 0.5 * (0.75 * qualifying_outpatients))
                    return f"Required outdoor area: {math.ceil(required_outdoor_area)} m²"

                elif unit1 in ['foot', 'ft', 'foot^2', 'ft^2']:
                    # Calculate outdoor area in square feet
                    required_outdoor_area = math.ceil(5 * (0.75 * peak_inpatients) + 5 * (0.75 * qualifying_outpatients))
                    return f"Required outdoor area: {math.ceil(required_outdoor_area)} ft²"

                else:
                    return "Invalid unit for area. Please specify either feet or meters."

            else:
                return "Invalid input for outdoor area. Please specify 'Area unit', 'Peak inpatients', and 'Qualifying outpatients'."

        except ValueError:
            logging.error("Value error in outdoor area calculation.")
            return "Invalid input for peak inpatients or qualifying outpatients. Please specify correct numbers."
            
    def process_air_volume_before_occupancy(self):
        """Process the calculation for air volume needed before occupancy."""
        length_width_match = self.matches.get('length_widthh')
        area_match = self.matches.get('area')

        try:
        # Case 1: Calculation based on length and width
            if length_width_match:
                length = float(length_width_match[0] or length_width_match[6])
                width = float(length_width_match[2] or length_width_match[4])
                length_unit = length_width_match[1] or length_width_match[5]
                width_unit = length_width_match[3] or length_width_match[7]
                # Normalize units to lowercase
                length_unit = length_unit.lower()
                width_unit = width_unit.lower()


                if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                    area = length * width
                    air_volume = math.ceil(area * 14000)  # Air volume in ft³
                    return f"Air volume needed before occupancy: {air_volume} ft³"

                elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                    area = length * width
                    air_volume = math.ceil(area * 4267140)  # Air volume in liters
                    return f"Air volume needed before occupancy: {air_volume} l"

                else:
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."

            # Case 2: Calculation based on area
            elif area_match:
                area = float(area_match[0])
                unit = area_match[1].lower()

                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    air_volume = math.ceil(area * 14000)  # Air volume in ft³
                    return f"Air volume needed before occupancy: {air_volume} ft³"

                elif unit in ['meter', 'm', 'meter^2', 'm^2']:
                    air_volume = math.ceil(area * 4267140)  # Air volume in liters
                    return f"Air volume needed before occupancy: {air_volume} l"

                else:
                    return "Invalid unit for area. Please specify either feet or meters."

            else:
                return "Invalid input for air volume calculation. Please specify area with unit or length and width with unit."

        except ValueError:
            logging.error("Value error in air volume calculation.")
            return "Invalid input for length, width, or area. Please specify correct numbers."

    def process_air_volume_to_complete(self):
        """Process the calculation for air volume needed during occupancy to complete."""
        length_width_match = self.matches.get('length_widthh')
        area_match = self.matches.get('area')

        try:
            if length_width_match:
            # Extract length and width, checking both possible groupings
                length = float(length_width_match[0] or length_width_match[6])  # Match either 'length' or 'length2'
                width = float(length_width_match[2] or length_width_match[4])   # Match either 'width' or 'width2'
                length_unit = length_width_match[1] or length_width_match[5]    # Match either 'length_unit' or 'length_unit2'
                width_unit = length_width_match[3] or length_width_match[7]     # Match either 'width_unit' or 'width_unit2'

                # Normalize units to lowercase
                length_unit = length_unit.lower()
                width_unit = width_unit.lower()

                # Ensure both units are the same
                if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                    area = length * width
                    air_volume = math.ceil(area * 10500)  # Air volume in ft³
                    return f"Air volume needed during occupancy to complete: {air_volume} ft³"

                elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                    area = length * width
                    air_volume = math.ceil(area * 3200880)  # Air volume in liters
                    return f"Air volume needed during occupancy to complete: {air_volume} l"

                else:
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."

            elif area_match:
                # Handle case where only area is provided
                area = float(area_match[0])
                unit = area_match[1].lower()

                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    air_volume = math.ceil(area * 10500)  # Air volume in ft³
                    return f"Air volume needed during occupancy to complete: {air_volume} ft³"

                elif unit in ['meter', 'm', 'meter^2', 'm^2']:
                    air_volume = math.ceil(area * 3200880)  # Air volume in liters
                    return f"Air volume needed during occupancy to complete: {air_volume} l"

                else:
                    return "Invalid unit for area. Please specify either feet or meters."

            else:
                return "Invalid input for air volume calculation. Please specify area with unit or length and width with unit."

        except ValueError:
            logging.error("Value error in air volume calculation.")
            return "Invalid input for length, width, or area. Please specify correct numbers."

    def process_air_volume_during_occupancy(self):
        """Process the calculation for air volume needed during occupancy."""
        length_width_match = self.matches.get('length_widthh')
        area_match = self.matches.get('area')

        try:
            if length_width_match:
            # Extract length and width, checking both possible groupings
                length = float(length_width_match[0] or length_width_match[6])  # Match either 'length' or 'length2'
                width = float(length_width_match[2] or length_width_match[4])   # Match either 'width' or 'width2'
                length_unit = length_width_match[1] or length_width_match[5]    # Match either 'length_unit' or 'length_unit2'
                width_unit = length_width_match[3] or length_width_match[7]     # Match either 'width_unit' or 'width_unit2'

                # Normalize units to lowercase
                length_unit = length_unit.lower()
                width_unit = width_unit.lower()

                # Ensure both units are the same
                if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                    area = length * width
                    air_volume = math.ceil(area * 3500)  # Air volume in ft³
                    return f"Air volume needed during occupancy: {air_volume} ft³"

                elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                    area = length * width
                    air_volume = math.ceil(area * 1066260)  # Air volume in liters
                    return f"Air volume needed during occupancy: {air_volume} l"

                else:
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."

            elif area_match:
                # Handle case where only area is provided
                area = float(area_match[0])
                unit = area_match[1].lower()

                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    air_volume = math.ceil(area * 3500)  # Air volume in ft³
                    return f"Air volume needed during occupancy: {air_volume} ft³"

                elif unit in ['meter', 'm', 'meter^2', 'm^2']:
                    air_volume = math.ceil(area * 1066260)  # Air volume in liters
                    return f"Air volume needed during occupancy: {air_volume} l"

                else:
                    return "Invalid unit for area. Please specify either feet or meters."

            else:
                return "Invalid input for air volume calculation. Please specify area with unit or length and width with unit."

        except ValueError:
            logging.error("Value error in air volume calculation.")
            return "Invalid input for length, width, or area. Please specify correct numbers."

    def process_depression_storage(self):
        """Process the calculation of depression storage using the provided formula."""
        fmin_match = self.matches.get('fmin')
        fmax_match = self.matches.get('fmax')
        k_match = self.matches.get('k')
        t_match = self.matches.get('t')

        try:
            # Ensure all necessary values are present for the calculation
            if fmin_match and fmax_match and k_match and t_match:
                fmin = float(fmin_match[0])  # Get fmin value
                fmax = float(fmax_match[0])  # Get fmax value
                k = float(k_match[0])  # Get k (decay factor) value
                t = float(t_match[0])  # Get t (time) value
            
                # Calculate depression storage using the formula Ft = fmin + (fmax - fmin) * e^(-kt)
                depression_storage = fmin + (fmax - fmin) * math.exp(-k * t)
                depression_storage = math.ceil(depression_storage)  # Round to up

                return f"Calculated depression storage: {depression_storage} mm/hr"

            else:
                # Collect missing inputs
                missing_inputs = []
                if not fmin_match:
                    missing_inputs.append("fmin")
                if not fmax_match:
                    missing_inputs.append("fmax")
                if not k_match:
                    missing_inputs.append("k")
                if not t_match:
                    missing_inputs.append("t")

                return f"Missing input for depression storage calculation. Please specify: {', '.join(missing_inputs)}."

        except ValueError:
            logging.error("Value error in depression storage calculation.")
            return "Invalid input values for depression storage calculation. Please specify correct numbers for fmin, fmax, k, and t."

    def process_runoff(self):
        """Process the calculation for runoff, including the calculation of Depression storage if not provided."""
        rainfall_match = self.matches.get('rainfall')
        depression_storage_match = self.matches.get('depression_storage')
        infiltration_match = self.matches.get('infiltration')

        fmin_match = self.matches.get('fmin')
        fmax_match = self.matches.get('fmax')
        k_match = self.matches.get('k')
        t_match = self.matches.get('t')

        try:
            if rainfall_match and infiltration_match:
                rainfall = float(rainfall_match[0])  # Get rainfall value
                infiltration = float(infiltration_match[0])  # Get infiltration value
            
            # Case 1: Depression storage is provided
                if depression_storage_match:
                    depression_storage = float(depression_storage_match[0])
                # Case 2: Depression storage needs to be calculated using the provided equation
                elif fmin_match and fmax_match and k_match and t_match:
                    fmin = float(fmin_match[0])  # Get fmin value
                    fmax = float(fmax_match[0])  # Get fmax value
                    k = float(k_match[0])  # Get k (decay factor) value
                    t = float(t_match[0])  # Get t (time) value
                
                    # Calculate depression storage using the formula Ft = fmin + (fmax - fmin) * e^(-kt)
                    depression_storage = fmin + (fmax - fmin) * math.exp(-k * t)
                    depression_storage = round(depression_storage, 2)  # Round for cleaner output
                    logging.debug(f"Depression storage calculated as {depression_storage} mm/hr")
                else:
                    # If necessary inputs are missing for depression storage calculation
                    missing_inputs = []
                    if not fmin_match:
                        missing_inputs.append("fmin")
                    if not fmax_match:
                        missing_inputs.append("fmax")
                    if not k_match:
                        missing_inputs.append("k")
                    if not t_match:
                        missing_inputs.append("t")

                    return f"Missing input for depression storage calculation. Please specify: {', '.join(missing_inputs)}."
            
                # Calculate runoff: runoff = rainfall - depression storage - infiltration
                runoff = math.ceil(rainfall - depression_storage - infiltration)
                return f"Runoff = {runoff} mm/hr"
            
            elif not rainfall_match and not infiltration_match and not depression_storage_match:
                return "Missing input for runoff calculation. Please specify: Rainfall, depression storage and Infiltration"
            
            elif  rainfall_match and not infiltration_match and not depression_storage_match:
                return "Missing input for runoff calculation. Please specify:  depression storage and Infiltration"
            
            elif  not rainfall_match and not depression_storage_match and  infiltration_match :
                return "Missing input for runoff calculation. Please specify:  depression storage and Rainfall"
            else:
            # Handle missing inputs
                missing_inputs = []
                if not rainfall_match:
                    missing_inputs.append("Rainfall")
                if not infiltration_match:
                    missing_inputs.append("Infiltration")

                return f"Missing input for runoff calculation. Please specify: {', '.join(missing_inputs)}."

        except ValueError:
            logging.error("Value error in runoff calculation.")
            return "Invalid input values for runoff calculation. Please specify correct numbers for Rainfall, Depression Storage, and Infiltration."

    def process_development_percentage(self):
        """Process the calculation for percentage of development on previously developed land."""
        previously_area_match = self.matches.get('previously_area')  # Area of previously developed land
        development_footprint_match = self.matches.get('development_footprint')  # Area of development footprint

        try:
            if previously_area_match and development_footprint_match:
                previously_developed_land = float(previously_area_match[0])  # Get previously developed land area
                development_footprint = float(development_footprint_match[0])  # Get development footprint area

                if development_footprint == 0:
                    return "Area of development footprint cannot be zero."

            # Calculate development percentage
                development_percentage = math.ceil(100 * (previously_developed_land / development_footprint))
                return f"Percentage of development on previously developed land = {development_percentage}%"

            elif not previously_area_match and not development_footprint_match:
                return "Missing input for development percentage calculation. Please specify: Area of previously developed land, and development footprint"
            else:
                # Handle missing inputs
                missing_inputs = []
                if not previously_area_match:
                    missing_inputs.append("Area of previously developed land")
                if not development_footprint_match:
                    missing_inputs.append("Area of development footprint")

                return f"Missing input for development percentage. Please specify: {', '.join(missing_inputs)}."

        
        except ValueError:
            logging.error("Value error in development percentage calculation.")
            return "Invalid input values for development percentage. Please specify correct numbers."

    def process_bicycle_racks(self):
        """Process the calculation for bicycle racks, both long-term and short-term."""
        occupants_match = self.matches.get('occupants')
        area_racks_match = self.matches.get('area_racks')
        long_term_match = self.matches.get('long_term')
        short_term_match = self.matches.get('short_term')
            # Condition 1: Long-term storage (default)
        if long_term_match or not short_term_match:
            if occupants_match:
                try:
                    occupants = float(occupants_match[1])  # Get the number of occupants
                    total_racks = math.ceil(occupants / 20)
                    return f"Total number of bicycle racks required (long-term): {total_racks}"
                except ValueError:
                    logging.error("Invalid value for occupants in long-term bicycle storage calculation.")
                    return "Invalid input for building occupants. Please specify a correct number."
            # Condition 2: Short-term storage
            elif area_racks_match:
                try:
                    area = float(area_racks_match[1])  # Get the area
                    total_racks = math.ceil(area / 500)
                    return f"Total number of bicycle racks required (short-term): {total_racks}"
                except ValueError:
                    logging.error("Invalid value for area in short-term bicycle storage calculation.")
                    return "Invalid input for area. Please specify a correct number."
        return "Invalid input for bicycle racks. Please specify building occupants or area with the appropriate term (long-term or short-term)."

    def process_energy_performance(self):
        """Process the calculation for percentage improvement in energy consumption."""
        baseline_energy_match = self.matches.get('baseline_energy')
        proposed_energy_match = self.matches.get('proposed_energy')

        if baseline_energy_match and proposed_energy_match:
            try:
                baseline_energy = float(baseline_energy_match[0])
                proposed_energy = float(proposed_energy_match[0])
                
                if baseline_energy == 0:
                    return "Baseline Annual Energy Consumption cannot be zero."

                # Calculate percentage improvement
                improvement = math.ceil(((baseline_energy - proposed_energy) / baseline_energy) * 100)
                return f"Percentage Improvement in Energy Consumption: {improvement}%"
            except ValueError:
                logging.error("Invalid input values for energy consumption.")
                return "Invalid input for energy consumption. Please specify correct numbers."
        elif baseline_energy_match and not proposed_energy_match:
            return "Invalid input for Energy performance. Please specify proposed energy."
        elif not baseline_energy_match and proposed_energy_match:
            return "Invalid input for Energy performance. Please specify baseline energy."
        else:
            return "Invalid input for Energy performance. Please specify baseline energy and proposed energy."

    def process_u_value(self):
        """Process the calculation for U-value."""
        R_value_match = self.matches.get('R_value')
        material_thickness_match = self.matches.get('material_thickness')
        thermal_conductivity_match = self.matches.get('thermal_conductivity')

        if R_value_match:
            try:
                R_value = float(R_value_match[0])
                
                if R_value == 0:
                    return "R-value cannot be zero."

                # Calculate U-value
                U_value = math.ceil(1 / R_value)
                return f"U-value = {U_value} (W/m²·K)"
            except ValueError:
                logging.error("Value error in U-value calculation.")
                return "Invalid input values for R-value. Please specify correct numbers."
        elif material_thickness_match and thermal_conductivity_match:
            try:
                material_thickness = float(material_thickness_match[0])
                thermal_conductivity = float(thermal_conductivity_match[0])
                
                if thermal_conductivity == 0:
                    return "Thermal conductivity cannot be zero."

                # Calculate R-value
                R_value = math.ceil(material_thickness / thermal_conductivity)
                # Calculate U-value
                U_value = math.ceil(1 / R_value)
                return f"U-value = {U_value} (W/m²·K)"
            except ValueError:
                logging.error("Value error in U-value calculation.")
                return "Invalid input values for material thickness or thermal conductivity. Please specify correct numbers."
        elif material_thickness_match and not thermal_conductivity_match:
            return "Invalid input for U-value calculation. Please specify 'Thermal Conductivity'."
        elif not material_thickness_match and thermal_conductivity_match:
            return "Invalid input for U-value calculation. Please specify 'Material Thickness'." 
        else:
            return "Invalid input for U-value calculation. Please specify either 'R-value' or both 'Material Thickness' and 'Thermal Conductivity'."

    def process_r_value(self):
        """Process the calculation for R-value."""
        material_thickness_match = self.matches.get('material_thickness')
        thermal_conductivity_match = self.matches.get('thermal_conductivity')

        if material_thickness_match and thermal_conductivity_match:
            try:
                # Extract and convert values
                material_thickness = float(material_thickness_match[0])
                thermal_conductivity = float(thermal_conductivity_match[0])
                
                if thermal_conductivity == 0:
                    return "Thermal conductivity cannot be zero."

                # Calculate R-value
                R_value = math.ceil(material_thickness / thermal_conductivity)
                return f"R-value = {R_value} (m²·K/W)"
            except ValueError:
                logging.error("Value error in R-value calculation.")
                return "Invalid input values for material thickness or thermal conductivity. Please specify correct numbers."
        elif material_thickness_match and not thermal_conductivity_match:
            return "Invalid input for R-value calculation. Please specify 'Thermal Conductivity'."
        elif not material_thickness_match and thermal_conductivity_match:
            return "Invalid input for R-value calculation. Please specify 'Material Thickness'."
        else:
            return "Invalid input for R-value calculation. Please specify both 'Material Thickness' and 'Thermal Conductivity'."

    def process_shw(self):
        """Process the calculation for SHW (Solar Hot Water) percentage."""
        shw_generated_match = self.matches.get('shw_generated')
        hot_water_demand_match = self.matches.get('hot_water_demand')

        if shw_generated_match and hot_water_demand_match:
            try:
                shw_generated = float(shw_generated_match[0])
                hot_water_demand = float(hot_water_demand_match[0])

                if hot_water_demand == 0:
                    return "Annual hot water demand cannot be zero."

                # Calculate percentage of hot water demand provided by SHW
                percentage_shw = math.ceil((shw_generated / hot_water_demand) * 100)
                return f"{percentage_shw}% of hot water demand is provided by SHW panels"
            except ValueError:
                logging.error("Value error in SHW calculation.")
                return "Invalid input for hot water generated or demand. Please specify correct numbers."
        elif shw_generated_match and not hot_water_demand_match:
            return "Invalid input for SHW calculation. Please specify 'Annual hot water demand'."
        elif not shw_generated_match and hot_water_demand_match:
            return "Invalid input for SHW calculation. Please specify 'Annual hot water generated by SHW panels'."
        else:
            return "Invalid input for SHW calculation. Please specify both 'Annual hot water generated by SHW panels' and 'Annual hot water demand'."

    def process_renewable_energy(self):
        """Process the calculation for Renewable Energy percentage."""
        pv_energy_generated_match = self.matches.get('pv_energy_generated')
        proposed_energy_consumption_match = self.matches.get('proposed_energy_consumption')
        annual_energy_generated_match = self.matches.get('annual_energy_generated')
        community_energy_consumed_match = self.matches.get('community_energy_consumed')

        if pv_energy_generated_match and proposed_energy_consumption_match:
            try:
                pv_energy_generated = float(pv_energy_generated_match[0])
                proposed_energy_consumption = float(proposed_energy_consumption_match[0])

                if proposed_energy_consumption == 0:
                    return "Proposed building annual energy consumption cannot be zero."

                # Calculate percentage of renewable energy provided by PV system
                percentage_renewable_energy = math.ceil((pv_energy_generated / proposed_energy_consumption) * 100)
                return f"{percentage_renewable_energy}% of the building's energy is provided by the PV system"
            except ValueError:
                logging.error("Value error in Renewable Energy calculation.")
                return "Invalid input for PV energy generated or proposed energy consumption. Please specify correct numbers."
        elif annual_energy_generated_match and community_energy_consumed_match:
            try:
                annual_energy_generated = float(annual_energy_generated_match[0])
                community_energy_consumed = float(community_energy_consumed_match[0])

                if community_energy_consumed == 0:
                    return "Annual community energy consumption cannot be zero."

                # Calculate percentage of renewable energy for the community
                renewable_energy_percentage = math.ceil((annual_energy_generated / community_energy_consumed) * 100)
                return f"Renewable Energy = {renewable_energy_percentage}%"
            except ValueError:
                logging.error("Value error in Renewable Energy calculation.")
                return "Invalid input for renewable energy generated or community energy consumption. Please specify correct numbers."
        elif pv_energy_generated_match and not proposed_energy_consumption_match:
            return "Invalid input for Renewable Energy calculation. Please specify 'Proposed building annual energy consumption'."
        elif not pv_energy_generated_match and proposed_energy_consumption_match:
            return "Invalid input for Renewable Energy calculation. Please specify 'Energy generated by PV'."
        elif not annual_energy_generated_match and community_energy_consumed_match:
            return "Invalid input for Renewable Energy calculation. Please specify 'Annual energy generated'."
        elif not community_energy_consumed_match and annual_energy_generated_match  :
            return "Invalid input for Renewable Energy calculation. Please specify 'Community energy consumption'."
        else:
            return "Invalid input for Renewable Energy calculation. Please specify both 'Energy generated by PV' and 'Proposed building annual energy consumption', or both 'Annual energy generated' and 'Community energy consumption'."

    def process_occupant_density(self):
        """Process the calculation for occupant density."""
        designed_occupancy_match = self.matches.get('designed_occupancy')
        expected_occupancy_match = self.matches.get('expected_occupancy')
        area_match = self.matches.get('areaa')
        length_width_match = self.matches.get('length_width')

        # Check if either designed maximum occupancy or expected occupancy is provided
        occupancy = None
        if designed_occupancy_match:
            occupancy = float(designed_occupancy_match[0])
        elif expected_occupancy_match:
            occupancy = float(expected_occupancy_match[0])

        # If neither occupancy type is provided, return an error
        if occupancy is None:
            return "Invalid input for occupant density. Please specify either 'Designed Maximum Occupancy' or 'Expected Occupancy' with area in meter square."

        # Handle area inputs
        area = None
        if area_match:
            try:
                area_value = float(area_match[0])
                unit = area_match[1] if area_match[1] else "meter"
                unit = unit.lower()
                # If the unit is in feet, return an error
                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    return "The unit for area must be in meters."
                # If the unit is correct, set the area
                area = area_value
            except ValueError:
                return "Invalid input for area. Please provide correct numbers."
        
        if length_width_match:
            try:
                # Since match.groups() is a tuple, access the values directly via indexing
                length = float(length_width_match[0] or length_width_match[6])
                width = float(length_width_match[2] or length_width_match[4])
                length_unit = length_width_match[1] or length_width_match[5]
                width_unit = length_width_match[3] or length_width_match[7]

                # Check if any unit is in feet
                if length_unit in ['foot', 'ft'] or width_unit in ['foot', 'ft']:
                    return "The unit for length and width must be in meters."

                area = length * width  # Calculate area in square meters
            except ValueError:
             return "Invalid input for length or width. Please provide correct numbers."

        # Ensure area is provided
        if area is None:
            return "Invalid input for area. Please specify 'Area' in square meters, or provide 'Length' and 'Width' in meters."

        # Calculate occupant density
        occupant_density = math.ceil(occupancy / area)
        return f"Occupant Density = {occupant_density} people per square meter"

    def process_size_of_outdoor_space(self):
        """Process the calculation for the size of the outdoor space."""
        total_occupancy_match = self.matches.get('total_occupancy')
        if total_occupancy_match:
            try:
                total_occupancy = float(total_occupancy_match[0])
                Size_of_Outdoor_Space = math.ceil(total_occupancy *0.25)
                return f"{Size_of_Outdoor_Space} m^2"
            except ValueError:
                 return "Invalid input for total occupancy. Please provide correct numbers."
        else:
            return "Invalid input for occupant density. Please specify total occupancy = '<number>'."

    def process_adhesives_sealants(self):
        """Process the calculation for compliant adhesives and sealants."""
        compliant_adhesives_match = re.search(self.patterns["compliant_adhesives"], self.input_text)
        total_adhesives_match = re.search(self.patterns["total_adhesives"], self.input_text)
        if compliant_adhesives_match and total_adhesives_match:
            try:
                weight_compliant = float(compliant_adhesives_match.group(1))
                total_weight = float(total_adhesives_match.group(1))

                if total_weight == 0:
                    return "Total weight of all adhesives and sealants cannot be zero."

                # Calculate the percentage of compliant adhesives and sealants
                percentage_compliant = math.ceil((weight_compliant / total_weight) * 100)
                return f"{percentage_compliant}% of adhesives and sealants are compliant"
            except ValueError:
                logging.error("Value error in compliant adhesives calculation.")
                return "Invalid input values for adhesives and sealants. Please specify correct numbers."
        elif compliant_adhesives_match and not total_adhesives_match:
            return "Invalid input for adhesives and sealants calculation. Please specify  'Total weight'."
        elif not compliant_adhesives_match and  total_adhesives_match:
            return "Invalid input for adhesives and sealants calculation. Please specify  'Weight of adhesives and sealants not exceeding VOC limits'."
        else:
                return "Invalid input for adhesives and sealants calculation. Please specify both 'Weight of adhesives and sealants not exceeding VOC limits' and 'Total weight'."
    
    def process_waste_diverted(self):
        """Process the calculation for % Waste Diverted from Landfill."""
        recycled_match = re.search(self.patterns['recycled'], self.input_text)
        reused_match = re.search(self.patterns['reused'], self.input_text)
        salvaged_match = re.search(self.patterns['salvaged'], self.input_text)
        donated_match = re.search(self.patterns['donated'], self.input_text)
        reclaimed_match = re.search(self.patterns['reclaimed'], self.input_text)
        total_waste_match = re.search(self.patterns['total_waste'], self.input_text)
        # Check if more than one waste management method is provided
        methods_count = sum(bool(match) for match in [recycled_match, reused_match, salvaged_match, donated_match, reclaimed_match])
        if methods_count > 1:
            return "Specify just one of these: recycled, reused, salvaged, donated, or reclaimed."

            # Proceed with calculation if only one method is present
        waste_diverted = None
        if recycled_match:
            waste_diverted = float(recycled_match.group(2))
        elif reused_match:
            waste_diverted = float(reused_match.group(2))
        elif salvaged_match:
            waste_diverted = float(salvaged_match.group(2))
        elif donated_match:
            waste_diverted = float(donated_match.group(2))
        elif reclaimed_match:
            waste_diverted = float(reclaimed_match.group(2))

        if waste_diverted is not None and total_waste_match:
            try:
                total_waste = float(total_waste_match.group(2))

                if total_waste == 0:
                    return "Total amount of waste generated cannot be zero."

                # Calculate the percentage of waste diverted
                percentage_waste_diverted = math.ceil((waste_diverted / total_waste) * 100)
                return f"{percentage_waste_diverted}% of waste is diverted from landfill"
            except ValueError:
                logging.error("Value error in waste diverted calculation.")
                return "Invalid input values for waste calculation. Please specify correct numbers."
        else:
            return "Invalid input for waste diverted calculation. Please specify both 'Amount of waste recycled, reused, salvaged, donated, or reclaimed' and 'Total amount of waste generated'."

    def process_connectivity_index(self):
        """Process the calculation for the Connectivity Index."""
        street_links_match = re.search(self.patterns['street_links'], self.input_text)
        nodes_match = re.search(self.patterns['nodes'], self.input_text)
        if street_links_match and nodes_match:
            try:
                street_links = int(street_links_match.group(1))
                nodes = int(nodes_match.group(1))

                if nodes == 0:
                    return "Number of nodes cannot be zero."

                # Calculate the Connectivity Index
                connectivity_index = math.ceil(street_links / nodes)
                return f"Connectivity Index = {connectivity_index}"
            except ValueError:
                logging.error("Value error in Connectivity Index calculation.")
                return "Invalid input values for street links or nodes. Please specify correct numbers."
        elif street_links_match and not nodes_match:
            return "Invalid input for Connectivity Index calculation. Please specify 'Nodes = <number>'."
        elif not street_links_match and nodes_match:
            return "Invalid input for Connectivity Index calculation. Please specify 'Street links = <number>'."
        else:
            return "Invalid input for Connectivity Index calculation. Please specify both 'Street links = <number>' and 'Nodes = <number>'."

    def process_intersection_density(self):
        """Process the calculation for Intersection Density."""
        intersections_match = re.search(self.patterns['intersections'], self.input_text)
        area_match = re.search(self.patterns['area'], self.input_text)
        length_width_match = re.search(self.patterns['length_width'], self.input_text)
        if intersections_match:
            try:
                intersections = int(intersections_match.group(1))
                area = None

                # Handle area input
                if area_match:
                    try:
                        area_value = float(area_match.group(1))
                        area_unit = area_match.group(2).lower() if area_match.group(2) else None  # Ensure unit is extracted
                            
                        if area_unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                            area = area_value / 10.764  # Convert ft² to m²
                        elif area_unit in ['meter', 'm', 'meter^2', 'm^2']:
                            area = area_value  # Already in m²
                        else:
                            return "Invalid area unit. Please specify the area in either square feet or square meters."
                    except ValueError:
                        return "Invalid input for area. Please specify a correct number."

                # Handle length and width input if area is not available
                if length_width_match and area is None:
                    try:
                        length = float(length_width_match.group('length') or length_width_match.group('length2'))
                        width = float(length_width_match.group('width') or length_width_match.group('width2'))
                        length_unit = length_width_match.group('length_unit') or length_width_match.group('length_unit2')
                        width_unit = length_width_match.group('width_unit') or length_width_match.group('width_unit2')
                            
                        # Convert units to meters for area calculation
                        if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                            area = (length * width) / 10.764  # Convert ft² to m²
                        elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                            area = length * width  # Already in m²
                        else:
                            return "Inconsistent units. Length and width must be in the same unit (feet or meters)."
                    except ValueError:
                        return "Invalid input for length and width. Please specify correct numbers."

                # Ensure area is available for calculation
                if area is None:
                    return "Invalid input for area. Please specify 'Area = <number> m²' or provide 'Length' and 'Width' in meters or feet."

                # Calculate Intersection Density
                intersection_density = math.ceil(intersections / area)
                return f"Intersection Density = {intersection_density} intersections/m²"
            except ValueError:
                logging.error("Value error in Intersection Density calculation.")
                return "Invalid input values for Intersection Density. Please specify correct numbers."
        else:
            return "Invalid input for Intersection Density. Please specify 'Intersections = <number>'."

    def process_continuous_walkway(self):
        """Process the calculation for Continuous Walkway (CW)."""
        continuous_walkway_match = re.search(self.patterns['continuous_walkway_on_both'], self.input_text)
        all_walkways_match = re.search(self.patterns['all_walkways'], self.input_text)

        if continuous_walkway_match and all_walkways_match:
            try:
                # Extract continuous walkway and all walkways length
                continuous_walkway_length = float(continuous_walkway_match.group(1))
                all_walkways_length = float(all_walkways_match.group(1))

                # Check if all walkways length is zero
                if all_walkways_length == 0:
                    return "Total length of all walkways cannot be zero."

                # Calculate CW percentage
                CW = math.ceil((continuous_walkway_length / all_walkways_length) * 100)
                return f"Continuous Walkway (CW) = {CW}%"
            except ValueError:
                logging.error("Value error in Continuous Walkway calculation.")
                return "Invalid input values for continuous walkways or all walkways. Please specify correct numbers."
        elif continuous_walkway_match and not all_walkways_match:
            return "Invalid input for Continuous Walkway calculation. Please specify 'All walkways'."
        elif not continuous_walkway_match and  all_walkways_match:
            return "Invalid input for Continuous Walkway calculation. Please specify 'Linear length on both sides'."
        else:
            return "Invalid input for Continuous Walkway calculation. Please specify both 'Linear length on both sides' and 'All walkways'."

    def process_Floor_Area_Ratio(self):
        """ process the calculation for Floor Area Ratio (FAR)."""
        gfa_match = re.search(self.patterns['gfa'],self.input_text)
        site_area_match = re.search(self.patterns['site_area'],self.input_text)

        if gfa_match and site_area_match:
            try:
                gfa_value = float(gfa_match.group(3))
                site_area_value = float(site_area_match.group(1))

                #check if site area is zero
                if site_area_value==0:
                    return "Total site area cannot be zero."

                # Calculate CW percentage
                FAR = math.ceil((gfa_value/site_area_value)*100)
                return f"Floor Area Ratio (FAR) = {FAR}%"
            except ValueError:
                logging.error("Value error in Floor Area Ratio.")
                return "Invalid input values for Total gross floor area or Total site area. Please specify correct numbers."
        elif gfa_match and not site_area_match:
            return "Invalid input for Floor Area Ratio.Please specify 'total site area'."
        elif not gfa_match and site_area_match:
            return "Invalid input for Floor Area Ratio.Please specify 'gross floor area'."
        else:
            return "Invalid input for Floor Area Ratio.Please specify 'gross floor area' and 'total site area'."

    def process_seer(self):
        """ process the calculation for SEER."""
        cooling_provided_match = re.search(self.patterns['cooling_provided'],self.input_text)
        energy_consumed_match =  re.search(self.patterns['energy_consumed'],self.input_text)

        if cooling_provided_match and energy_consumed_match:
            try:
                cooling_provided_value = float(cooling_provided_match.group(1))
                energy_consumed_value = float(energy_consumed_match.group(1))

                #Check if Energy consumed is zero
                if energy_consumed_value==0:
                    return "Amount of energy consumed cannot be zero."

                ## Calculate SEER
                seer = math.ceil((cooling_provided_value / energy_consumed_value) * 100)
                return f"SEER = {seer}%"
            except ValueError:
                logging.error("Value error in SEER calculation.")
                return "Invalid input values for cooling provided or energy consumed. Please specify correct numbers."
        elif cooling_provided_match and not energy_consumed_match:
            return "Invalid input for SEER calculation. Please specify 'Energy consumed'."
        elif not cooling_provided_match and energy_consumed_match:
             return "Invalid input for SEER calculation. Please specify 'Cooling provided'."
        else:
            return "Invalid input for SEER calculation. Please specify both 'Cooling provided' and 'Energy consumed'."

    def process_compliant_paints_coatings(self):
        """ process the calculation for compliant paints and coatings."""
        compliant_paints_match=re.search(self.patterns['compliant_paints'],self.input_text)
        total_paints_match=re.search(self.patterns['total_paints'],self.input_text)

        if  compliant_paints_match and total_paints_match:
            try:
                weight_compliant = float(compliant_paints_match.group(1))
                total_weight = float(total_paints_match.group(1))

                if total_weight == 0:
                    return "Total weight of all paints and coatings cannot be zero."

                # Calculate the percentage of compliant paints and coatings
                percentage_compliant = math.ceil((weight_compliant / total_weight) * 100)
                return f"{percentage_compliant}% of paints and coatings are compliant"
            except ValueError:
                logging.error("Value error in compliant paints calculation.")
                return "Invalid input values for paints and coatings. Please specify correct numbers."
        elif compliant_paints_match and not total_paints_match:
            return "Invalid input for compliant paints and coatings. Please specify 'Total weight'."
        elif not compliant_paints_match and total_paints_match:
            return "Invalid input for compliant paints and coatings. Please specify 'Weight not exceeding VOC'."
        else:
            return "Invalid input for compliant paints and coatings. Please specify both 'Weight not exceeding VOC' and 'Total weight'."

    def process_dwelling_building_size(self):
        """Process the calculation of Dwelling-Size of Private and Communal Outdoor Space."""
        building_type_matchh = self.matches.get('building_typee')
        occupants_match = self.matches.get('occupantss')
        total_occupancy_match = self.matches.get('total_occupancy')
        Dwelling_building_match = self.matches.get('Dwelling_building_size')

         # Add logging to debug extracted matches
        logging.debug(f"Building type: {building_type_matchh}")  # Log building type match
        logging.debug(f"Dwelling size: {Dwelling_building_match}")  # Log dwelling size match


        try:
            # Check if building_typee and Dwelling_building_size are properly matched
            if building_type_matchh:
                building_type = building_type_matchh[0].lower()  # Ensure lowercase comparison
            else:
                return "Please specify 'individual' or 'multi-residential'."

            if Dwelling_building_match:
                dwelling_size = Dwelling_building_match[0].lower()  # Ensure lowercase comparison
            else:
                return "Please specify 'communal' or 'private'."

            # Case 1: Individual Dwelling - Size of Private
            if building_type == "individual" and dwelling_size == "private":
                if occupants_match:
                    persons = int(occupants_match[1])  # Extract number of occupants
                    if persons <= 2:
                        return f"Individual Dwelling - Size of Private: 5 m²"
                    else:
                        return f"Individual Dwelling - Size of Private: {persons + 3} m²"
                else:
                    return "Please specify 'occupants' for the individual dwelling."

            # Case 2: Multi-Residential Building - Size of Private
            elif building_type == "multi-residential" and dwelling_size == "private":
                if occupants_match:
                    persons = int(occupants_match[1])  # Extract number of occupants
                    if persons <= 2:
                        return f"Multi-Residential Building - Size of Private: 5 m²"
                    else:
                        return f"Multi-Residential Building - Size of Private: {persons + 3} m²"
                else:
                    return "Please specify 'people' for the multi-residential building."

            # Case 3: Multi-Residential Building - Size of Communal Outdoor Space
            elif building_type == "multi-residential" and dwelling_size == "communal" :
                if total_occupancy_match:
                    total_occupancy = int(total_occupancy_match[0])  # Extract total occupancy
                    communal_space = math.ceil(total_occupancy * 0.25)  # Size of Outdoor Space
                    return f"Multi-Residential Building - Size of Communal Outdoor Space: {communal_space} m²"
                else:
                    return "Please specify 'total occupancy' for the multi-residential building."

            else:
                return "Invalid building type or dwelling size."
        except ValueError:
            logging.error("Value error in Dwelling-Size of Private or Communal Outdoor Space calculation.")
            return "Invalid input for occupants or total occupancy. Please specify correct numbers."
            
    def process(self):
        """Main method to process intents and return results."""
        if self.intents.get('long_term_storage'):
            return self.process_long_term_storage()
        elif self.intents.get('short_term_storage'):
            return self.process_short_term_storage()
        elif self.intents.get('shower_facilities'):
            return self.process_shower_facilities()
        elif self.intents['preferred_spaces']:
            return self.process_preferred_spaces()
        elif self.intents['fueling_stations']:
            return self.process_fueling_stations()
        elif self.intents['restoration_area']:
            return self.process_restoration_area()
        elif self.intents['vegetated_space']:
            return self.process_vegetated_space()
        elif self.intents['open_space']:
            required_open_space = self.process_required_open_space()
            if required_open_space:
                return f"Required open space ≥ {required_open_space}% of total site area"
            else:
                return "Invalid input for required open space please specify 'Total site area = <number>'."
        elif self.intents['outdoor_area']:
            return self.process_outdoor_area()
        elif self.intents['air_volume_before_occupancy']:
            return self.process_air_volume_before_occupancy()
        elif self.intents['air_volume_during_occupancy']:
            return self.process_air_volume_during_occupancy()
        elif self.intents['air_volume_to_complete']:
            return self.process_air_volume_to_complete()
        elif self.intents['Runoff']:
            return self.process_runoff()
        elif self.intents['Depression storage']:
            return self.process_depression_storage()
        elif self.intents['development_percentage']:
            return self.process_development_percentage()
        elif self.intents['bicycle_racks']:
            return self.process_bicycle_racks()
        elif self.intents['energy_performance']:
            return self.process_energy_performance()
        elif self.intents['u_value']:
            return self.process_u_value()
        elif self.intents['r_value']:
            return self.process_r_value()
        elif self.intents['shw']:
            return self.process_shw()
        elif self.intents['renewable_energy']:
            return self.process_renewable_energy()
        elif self.intents['occupant_density']:
            return self.process_occupant_density()
        elif  self.intents['size_of_outdoor_space']:
            return self.process_size_of_outdoor_space()
        elif self.intents['adhesives_sealants_intent']:
            return self. process_adhesives_sealants()
        elif self.intents['waste_diverted_intent']:
            return self.process_waste_diverted()
        elif self.intents['connectivity_index_intent']:
            return self.process_connectivity_index()
        elif self.intents['intersection_density_intent']:
            return self.process_intersection_density()
        elif self.intents['continuous_walkway_intent']:
            return self.process_continuous_walkway()
        elif self.intents['far']:
            return self.process_Floor_Area_Ratio()
        elif self.intents['seer']:
            return self.process_seer()
        elif self.intents['compliant_paints']:
            return self.process_compliant_paints_coatings()
        elif self.intents['dwelling_building_size']:
            return self.process_dwelling_building_size()
        elif not any(char.isdigit() for char in self.input_text):
            return "No valid number in the response"
        # Add more processing for other intents...
        return "No valid numerical data found for required calculation"
        # Example response for debugging
        return f"Processed input: {self.input_text}"
