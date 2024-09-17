import re
import logging
import math

def process_input(input_text: str) -> str:
    # Regex patterns for detecting building type, occupants, dwelling units, peak visitors, and area
    building_type_pattern = r"(commercial|institutional|residential|retail)"
    occupants_pattern = r"(regular\s+building\s+occupants|residents|people)\s*=\s*(\d+)"
    dwelling_units_pattern = r"number\s*of\s*dwelling\s*units\s*=\s*(\d+)"
    peak_visitors_pattern = r"peak\svisitors\s*=\s*([\d.]+)"
    peak_inpatients_pattern = r"peak\sinpatients\s*=\s*([\d.]+)"
    qualifying_outpatients_pattern = r"qualifying\soutpatients\s*=\s*([\d.]+)"
    baseline_energy_pattern = r"(?i)\b(?:baseline\s+(?:annual\s+)?energy)\s*=\s*([\d.]+)"
    proposed_energy_pattern = r"(?i)\b(?:proposed\s+(?:annual\s+)?energy)\s*=\s*([\d.]+)"

    # Area patterns with unit specifications
    unit_pattern = r"(foot|ft|feet|foot2|ft2|feet2|m|meter|meter2|m2)"
    
    # Area patterns with unit specifications
    area_pattern = r"(\s*floor\s*area|floor\s*area|building\s*area|area)\s*=\s*([\d.]+)\s*(foot|ft|foot\^2|ft\^2|meter|m|meter\^2|m\^2)"
    
    # Length and width patterns with unit specifications
    length_width_pattern = (
        r"(?:length\s*=\s*(?P<length>[\d.]+)\s*(?P<length_unit>foot|ft|meter|m)\s*(?:,|and)?\s*width\s*=\s*(?P<width>[\d.]+)\s*(?P<width_unit>foot|ft|meter|m)|"
        r"width\s*=\s*(?P<width2>[\d.]+)\s*(?P<width_unit2>foot|ft|meter|m)\s*(?:,|and)?\s*length\s*=\s*(?P<length2>[\d.]+)\s*(?P<length_unit2>foot|ft|meter|m))"
    )
    
    # Total parking space pattern
    Total_parking_space_pattern = r"(Total\s*parking\s*space|Total\s*space|Total\s*spaces|Total\s*parking\s*spaces)\s*=\s*(\d+)"

    # Restoration and site area patterns
    restoration_area_pattern = r"Restoration\s*area\s*=\s*([\d.]+)"
    disturbed_area_pattern = r"Total\s*previously\s*disturbed\s*site\s*area\s*=\s*([\d.]+)"
    
    # Total site area and required open space patterns
    Required_open_space_pattern = r"(required\s*open\s*space|open\s*space)\s*=\s*([\d.]+)"
    total_site_area_pattern = r"Total\s*site\s*area\s*=\s*([\d.]+)"

    # patterns for runoff equation
    rainfall_pattern = r"rainfall\s*=\s*([\d.]+)(?:\s*(mm/hr|mm))?"
    depression_storage_pattern = r"depression\s*storage\s*=\s*([\d.]+)(?:\s*(mm/hr|mm))?"
    infiltration_pattern = r"infiltration\s*=\s*([\d.]+)(?:\s*(mm/hr|mm))?"
    # pattern for Previously Developed Land
    previously_area_pattern = r"Area\s*of\s*previously\s*developed\s*land\s*=\s*([\d.]+)"
    development_footprint_pattern = r"development\s*footprint\s*=\s*([\d.]+)"
    
    #patterns for long and short-term and area for bicycle racks,and for R-value
    long_term_pattern = r"long\s*term\s*=\s*([\d]+)"
    short_term_pattern = r"short\s*term\s*=\s*([\d]+)"
    area_racks_pattern = r"(area|floor|building)\s*=\s*([\d.]+)"
    material_thickness_pattern = r"material\s*thickness\s*=\s*([\d.]+)"
    thermal_conductivity_pattern = r"thermal\s*conductivity\s*=\s*([\d.]+)"
    R_value_pattern = r"(?i)r\s*value\s*=\s*([\d.]+)"

     # New SHW-related regex patterns
    shw_generated_pattern = r"annual\s*hot\s*water\s*generated\s*by\s*shw\s*=\s*([\d.]+)"
    hot_water_demand_pattern = r"annual\s*hot\s*water\s*demand\s*=\s*([\d.]+)"
    
    # New regex patterns for Renewable Energy calculation
    pv_energy_generated_pattern = r"energy\s*generated\s*by\s*the\s*pv\s*=\s*([\d.]+)"
    proposed_energy_consumption_pattern = r"proposed\s*annual\s*energy\s*consumption\s*=\s*([\d.]+)"
    
    # New regex patterns for Occupant Density calculation
    designed_occupancy_pattern = r"designed\s*maximum\s*occupancy\s*=\s*(\d+)"
    expected_occupancy_pattern = r"expected\s*occupancy\s*=\s*(\d+)"

    # Regex patterns for the % Compliant Adhesives and Sealants calculation
    compliant_adhesives_pattern = r"weight\s*of\s*adhesives\s*and\s*sealants\s*not\s*exceeding\s*voc\s*=\s*([\d.]+)"
    total_adhesives_pattern = r"total\s*weight\s*=\s*([\d.]+)"

    # Regex patterns for waste diverted from landfill
    recycled_pattern = r"(amount\s*of\s*recycled|recycled)\s*=\s*([\d.]+)"
    reused_pattern = r"(amount\s*of\s*reused|reused)\s*=\s*([\d.]+)"
    salvaged_pattern = r"(amount\s*of\s*salvaged|salvaged)\s*=\s*([\d.]+)"
    donated_pattern = r"(amount\s*of\s*donated|donated)\s*=\s*([\d.]+)"
    reclaimed_pattern = r"(amount\s*of\s*reclaimed|reclaimed)\s*=\s*([\d.]+)"
    total_waste_pattern = r"(total\s*amount\s*of\s*waste\s*generated|total\s*waste)\s*=\s*([\d.]+)"
  
    # Add regex pattern for street links and nodes
    street_links_pattern = r"street\s*links\s*=\s*(\d+)"
    nodes_pattern = r"nodes\s*=\s*(\d+)"
    # Add new regex for Intersection Density
    intersections_pattern = r"intersections\s*=\s*(\d+)"

    # Regex for Continuous Walkway equation
    continuous_walkway__on_both_pattern = r"linear\s*length\s*on\s*both\s*sides\s*=\s*([\d.]+)"
    all_walkways_pattern = r"all\s*walkways\s*=\s*([\d.]+)"

    # Regex for Floor Area Ratio (FAR)
    gfa_pattern = r"(gross\s*(floor\s*)?area|gfa)\s*=\s*([\d.]+)"
    site_area_pattern = r"total\s*site\s*area\s*=\s*([\d.]+)"

    # Regex patterns for detecting cooling provided and energy consumed
    cooling_provided_pattern = r"cooling\s*provided\s*=\s*([\d.]+)"
    energy_consumed_pattern = r"energy\s*consumed\s*=\s*([\d.]+)"

    # Regex patterns for Renewable Energy calculation
    annual_energy_generated_pattern = r"annual\s*energy\s*generated\s*=\s*([\d.]+)"
    community_energy_consumed_pattern = r"community\s*energy\s*consumption\s*=\s*([\d.]+)"

    # Add new regex patterns for compliant paints and coatings
    compliant_paints_pattern = r"weight\s*not\s*exceeding\s*voc\s*=\s*([\d.]+)"
    total_paints_pattern = r"total\s*weight\s*=\s*([\d.]+)"
   
    # Search for intents in the user input
    long_term_intent = "long-term bicycle storage" in input_text
    short_term_intent = "short-term bicycle storage" in input_text
    shower_facilities_intent = any(phrase in input_text.lower() for phrase in ["shower facilities", "shower", "shower facility"])
    number_Preferred_spaces_intent = any(phrase in input_text.lower() for phrase in ["preferred space", "preferred spaces", "required number of preferred spaces", "required number of preferred space"])
    fueling_stations_intent = any(phrase in input_text.lower() for phrase in ["fueling stations", "fuel stations", "required number of fueling stations", "required number of fuel stations"])
    restoration_area_intent = any(phrase in input_text.lower() for phrase in ["percentage of restoration area", "restoration area percentage"])
    open_space_intent = any(phrase in input_text.lower() for phrase in ["required open space", "open space requirement"])
    vegetated_space_intent = "vegetated space" in input_text
    outdoor_area_intent = any(phrase in input_text.lower() for phrase in ["required outdoor area", "outdoor area requirement", "outdoor space"])
    air_volume_intent_before_occupancy = any (phrase in input_text.lower() for phrase in [ "air volume before occupancy", "flush out before occupancy"])
    air_volume_intent_during_occupancy = any (phrase in input_text.lower() for phrase in [ "air volume during occupancy", "flush out during occupancy"])
    air_volume_intent_to_complete = any (phrase in input_text.lower() for phrase in [ "air volume during occupancy to complete", "flush out to complete"])
     # intent for runoff calculation
    runoff_intent = any(phrase in input_text.lower() for phrase in ["runoff", "Expected runoff","run off"])
    # Intent for % of development on previously developed land
    development_percentage_intent = any(phrase in input_text.lower() for phrase in ["previously developed land", "percentage of previously developed land"])
    Bicycle_racks_intent = any(phrase in input_text.lower() for phrase in ["Number of bicycle racks required","total of bicycle racks","bicycle racks"])
    Energy_performance_intent = any(phrase in input_text.lower() for phrase in["energy performance","energy improvement"])
    R_value_intent = any(phrase in input_text.lower() for phrase  in["r-value", "r value"])
    U_value_intent = any(phrase in input_text.lower() for phrase  in["u-value", "u value"])
    # Intent for Intersection Density
    intersection_density_intent = "intersection density" in input_text.lower()
    # SHW Intent
    shw_intent = "hot water demand provided by shw" in input_text.lower()
    renewable_energy_intent = "renewable energy" in input_text.lower()
    # Intent flag for Occupant Density
    occupant_density_intent = "occupant density" in input_text.lower()
    # Add intent for compliant adhesives and sealants
    adhesives_sealants_intent = "compliant adhesives and sealants" in input_text.lower()
    # Intent for waste diverted from landfill
    waste_diverted_intent = "waste diverted from landfill" in input_text.lower()
    # Intent for connectivity index calculation
    connectivity_index_intent = "connectivity index" in input_text.lower()
    # Intent for Continuous Walkway
    continuous_walkway_intent = any(phrase in input_text.lower() for phrase in ["continuous walkway", "cw"])
    # Intent for Floor Area Ratio (FAR)
    far_intent = any(phrase in input_text.lower() for phrase in["floor area ratio","far"])
    # Intent flag for SEER calculation
    seer_intent = "seer" in input_text.lower()
    # Intent for compliant paints
    compliant_paints_intent = "compliant paints and coatings"  in input_text.lower()

    
    # Search for building type, number of occupants, dwelling units, peak visitors, and area
    building_type_match = re.search(building_type_pattern, input_text, re.IGNORECASE)
    occupants_match = re.search(occupants_pattern, input_text, re.IGNORECASE)
    dwelling_units_match = re.search(dwelling_units_pattern, input_text, re.IGNORECASE)
    peak_visitors_match = re.search(peak_visitors_pattern, input_text, re.IGNORECASE)
    area_match = re.search(area_pattern, input_text, re.IGNORECASE)
    length_width_match = re.search(length_width_pattern, input_text, re.IGNORECASE)
    Total_parking_match = re.search(Total_parking_space_pattern, input_text, re.IGNORECASE)
    restoration_area_match = re.search(restoration_area_pattern, input_text, re.IGNORECASE)
    disturbed_area_match = re.search(disturbed_area_pattern, input_text, re.IGNORECASE)
    total_site_area_match = re.search(total_site_area_pattern, input_text, re.IGNORECASE)
    required_open_space_match = re.search(Required_open_space_pattern, input_text, re.IGNORECASE)
    qualifying_outpatients_match = re.search(qualifying_outpatients_pattern, input_text, re.IGNORECASE)
    peak_inpatients_match = re.search(peak_inpatients_pattern, input_text, re.IGNORECASE)
    unit_match = re.search(unit_pattern, input_text, re.IGNORECASE)
    rainfall_match = re.search(rainfall_pattern, input_text, re.IGNORECASE)
    depression_storage_match = re.search(depression_storage_pattern, input_text, re.IGNORECASE)
    infiltration_match = re.search(infiltration_pattern, input_text, re.IGNORECASE)
    previously_area_match = re.search(previously_area_pattern,input_text, re.IGNORECASE)
    development_footprint_match = re.search(development_footprint_pattern,input_text, re.IGNORECASE)
    long_term_match = re.search(long_term_pattern,input_text, re.IGNORECASE)
    short_term_match = re.search(short_term_pattern,input_text, re.IGNORECASE)
    area_racks_match = re.search(area_racks_pattern,input_text, re.IGNORECASE)
    baseline_energy_match = re.search(baseline_energy_pattern, input_text, re.IGNORECASE)
    proposed_energy_match = re.search(proposed_energy_pattern, input_text, re.IGNORECASE)
    material_thickness_match = re.search(material_thickness_pattern, input_text, re.IGNORECASE)
    thermal_conductivity_match = re.search(thermal_conductivity_pattern, input_text, re.IGNORECASE)
    R_value_match = re.search(R_value_pattern, input_text, re.IGNORECASE)
    shw_generated_match = re.search(shw_generated_pattern, input_text, re.IGNORECASE)
    hot_water_demand_match = re.search(hot_water_demand_pattern, input_text, re.IGNORECASE)
    pv_energy_generated_match = re.search(pv_energy_generated_pattern, input_text, re.IGNORECASE)
    proposed_energy_consumption_match = re.search(proposed_energy_consumption_pattern, input_text, re.IGNORECASE)
    designed_occupancy_match = re.search(designed_occupancy_pattern, input_text, re.IGNORECASE)
    expected_occupancy_match = re.search(expected_occupancy_pattern, input_text, re.IGNORECASE)
    compliant_adhesives_match = re.search(compliant_adhesives_pattern, input_text, re.IGNORECASE)
    total_adhesives_match = re.search(total_adhesives_pattern, input_text, re.IGNORECASE)
    recycled_match = re.search(recycled_pattern, input_text, re.IGNORECASE)
    reused_match = re.search(reused_pattern, input_text, re.IGNORECASE)
    salvaged_match = re.search(salvaged_pattern, input_text, re.IGNORECASE)
    donated_match = re.search(donated_pattern, input_text, re.IGNORECASE)
    reclaimed_match = re.search(reclaimed_pattern, input_text, re.IGNORECASE)
    total_waste_match = re.search(total_waste_pattern, input_text, re.IGNORECASE)
    street_links_match = re.search(street_links_pattern, input_text, re.IGNORECASE)
    nodes_match = re.search(nodes_pattern, input_text, re.IGNORECASE)
    # Search for intersections, length/width, and area
    intersections_match = re.search(intersections_pattern, input_text, re.IGNORECASE)
    continuous_walkway_match = re.search(continuous_walkway__on_both_pattern, input_text, re.IGNORECASE)
    all_walkways_match = re.search(all_walkways_pattern, input_text, re.IGNORECASE)
    gfa_match = re.search(gfa_pattern, input_text, re.IGNORECASE)
    site_area_match = re.search(site_area_pattern, input_text, re.IGNORECASE)
    cooling_provided_match = re.search(cooling_provided_pattern, input_text, re.IGNORECASE)
    energy_consumed_match = re.search(energy_consumed_pattern, input_text, re.IGNORECASE)
    annual_energy_generated_match = re.search(annual_energy_generated_pattern, input_text, re.IGNORECASE)
    community_energy_consumed_match = re.search(community_energy_consumed_pattern, input_text, re.IGNORECASE)
    compliant_paints_match = re.search(compliant_paints_pattern, input_text, re.IGNORECASE)
    total_paints_match = re.search(total_paints_pattern, input_text, re.IGNORECASE)

    
    # Handle U-value calculation
    if U_value_intent:
        if R_value_match:
            try:
                R_value = float(R_value_match.group(1))
                # Calculate U-value
                U_value = math.ceil( 1 / R_value)
                return f"U-value = {U_value } (W/m²·K)"
            except ValueError:
                logging.error("Value error in U-value calculation.")
                return "Invalid input values for R-value. Please specify correct numbers."
        elif material_thickness_match and thermal_conductivity_match:
            try:
                material_thickness = float(material_thickness_match.group(1))
                thermal_conductivity = float(thermal_conductivity_match.group(1))
                # Calculate R-value
                R_value = math.ceil(material_thickness / thermal_conductivity)
                # Calculate U-value
                U_value = math.ceil( 1 / R_value)
                return f"U-value = {U_value } (W/m²·K)"
            except ValueError:
                logging.error("Value error in U-value calculation.")
                return "Invalid input values for material thickness or thermal conductivity. Please specify correct numbers."
        else:
            return "Invalid input for U-value calculation. Please specify both 'Material Thickness' and 'Thermal Conductivity' or R-value."
    # Handle R-value calculation
    if R_value_intent:
        if material_thickness_match and thermal_conductivity_match:
            try:
                # Extract and convert values
                material_thickness = float(material_thickness_match.group(1))
                thermal_conductivity = float(thermal_conductivity_match.group(1))
                 # Calculate R-value
                R_value = math.ceil(material_thickness / thermal_conductivity)
                return f"R-value = {R_value} (m²·K/W)"
            except ValueError:
                logging.error("Value error in R-value calculation.")
                return "Invalid input values for material thickness or thermal conductivity. Please specify correct numbers."
        else:
            return "Invalid input for R-value calculation. Please specify both 'Material Thickness' and 'Thermal Conductivity'."
            
    # Handle long-term bicycle storage calculations
    if long_term_intent:
        if building_type_match:
            building_type = building_type_match.group(1).lower()
            if building_type == 'residential':
                if occupants_match and dwelling_units_match:
                    try:
                        regular_occupants = float(occupants_match.group(2))
                        dwelling_units = float(dwelling_units_match.group(1))
                        occupants_bikes_required = regular_occupants * 0.30
                        bikes_required = max(math.ceil(occupants_bikes_required), math.ceil(dwelling_units))
                        return f"{bikes_required} Bicycles required for long-term storage (residential)"
                    except ValueError:
                        logging.error("Value error in calculation for residential.")
                        return "Invalid input values for occupants or dwelling units. Please specify correct numbers."
                elif occupants_match:
                    try:
                        regular_occupants = float(occupants_match.group(2))
                        bikes_required = math.ceil(regular_occupants * 0.30)
                        return f"{bikes_required} Bicycles storage required for long-term storage (residential)"
                    except ValueError:
                        logging.error("Value error in occupants calculation.")
                        return "Invalid input for regular building occupants. Please specify a correct number."
                elif dwelling_units_match:
                    try:
                        dwelling_units = float(dwelling_units_match.group(1))
                        bikes_required = math.ceil(dwelling_units)
                        return f"{bikes_required} Bicycles storage required for long-term storage (residential)"
                    except ValueError:
                        logging.error("Value error in dwelling units calculation.")
                        return "Invalid input for number of dwelling units. Please specify a correct number."
                else:
                    return "Please specify 'Regular Building occupants' or 'number of dwelling units' for residential buildings."

            elif building_type in ['commercial', 'institutional']:
                if occupants_match:
                    try:
                        regular_occupants = float(occupants_match.group(2))
                        multiplier = 0.05
                        long_term_bikes_required = regular_occupants * multiplier
                        return f"{math.ceil(long_term_bikes_required)} Bicycles required for long-term storage ({building_type})"
                    except ValueError:
                        logging.error("Value error in occupants calculation.")
                        return "Invalid input for regular building occupants. Please specify a correct number."
        return "Invalid input for long-term storage. Please specify 'Regular Building occupants = <number>' or 'dwelling units' with 'Building type'."

    # Handle shower facilities calculation
    if shower_facilities_intent:
        if occupants_match:
            try:
                regular_occupants = float(occupants_match.group(2))
                if regular_occupants <= 100:
                    showers_required = 1
                else:
                    showers_required = math.ceil((1 + (regular_occupants - 100)) / 150)
                return f"{showers_required} Showers required"
            except ValueError:
                logging.error("Value error in shower facilities calculation.")
                return "Invalid input for regular building occupants. Please specify a correct number."
        return "Error: The input does not contain sufficient data for shower facilities calculation."

    # Handle short-term storage calculation
    if short_term_intent:
        if peak_visitors_match:
            try:
                peak_visitors = float(peak_visitors_match.group(1))
                bikes_required = peak_visitors * 0.025
                return f"{math.ceil(bikes_required)} Bicycles storage required for short-term storage based on peak visitors"
            except ValueError:
                logging.error("Value error in peak visitors calculation.")
                return "Invalid input for peak visitors. Please specify a correct number."
    if short_term_intent:
        if area_match:
            try:
                area = float(area_match.group(2))
                unit = area_match.group(3).lower()
                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    bikes_required = 2 * (area / 5000)
                    return f"{math.ceil(bikes_required)} Bicycles storage required for short-term storage based on area in square feet"
                elif unit in ['meter', 'm', 'meter^2', 'm^2']:
                    bikes_required = 2 * (area / 465)
                    return f"{math.ceil(bikes_required)} Bicycles storage required for short-term storage based on area in square meters"
                else:
                    return "Invalid unit for area. Please specify either feet or meters."
            except ValueError:
                logging.error("Value error in area calculation.")
                return "Invalid input for area. Please specify a correct number."
    if short_term_intent:
        if length_width_match:
            try:
            # Capture length and width irrespective of their order and separator
                length = float(length_width_match.group('length') or length_width_match.group('length2'))
                width = float(length_width_match.group('width') or length_width_match.group('width2'))
                length_unit = length_width_match.group('length_unit') or length_width_match.group('length_unit2')
                width_unit = length_width_match.group('width_unit') or length_width_match.group('width_unit2')
            
                if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                    area = length * width
                    bikes_required = 2 * (area / 5000)
                    return f"{math.ceil(bikes_required)} Bicycles storage required for short-term storage based on length and width in feet"
                elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                    area = length * width
                    bikes_required = 2 * (area / 465)
                    return f"{math.ceil(bikes_required)} Bicycles storage required for short-term storage based on length and width in meters"
                else:
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."
            except ValueError:
                logging.error("Value error in length and width calculation.")
                return "Invalid input for length and width. Please specify correct numbers."
    
    # Required number of Preferred spaces
    if number_Preferred_spaces_intent:
        if Total_parking_match:
            try:
                Total_parking_spaces = float(Total_parking_match.group(2))
                Preferred_spaces = Total_parking_spaces * 0.05
                return f"{math.ceil(Preferred_spaces)} parking spaces required"
            except ValueError:
                logging.error("Value error in Total parking spaces")
                return "Invalid input for Total parking spaces."
        else:
            return "Invalid input for Preferred space. Please specify 'Total parking spaces = <number>'."
    
    # Required number of Fueling stations
    if fueling_stations_intent:
        if Total_parking_match:
            try:
                Total_parking_spaces = float(Total_parking_match.group(2))
                Fueling_stations = Total_parking_spaces * 0.02
                return f"{math.ceil(Fueling_stations)} fueling stations required"
            except ValueError:
                logging.error("Value error in Total parking spaces")
                return "Invalid input for Total parking spaces."
        else:
            return "Invalid input for Fueling stations. Please specify 'Total parking spaces = <number>'."
    
    # Percentage of Restoration Area
    if restoration_area_intent:
        if restoration_area_match and disturbed_area_match:
            try:
                restoration_area = float(restoration_area_match.group(1))
                disturbed_area = float(disturbed_area_match.group(1))
                percentage_restoration = math.ceil((restoration_area / disturbed_area) * 100)
                return f"{percentage_restoration:.2f}% restoration area"
            except ValueError:
                logging.error("Value error in restoration area calculation.")
                return "Invalid input for restoration area or total disturbed area."
        else:
            return "Invalid input for restoration area percentage. Please specify both 'Restoration area = <number>' and 'Total previously disturbed site area = <number>'."
     # Vegetated Space
    if vegetated_space_intent:
        # Check if either required_open_space_match or total_site_area_match is valid
        if required_open_space_match:
            try:
                required_open_space = float(required_open_space_match.group(2))
                vegetated_space = math.ceil(required_open_space * 0.25)
                return f"≥ {vegetated_space:.2f}% vegetated space required"
            except ValueError:
                logging.error("Value error in required open space calculation.")
                return "Invalid input for required open space."
        elif total_site_area_match:
            try:
                total_site_area = float(total_site_area_match.group(1))
                required_open_space = math.ceil(total_site_area * 0.30)
                vegetated_space = math.ceil(required_open_space * 0.25)
                return f"≥ {vegetated_space:.2f}% vegetated space required"
            except ValueError:
                logging.error("Value error in total site area calculation.")
                return "Invalid input for total site area."
        else:
            return "Invalid input for vegetated space. Please specify 'Required open space = <number>' or 'Total site area = <number>'."

    # Required Open Space
    if open_space_intent:
        if total_site_area_match:
            try:
                total_site_area = float(total_site_area_match.group(1))
                required_open_space = math.ceil(total_site_area * 0.30)
                return f"≥ {required_open_space:.2f}% open space required"
            except ValueError:
                logging.error("Value error in total site area calculation.")
                return "Invalid input for total site area."
        else:
            return "Invalid input for open space. Please specify 'Total site area = <number>'."
     # Required Outdoor Area Calculation
    if outdoor_area_intent:
        if unit_match and peak_inpatients_match and qualifying_outpatients_match:
            try:
                peak_inpatients = float(peak_inpatients_match.group(1))
                qualifying_outpatients = float(qualifying_outpatients_match.group(1))
                unit1 = unit_match.group(1).lower()
                    
                if unit1 in ['meter', 'm', 'meter^2', 'm^2']:
                    required_outdoor_area = 0.5 * (0.75 * peak_inpatients) + 0.5 * (0.75 * qualifying_outpatients)
                    return f"Required outdoor area: {math.ceil(required_outdoor_area)} m²"
                    
                elif unit1 in ['foot', 'ft', 'foot^2', 'ft^2']:
                    required_outdoor_area = 5 * (0.75 * peak_inpatients) + 5 * (0.75 * qualifying_outpatients)
                    return f"Required outdoor area: {math.ceil(required_outdoor_area):.2f} ft²"
                else:
                    return "Invalid unit for area. Please specify either feet or meters."
            except ValueError:
                logging.error("Value error in outdoor area calculation.")
                return "Invalid input for peak inpatients or qualifying outpatients. Please specify correct numbers."
        else:
            return "Invalid input for outdoor area. Please specify 'Area unit', 'Peak inpatients', and 'Qualifying outpatients'."
     # Calculate Air Volume Needed before Occupancy
    if air_volume_intent_before_occupancy:
        if length_width_match:
            try:
                # Calculate area from length and width
                length = float(length_width_match.group('length') or length_width_match.group('length2'))
                width = float(length_width_match.group('width') or length_width_match.group('width2'))
                length_unit = length_width_match.group('length_unit') or length_width_match.group('length_unit2')
                width_unit = length_width_match.group('width_unit') or length_width_match.group('width_unit2')

                if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                    area = length * width
                    air_volume = math.ceil(area * 14000)  # ft³
                    return f"Air volume needed before occupancy: {air_volume} ft³"
                elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                    area = length * width
                    air_volume = math.ceil(area * 4267140)  # liters
                    return f"Air volume needed before occupancy: {air_volume} l"
                else:
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."
            except ValueError:
                logging.error("Value error in air volume calculation.")
                return "Invalid input for length and width. Please specify correct numbers."
        elif area_match:
            try:
                area = float(area_match.group(2))
                unit = area_match.group(3).lower()
                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    air_volume = math.ceil(area * 14000)  # ft³
                    return f"Air volume needed before occupancy: {air_volume} ft³"
                elif unit in ['meter', 'm', 'meter^2', 'm^2']:
                    air_volume = math.ceil(area * 4267140)  # liters
                    return f"Air volume needed before occupancy: {air_volume} l"
                else:
                    return "Invalid unit for area. Please specify either feet or meters."
            except ValueError:
                logging.error("Value error in area calculation.")
                return "Invalid input for area. Please specify a correct number."
        else:
            return "Invalid input for air volume calculation. Please specify area or length and width."
            
  # Calculate Air Volume Needed during  Occupancy to complete
    if air_volume_intent_to_complete:
        if length_width_match:
            try:
                # Calculate area from length and width
                length = float(length_width_match.group('length') or length_width_match.group('length2'))
                width = float(length_width_match.group('width') or length_width_match.group('width2'))
                length_unit = length_width_match.group('length_unit') or length_width_match.group('length_unit2')
                width_unit = length_width_match.group('width_unit') or length_width_match.group('width_unit2')

                if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                    area = length * width
                    air_volume = math.ceil(area * 10500)  # ft³
                    return f"Air volume needed during occupancy to complete: {air_volume} ft³"
                elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                    area = length * width
                    air_volume = math.ceil(area * 3200880)  # liters
                    return f"Air volume needed during occupancy to complete: {air_volume} l"
                else:
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."
            except ValueError:
                logging.error("Value error in air volume calculation.")
                return "Invalid input for length and width. Please specify correct numbers."
        elif area_match:
            try:
                area = float(area_match.group(2))
                unit = area_match.group(3).lower()
                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    air_volume = math.ceil(area * 10500)  # ft³
                    return f"Air volume needed during occupancy to complete: {air_volume} ft³"
                elif unit in ['meter', 'm', 'meter^2', 'm^2']:
                    air_volume = math.ceil(area * 3200880)  # liters
                    return f"Air volume needed during occupancy to complete: {air_volume} l"
                else:
                    return "Invalid unit for area. Please specify either feet or meters."
            except ValueError:
                logging.error("Value error in area calculation.")
                return "Invalid input for area. Please specify a correct number."
        else:
            return "Invalid input for air volume calculation. Please specify area with unit or length and width with unit."  
     # Calculate Air Volume Needed during  Occupancy
    if air_volume_intent_during_occupancy:
        if length_width_match:
            try:
                # Calculate area from length and width
                length = float(length_width_match.group('length') or length_width_match.group('length2'))
                width = float(length_width_match.group('width') or length_width_match.group('width2'))
                length_unit = length_width_match.group('length_unit') or length_width_match.group('length_unit2')
                width_unit = length_width_match.group('width_unit') or length_width_match.group('width_unit2')

                if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                    area = length * width
                    air_volume = math.ceil(area * 3500)  # ft³
                    return f"Air volume needed during occupancy: {air_volume} ft³"
                elif length_unit in ['meter', 'm'] and width_unit in ['meter', 'm']:
                    area = length * width
                    air_volume = math.ceil(area * 1066260)  # liters
                    return f"Air volume needed during occupancy: {air_volume} l"
                else:
                    return "Inconsistent units. Length and width must be specified in the same unit, either feet or meters."
            except ValueError:
                logging.error("Value error in air volume calculation.")
                return "Invalid input for length and width. Please specify correct numbers."
        elif area_match:
            try:
                area = float(area_match.group(2))
                unit = area_match.group(3).lower()
                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    air_volume = math.ceil(area * 3500)  # ft³
                    return f"Air volume needed during occupancy: {air_volume} ft³"
                elif unit in ['meter', 'm', 'meter^2', 'm^2']:
                    air_volume = math.ceil(area * 1066260)  # liters
                    return f"Air volume needed during occupancy: {air_volume} l"
                else:
                    return "Invalid unit for area. Please specify either feet or meters."
            except ValueError:
                logging.error("Value error in area calculation.")
                return "Invalid input for area. Please specify a correct number."
        else:
            return "Invalid input for air volume calculation. Please specify area with unit or length and width with unit."
    # Handle runoff calculation
    if runoff_intent:
        if rainfall_match and depression_storage_match and infiltration_match:
            try:
                rainfall = float(rainfall_match.group(1))
                depression_storage = float(depression_storage_match.group(1))
                infiltration = float(infiltration_match.group(1))
                
                runoff = math.ceil(rainfall - depression_storage - infiltration)
                return f"Runoff = {runoff} mm/hr"
            except ValueError:
                logging.error("Value error in runoff calculation.")
                return "Invalid input values for runoff calculation. Please specify correct numbers for Rainfall, Depression Storage, and Infiltration."
        else:
            return "Missing input for runoff calculation. Please specify 'Rainfall = <number>', 'Depression storage = <number>', and 'Infiltration = <number>'."
    # Handle the % of development on previously developed land
    if development_percentage_intent:
        if previously_area_match and development_footprint_match:
            try:
                previously_developed_land = float(previously_area_match.group(1))
                development_footprint = float(development_footprint_match.group(1))
                
                if development_footprint == 0:
                    return "Area of development footprint cannot be zero."
                
                development_percentage = math.ceil(100 * (previously_developed_land / development_footprint))
                return f"Percentage of development on previously developed land = {development_percentage}%"
            except ValueError:
                logging.error("Value error in development percentage calculation.")
                return "Invalid input values for development percentage. Please specify correct numbers."
        else:
            return "Missing input for development percentage. Please specify 'Area of previously developed land' and 'Area of development footprint'."
    # Condition 1: Long-term or not mentioned (default is long-term)
    if Bicycle_racks_intent:
        if occupants_match:
                try:
                    occupants = float(occupants_match.group(2))  # Get the number of occupants
                    total_racks = math.ceil(occupants / 20)
                    return f"Total number of bicycle racks required (long-term): {total_racks}"
                except ValueError:
                    logging.error("Invalid value for occupants in long-term bicycle storage calculation.")
                    return "Invalid input for building occupants. Please specify a correct number."
    # Condition 2: Short-term storage
        elif area_racks_match:
            try:
                area = float(area_racks_match.group(2))  # Get the area
                total_racks = math.ceil(area / 500)
                return f"Total number of bicycle racks required (short-term): {total_racks}"
            except ValueError:
                logging.error("Invalid value for area in short-term bicycle storage calculation.")
                return "Invalid input for area. Please specify a correct number."

        # If no valid input for either long-term or short-term
        else:
            return "Invalid input for bicycle racks required. Please specify either Building occupants or Area with the appropriate term (long-term or short-term)."

     # Condition: Check for % Improvement calculation
    if Energy_performance_intent:
        if baseline_energy_match and proposed_energy_match:
            try:
                baseline_energy = float(baseline_energy_match.group(1))
                proposed_energy = float(proposed_energy_match.group(1))
                if baseline_energy == 0:
                    return "Baseline Annual Energy Consumption cannot be zero."

            # Calculate percentage improvement
                improvement = math.ceil(((baseline_energy - proposed_energy) / baseline_energy) * 100)
                return f"Percentage Improvement in Energy Consumption: {improvement:.2f}%"
            except ValueError:
                logging.error("Invalid input values for energy consumption.")
                return "Invalid input for energy consumption. Please specify correct numbers."
        else:
            return "Invalid input for Energy performance required.Please specify baseline energy and proposed energy"
     # SHW Calculation
    if shw_intent:
        if shw_generated_match and hot_water_demand_match:
            try:
                shw_generated = float(shw_generated_match.group(1))
                hot_water_demand = float(hot_water_demand_match.group(1))
                
                if hot_water_demand == 0:
                    return "Annual hot water demand cannot be zero."
                
                # Calculate the percentage of hot water demand provided by SHW panels
                percentage_shw = math.ceil((shw_generated / hot_water_demand) * 100)
                return f"{percentage_shw}% of hot water demand is provided by SHW panels"
            except ValueError:
                logging.error("Value error in SHW calculation.")
                return "Invalid input for hot water generated or demand. Please specify correct numbers."
        else:
            return "Invalid input for SHW calculation. Please specify both 'Annual hot water generated by SHW panels' and 'Annual hot water demand'."
    
    # Renewable Energy Calculation
    if renewable_energy_intent:
        if pv_energy_generated_match and proposed_energy_consumption_match:
            try:
                pv_energy_generated = float(pv_energy_generated_match.group(1))
                proposed_energy_consumption = float(proposed_energy_consumption_match.group(1))

                if proposed_energy_consumption == 0:
                    return "Proposed building annual energy consumption cannot be zero."

                # Calculate the percentage of renewable energy
                percentage_renewable_energy = math.ceil((pv_energy_generated / proposed_energy_consumption) * 100)
                return f"{percentage_renewable_energy}% of the building's energy is provided by the PV system"
            except ValueError:
                logging.error("Value error in Renewable Energy calculation.")
                return "Invalid input for PV energy generated or proposed energy consumption. Please specify correct numbers."
                
        elif annual_energy_generated_match and community_energy_consumed_match:
            try:
                # Extract energy generated and energy consumed values
                annual_energy_generated = float(annual_energy_generated_match.group(1))
                community_energy_consumed = float(community_energy_consumed_match.group(1))
                 # Check for zero energy consumption
                if community_energy_consumed == 0:
                    return "Error: Annual community energy consumption cannot be zero."
                # Calculate Renewable Energy percentage
                renewable_energy_percentage = math.ceil((annual_energy_generated / community_energy_consumed) * 100)
                return f"Renewable Energy = {renewable_energy_percentage}%"
            except ValueError:
                logging.error("Value error in Renewable Energy calculation.")
                return "Invalid input values for renewable energy generated or community energy consumption. Please specify correct numbers."
                
        else:
            return "Invalid input for Renewable Energy calculation. Please specify both 'Energy generated by the PV System' and 'Proposed building annual energy consumption' or both 'annual_energy_generated' and 'community_energy_consumed' ."
    
    # Occupant Density Calculation
    if occupant_density_intent:
        # Check if either designed maximum occupancy or expected occupancy is provided
        occupancy = None
        if designed_occupancy_match:
            occupancy = float(designed_occupancy_match.group(1))
        elif expected_occupancy_match:
            occupancy = float(expected_occupancy_match.group(1))
        # If neither occupancy type is provided, return an error
        if occupancy is None:
            return "Invalid input for occupant density. Please specify either 'Designed Maximum Occupancy' or 'Expected Occupancy'."

        # Handle area inputs
        area = None
        if area_match:
            try:
                unit = area_match.group(3).lower()
                if unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                    return "The unit for area must be in meters."
                else:
                    area_value = float(area_match.group(2))
                    area = area_value  # Area is already in square meters
            except ValueError:
                return "Invalid input for area. Please provide correct numbers."
        if length_width_match:
            try:
                length = float(length_width_match.group('length') or length_width_match.group('length2'))
                width = float(length_width_match.group('width') or length_width_match.group('width2'))
                length_unit = length_width_match.group('length_unit') or length_width_match.group('length_unit2')
                width_unit = length_width_match.group('width_unit') or length_width_match.group('width_unit2')
                
                # Check if any unit is in feet
                if length_unit in ['foot', 'ft'] or width_unit in ['foot', 'ft']:
                    return "The unit for length and width must be in meters."

                area = length* width  # Calculate area in square meters
            except ValueError:
                return "Invalid input for length or width. Please provide correct numbers."

        # Ensure area is provided
        if area is None:
            return "Invalid input for area. Please specify 'Area' in square meter, or provide 'Length' and 'Width' in meter."
            

        # Calculate occupant density
        occupant_density = math.ceil(occupancy / area)
        return f"Occupant Density = {occupant_density} occupants per square meter"
        
    if adhesives_sealants_intent:
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
        else:
            return "Invalid input for adhesives and sealants calculation. Please specify both 'Weight of adhesives and sealants not exceeding VOC limits' and 'Total weight of all adhesives and sealants'."
     # Handle % Waste Diverted from Landfill calculation
    if waste_diverted_intent:
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
    # Handle Connectivity Index calculation
    if connectivity_index_intent:
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
        else:
            return "Invalid input for Connectivity Index calculation. Please specify both 'Street links = <number>' and 'Nodes = <number>'."
    # Handle Intersection Density calculation
    if intersection_density_intent:
        if intersections_match:
            try:
                intersections = int(intersections_match.group(1))
                area = None

                # Handle area input if provided
                if area_match:
                    try:
                        area_value = float(area_match.group(2))
                        area_unit = area_match.group(3).lower()
                        
                        if area_unit in ['foot', 'ft', 'foot^2', 'ft^2']:
                            area = area_value / 10.764  # Convert ft² to m²
                        elif area_unit in ['meter', 'm', 'meter^2', 'm^2']:
                            area = area_value  # Already in m²
                        else:
                            return "Invalid area unit. Please specify the area in either square feet or square meters."
                    except ValueError:
                        return "Invalid input for area. Please specify a correct number."

                # Handle length and width input if provided
                if length_width_match and area is None:
                    try:
                        length = float(length_width_match.group('length') or length_width_match.group('length2'))
                        width = float(length_width_match.group('width') or length_width_match.group('width2'))
                        length_unit = length_width_match.group('length_unit') or length_width_match.group('length_unit2')
                        width_unit = length_width_match.group('width_unit') or length_width_match.group('width_unit2')
                        
                        # Convert units to meters for area calculation
                        if length_unit in ['foot', 'ft'] and width_unit in ['foot', 'ft']:
                            area = (length * width) / 10.764  # ft² to m²
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
            
    # Handle Continuous Walkway (CW) calculation
    if continuous_walkway_intent:
         if continuous_walkway_match and all_walkways_match:
            try:
                # Extract continuous walkway and all walkways length
                continuous_walkway_length = float(continuous_walkway_match.group(1))
                all_walkways_length = float(all_walkways_match.group(1))
                # Calculate CW percentage
                if all_walkways_length == 0:
                    return "Total length of all walkways cannot be zero."
                CW = math.ceil((continuous_walkway_length / all_walkways_length) * 100)
                return f"Continuous Walkway (CW) = {CW}%"
            except ValueError:
                logging.error("Value error in Continuous Walkway calculation.")
                return "Invalid input values for continuous walkways or all walkways. Please specify correct numbers."
         else:
            return "Invalid input for Continuous Walkway calculation. Please specify both 'Linear length on both side' and 'All walkways'."
    # Handle Floor Area Ratio (FAR) calculation
    if far_intent:
        if gfa_match and site_area_match:
            try:
                # Extract GFA and Site Area
                gfa = float(gfa_match.group(3))
                site_area = float(site_area_match.group(1))
                # Calculate FAR
                if site_area == 0:
                    return "Total site area cannot be zero."

                far = math.ceil((gfa / site_area)*100)
                return f"Floor Area Ratio (FAR) = {far}%"
            except ValueError:
                logging.error("Value error in FAR calculation.")
                return "Invalid input values for GFA or Site Area. Please specify correct numbers."
        else:
            return "Invalid input for Floor Area Ratio calculation. Please specify both 'Gross Floor Area (GFA)' and 'Site Area' with units."

     # Handle SEER calculation
    if seer_intent:
        if cooling_provided_match and energy_consumed_match:
            try:
                # Extract cooling provided and energy consumed values
                cooling_provided = float(cooling_provided_match.group(1))
                energy_consumed = float(energy_consumed_match.group(1))

                # Check for zero energy consumed
                if energy_consumed == 0:
                    return "Error: Amount of energy consumed cannot be zero."

                # Calculate SEER
                seer = math.ceil((cooling_provided / energy_consumed) * 100)
                return f"SEER = {seer}%"
            except ValueError:
                logging.error("Value error in SEER calculation.")
                return "Invalid input values for cooling provided or energy consumed. Please specify correct numbers."
        else:
            return "Invalid input for SEER calculation. Please specify both 'Cooling provided' and 'Energy consumed' with values."
            
    # Handle Compliant Paints and Coatings calculation        
    if compliant_paints_intent:
        if compliant_paints_match and total_paints_match:
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
        else:
            return "Invalid input for compliant paints and coatings. Please specify both 'Weight not exceeding VOC limits' and 'Total weight'."

    # Error messages when incorrect terms are used in storage queries
    if "short-term" in input_text and not (peak_visitors_match or area_match or length_width_match):
        return "Invalid input for short-term storage. Please specify 'Peak visitors = <number>' or 'Area = <number>' with units."
            
    # Error messages when incorrect terms are used in storage queries
    if "short-term" in input_text and not (peak_visitors_match or area_match or length_width_match):
        return "Invalid input for short-term storage. Please specify 'Peak visitors = <number>' or 'Area = <number>' with units."

    if "long-term" in input_text and "regular building occupants" not in input_text:
        return "Invalid input for long-term storage. Please specify 'Regular Building occupants = <number>' with a valid building type."

    # Generic check when 'bicycle storage' is mentioned without specific terms
    if "bicycle storage" in input_text and not (peak_visitors_match or area_match or length_width_match or (building_type_match and (occupants_match or dwelling_units_match))):
        return "No valid numerical data found for required calculation."
    
    if "Preferred space" in input_text and not Total_parking_match:
        return "Invalid input for Preferred space. Please specify 'Total parking spaces = <number>'."

    # Fallback for other inputs
    if not any(char.isdigit() for char in input_text):
        return "No valid number in the response"

    # Default response when input does not match any patterns
    return "No valid numerical data found for required calculation."
