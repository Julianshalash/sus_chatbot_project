import pandas as pd
import openpyxl
# Load the Excel file (replace 'your_file.xlsx' with the actual file name)
file_path = 'U_value_based_k_Material.xlsx'
df = pd.read_excel(file_path)
import re
import logging
# Function to get 'K Value' based on 'Material'
def get_k_value(Material):
    Material = Material.strip().lower()
    result = df[df['Material'].str.lower() == Material]
    
    if not result.empty:
        k_value = result['K_value'].values[0]
        if isinstance(k_value, (int, float)):  # Ensure K value is numeric
            return k_value
        else:
            print(f"Invalid K value for Material '{Material}'. Expected numeric, got {type(k_value)}.")
            return None
    else:
        print(f"Material '{Material}' not found.")
        return None

# Function to calculate the R Value based on Thickness and K Value
def calculate_r_value(thickness, k_value):
    if k_value is not None and k_value != 0:
        try:
            return round(float(thickness) / k_value, 3)  # Ensure thickness is converted to float
        except ValueError:
            print(f"Invalid thickness value: {thickness}. Expected a number.")
            return None
    else:
        return None

# Function to process multiple inputs (Materials and Thicknesses) and return U Value
def process_multiple_inputs(Materials, thicknesses):
    if len(Materials) != len(thicknesses):
        print(f"Error: Mismatch between the number of materials ({len(Materials)}) and thicknesses ({len(thicknesses)}).")
        return None
    total_r_value = 0  # Initialize the total R Value accumulator
    valid_r_value_count = 0  # To count valid R Values
    
    # Loop through each Material and thickness
    for Material, thickness in zip(Materials, thicknesses):
        k_value = get_k_value(Material.strip())
        
        if k_value is not None:
            r_value = calculate_r_value(thickness, k_value)
            if r_value is not None:
                total_r_value += r_value  # Add to the total R Value
                valid_r_value_count += 1  # Increment valid R Value count
                print(f"Material: {Material}, Thickness: {thickness}")
                print(f"K Value: {k_value}, R Value: {r_value}\n")
            else:
                print(f"Invalid R Value for Material: {Material}.")
        else:
            print(f"Material '{Material}' not found.\n")
    
    if valid_r_value_count > 0:
        print(f"Total R Value Sum: {round(total_r_value, 3)}")
        # Calculate and return the U Value as 1 / total R Value
        if total_r_value > 0:
            u_value = round(1 / total_r_value, 3)
            return u_value
        else:
            print("Total R Value is zero. Cannot compute U Value.")
            return None
    else:
        print("No valid R Values to sum.")
        return None

# Function to parse user input to extract areas, materials, and thicknesses
def parse_user_input(user_input):
    # Expected input format validation, giving feedback if invalid
    try:
        user_input = user_input.lower()
    
    # Regex to capture complex material names and area matches
        material_regex = r"material:\s*([a-zA-Z0-9\s\/\.\,\-\_\%\°]+(?:,?[a-zA-Z0-9\s\/\.\,\-\_\%\°]+)*)\s*(?:and|with|$)"
        thickness_regex = r"thickness(?:es)?:\s*([0-9.,\s]+)\s*(?:and|with|$)"
        area_regex = r"a(\d+)\s*=\s*([0-9.]+)"  # Capture areas like A1 = 90

        Material_match = re.search(material_regex, user_input)
        thickness_match = re.search(thickness_regex, user_input)
        areas = re.findall(area_regex, user_input)  # Match all area patterns like A1 = 90

        if not Material_match or not thickness_match:
            return None, None, None
    
        Materials = [mat.strip() for mat in Material_match.group(1).split(',')]
        thicknesses = [float(thick.strip()) for thick in thickness_match.group(1).split(',')]

        return Materials, thicknesses, areas
    except ValueError as e:
        logging.error(f"Error in parsing input: {e}")
        return None, None, None

# Function to calculate simple U Value
def calculate_u_value(Materials, thicknesses):
    # Process the input and calculate the U value
    u_value = process_multiple_inputs(Materials, thicknesses)
    
    if u_value is not None:
        return u_value
    else:
        return None

# Updated function to handle the input separated by semicolons
def parse_weighted_input(user_input):
    user_input = user_input.lower()

    # Split by semicolon to separate different areas
    area_sections = user_input.split(';')

    parsed_data = []
    
    # Regex patterns for parsing area, materials, and thicknesses
    area_regex = r"(a\d+)\s*=\s*([0-9.]+)"
    material_regex = r"material:\s*([a-zA-Z0-9\s\/\.\,\-\_\%\°]+(?:,?[a-zA-Z0-9\s\/\.\,\-\_\%\°]+)*)\s*(?:and|with|$)"
    thickness_regex = r"thickness(?:es)?:\s*([0-9.,\s]+)\s*(?:and|with|$)"
    
    for section in area_sections:
        # Extract area
        area_match = re.search(area_regex, section)
        if not area_match:
            print("Error: Invalid area format.")
            return None
        
        area_label, area_value = area_match.groups()
        
        # Extract materials
        material_match = re.search(material_regex, section)
        if not material_match:
            print("Error: Invalid material format.")
            return None
        
        Materials = [mat.strip() for mat in material_match.group(1).split(',')]
        
        # Extract thicknesses
        thickness_match = re.search(thickness_regex, section)
        if not thickness_match:
            print("Error: Invalid thickness format.")
            return None
        
        thicknesses = [float(thick.strip()) for thick in thickness_match.group(1).split(',')]
        
        # Append the parsed data for this area
        parsed_data.append((float(area_value), Materials, thicknesses))
    
    return parsed_data

# Function to calculate the Weighted U value based on areas and U values
def calculate_weighted_u_value(user_input):
    # Parse the user input for areas, materials, and thicknesses
    parsed_data = parse_weighted_input(user_input)

    if not parsed_data:
        return "Error: Invalid input format."
        

    sum_area_u = 0  # To accumulate total A × U
    sum_area = 0    # To accumulate total A (areas)
    
    # Process each area, materials, and thicknesses
    for area_value, Materials, thicknesses in parsed_data:
        # Check for material-thickness mismatch
        if len(Materials) != len(thicknesses):
            return f"Error: Mismatch between the number of materials and thicknesses in area {area_value}."
            

        # Calculate the U value for the area
        u_value = process_multiple_inputs(Materials, thicknesses)
        
        if u_value is not None:
            # Add the area and A × U to the sums
            sum_area_u += area_value * u_value
            sum_area += area_value
            print(f"Area: {area_value}, U Value: {u_value}, A × U: {round(area_value * u_value, 3)}")
        else:
            return f"Could not calculate U Value for area {area_value}."

    # Calculate the Weighted U Value
    if sum_area > 0:
        weighted_u_value = sum_area_u / sum_area
        print(f"Total Weighted U Value: {round(weighted_u_value, 3)}")
        return round(weighted_u_value, 3)  # Return the calculated weighted U value
    else:
        print("Error: Total area cannot be zero.")

# Intent recognition function to determine whether to calculate simple or weighted U value
def chatbot_calculate(user_input):
    logging.debug(f"Input received for U-value calculation: {user_input}")
    if "weighted u" in user_input.lower():
        result = calculate_weighted_u_value(user_input)
        if isinstance(result, float):  # If result is a valid U value
            return f"Calculated Weighted U Value: {result}"
        else:
            return result 
    elif "u value" in user_input.lower():
        Materials, thicknesses, _ = parse_user_input(user_input)
        # Ensure Materials and thicknesses are not None
        if Materials is None or thicknesses is None:
            return "Error: Invalid input format or missing materials/thicknesses."
        if len(Materials) != len(thicknesses):
            logging.debug("Mismatch between materials and thicknesses.")
            return "Error: Invalid input format or mismatch between the materials and thicknesses."
        u_value = calculate_u_value(Materials, thicknesses)
        if u_value is not None:
            logging.debug(f"Calculated U Value: {u_value}")
            return f"Calculated U Value: {u_value}"
        else:
            return "Error: Could not calculate U value."
    else:
        logging.debug("Unknown intent for U-value.")
        return "Unknown intent. Please specify 'U value' or 'Weighted U value'."
