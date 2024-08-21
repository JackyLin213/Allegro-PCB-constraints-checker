import re

def convert_rpt_to_txt(input_file_path, output_file_path):
    data = []
    
    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            is_data_section = False
            
            for line in file:
                line = line.strip()
                if line.startswith("Type"):
                    is_data_section = True
                    next(file)  # Skip the header line
                    continue
                
                if is_data_section and line.startswith("Net"):
                    values = extract_values(line)
                    if values:
                        add_unique(data, values)
        
        with open(output_file_path, "w", encoding="utf-8") as file:
            for values in data:
                file.write(",".join(values) + "\n")
            print("Data extracted and written to text file successfully.")
    
    except Exception as e:
        print(f"Error processing file: {e}")

def extract_values(line):
    parts = re.split(r'\s+', line.strip())
    if len(parts) >= 8:
        return [parts[0], parts[2], parts[7]]
    return None

def add_unique(data_list, new_item):
    if new_item not in data_list:
        data_list.append(new_item)

# Example usage
input_file_path = "consmgr.rpt"  # Replace with your input RPT file path
output_file_path = "rpt_output.txt"  # Replace with your desired output TXT file path

convert_rpt_to_txt(input_file_path, output_file_path)
