import re

def convert_rpt_to_txt(input_file_path, output_file_path):
    data = []
    brd_name = None

    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            is_data_section = False

            for line in file: 
                line = line.strip() 
                
                if "Design:" in line:
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 2:
                        brd_name = parts[1]
                        # print(brd_name)

                if line.startswith("Type"):
                    is_data_section = True
                    next(file) 
                    continue

                if is_data_section and line.startswith("Net"):
                    values = extract_values(line) 
                    if values:
                        add_unique(data, values) 

        with open(output_file_path, "w", encoding="utf-8") as file:
            if brd_name:  # 如果成功提取到brd_name，则先写入
                file.write(brd_name + "\n")
            for values in data:
                file.write(",".join(values) + "\n") 
            print("Data extracted and written to text file successfully.")

    except Exception as e:
        print(f"Error processing file: {e}")

def extract_values(line):
    line = re.sub(r'\*\*', '', line)  # Remove "**" from the line
    parts = re.split(r'\s+', line.strip())  # 將file內的data依","方式做split
    # print(parts)
    if len(parts) >= 4:  # 假如split後有8個parts
        return [parts[0], parts[2], parts[3]]  # 則return指定位置part[]
    return None

def add_unique(data_list, new_item):
    if new_item not in data_list:  # 假如values不在data list內
        data_list.append(new_item)  # 則將values添加到data list尾中

# Example usage
input_file_path = "consmgr.rpt"  # Replace with your input RPT file path
output_file_path = "rpt_output.txt"  # Replace with your desired output TXT file path

convert_rpt_to_txt(input_file_path, output_file_path)
