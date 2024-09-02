import re

def convert_rpt_to_txt(input_file_path, output_file_path):
    data = []
    
    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            is_data_section = False
            
            for line in file:  # 逐行讀取 .rpt 檔案
                line = line.strip()  # 去除每行前後的空白字符
                if line.startswith("Type"):
                    is_data_section = True
                    next(file)  # Skip the header line
                    continue
                
                if is_data_section and line.startswith("Net"):
                    values = extract_values(line)  # 調用 extract_values 函數從該行提取values
                    if values:  # 如果提取到values
                        add_unique(data, values)  # 調用 add_unique 函數將values添加到 data 列表中，確保不重複添加
        
        with open(output_file_path, "w", encoding="utf-8") as file:
            for values in data:
                file.write(",".join(values) + "\n")  # 將每一組數據用","組成一個字串，並換行，然後寫入到 .txt 文件中
            print("Data extracted and written to text file successfully.")
    
    except Exception as e:
        print(f"Error processing file: {e}")

def extract_values(line):
    parts = re.split(r'\s+', line.strip())  # 將file內的data依","方式做split
    if len(parts) >= 8:  # 假如split後有8個parts
        return [parts[0], parts[2], parts[7]]  # 則return指定位置part[]
    return None

def add_unique(data_list, new_item):
    if new_item not in data_list:  # 假如values不在data list內
        data_list.append(new_item)  # 則將values添加到data list尾中

# Example usage
input_file_path = "consmgr.rpt"  # Replace with your input RPT file path
output_file_path = "rpt_output.txt"  # Replace with your desired output TXT file path

convert_rpt_to_txt(input_file_path, output_file_path)
