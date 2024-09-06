import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Frame, Notebook, Entry, Button, Label
import os
import re 

# Global variables to store tab contents and names
tab_contents = []
tab_names = []

# Utility functions (placed outside any class)
def wildcard_to_regex(wildcard):
    regex = "^"
    for char in wildcard:
        if char == "*":
            regex += ".*"
        elif char == "?":
            regex += "."
        elif char == ".":
            regex += "\\."
        elif char == "\\":
            regex += "\\\\"
        else:
            regex += char
    regex += "$"
    return regex

def import_file():
    file_path = filedialog.askopenfilename(filetypes=[("RPT Files", "*.rpt")])
    if file_path:
        input_file_path_field.delete(0, tk.END)
        input_file_path_field.insert(0, file_path)

def process_data():
    input_file_path = input_file_path_field.get()
    output_file_path = os.path.join(os.getcwd(), "rpt.txt")

    if not input_file_path:
        messagebox.showwarning("Warning", "Please select a file.")
        return

    try:
        brd_name = convert_rpt_to_txt(input_file_path, output_file_path) 

    except Exception as e:
        messagebox.showerror("Error", f"Error converting file: {e}")
        return

    for i, tab_content in enumerate(tab_contents):
        tab_content.process_tab(output_file_path, tab_names[i], brd_name) 

    combine_reports()

def combine_reports():
    save_directory = os.path.join(os.getcwd(), "Spacing reports")
    combined_report_path = os.path.join(save_directory, "spacing_constraint_report.txt")

    try:
        with open(combined_report_path, "w", encoding="utf-8") as combined_file:
            for i in range(8): 
                tab_filename = f"Tab_{i+1}.txt"
                tab_filepath = os.path.join(save_directory, tab_filename)

                if os.path.exists(tab_filepath):
                    with open(tab_filepath, "r", encoding="utf-8") as tab_file:
                        combined_file.write(tab_file.read())
                        combined_file.write("\n\n") 

    except Exception as e:
        messagebox.showerror("Error", f"Error combining reports: {e}")

def convert_rpt_to_txt(input_file_path, output_file_path):
    data = []
    brd_name = None

    with open(input_file_path, "r", encoding="utf-8") as file:
        is_data_section = False

        for line in file: 
            line = line.strip()

            if "Design:" in line:
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 2:
                    brd_name = parts[1]

            if line.startswith("Type"):
                is_data_section = True
                next(file)
                continue

            if is_data_section and line.startswith("Net"):
                values = extract_values(line) 
                if values: 
                    add_unique(data, values) 

    with open(output_file_path, "w", encoding="utf-8") as file:
        if brd_name:
            file.write(brd_name + "\n")
        for values in data:
            file.write(",".join(values) + "\n") 

    return brd_name

def extract_values(line):
    parts = re.split(r'\s+', line.strip())
    if len(parts) >= 52:
        return [parts[0], parts[2], parts[5], parts[9], parts[12], parts[51]] 
    return None

def add_unique(data, values):
    if values not in data: 
        data.append(values)

# Create the main GUI window
window = tk.Tk()
window.title("Spacing Checker V1.2")
window.geometry("1280x850")

# File import panel
import_panel = Frame(window)
import_panel.pack(side=tk.TOP, padx=0, pady=10, anchor="nw")

import_button = Button(import_panel, text="Import .rpt file", command=import_file)
import_button.pack(side=tk.LEFT, padx=5)

input_file_path_field = Entry(import_panel, width=50)
input_file_path_field.pack(side=tk.LEFT, padx=5)

# Tabbed pane
tab_control = Notebook(window)
tab_control.pack(expand=1, fill="both")

predefined_net_names1 = [
    "*PCIE4_*X*", "*USB2*_D*", "*MDI*",
    "*SATA*_*X*", "CLK*", "", "", ""
]
predefined_net_names2 = [
    "*PCIE3_*X*", "*USB3*_*X*", "",
    "", "", "", "", ""
]
predefined_net_names3 = [
    "*PCIE2_*X*", "", "", "",
    "", "", "", ""
]
predefined_net_names4 = [
    "", "", "", "",
    "", "", "", ""
]

# Function to create a tab's content
def create_tab_content(default_net_names):
    frame = Frame(window)

    net_name_fields = []
    line_to_line_areas = []
    line_to_via_areas = []
    line_to_shape_areas = []
    via_to_via_areas = []

    def process_tab(file_path, tab_name, brd_name):
        all_line_to_line_lists = []
        all_line_to_via_lists = []
        all_line_to_shape_lists = []
        all_via_to_via_lists = []

        for i in range(4):
            target_net_name = net_name_fields[i].get()
            line_to_line_list = []
            line_to_via_list = []
            line_to_shape_list = []
            via_to_via_list = []

            try:
                process_file(file_path,
                              target_net_name,
                              line_to_line_list,
                              line_to_via_list,
                              line_to_shape_list,
                              via_to_via_list
                              )
                display_results(line_to_line_list, line_to_line_areas[i])
                display_results(line_to_via_list, line_to_via_areas[i])
                display_results(line_to_shape_list, line_to_shape_areas[i])
                display_results(via_to_via_list, via_to_via_areas[i])

                all_line_to_line_lists.append(line_to_line_list)
                all_line_to_via_lists.append(line_to_via_list)
                all_line_to_shape_lists.append(line_to_shape_list)
                all_via_to_via_lists.append(via_to_via_list)

            except Exception as e:
                messagebox.showerror("Error", f"Error processing file: {e}")

        output_report(all_line_to_line_lists,
                      all_line_to_via_lists,
                      all_line_to_shape_lists,
                      all_via_to_via_lists,
                      tab_name,
                      brd_name
                      )

    def output_report(all_line_to_line_lists,
                      all_line_to_via_lists,
                      all_line_to_shape_lists,
                      all_via_to_via_lists,
                      tab_name,
                      brd_name
                      ):
        report_content = f"Board File : {brd_name}\n\n"
        report_content += f"{tab_name} Report\n\n"

        for i in range(4):
            report_content += f"\n{net_name_fields[i].get()}:\n\n"
            report_content += "【Line_to_Line】\n"
            if all_line_to_line_lists[i]:
                for item in all_line_to_line_lists[i]:
                    report_content += "".join(item) + "\n"
            report_content += "\n【Line_to_Via】\n"
            if all_line_to_via_lists[i]:
                for item in all_line_to_via_lists[i]:
                    report_content += "".join(item) + "\n"
            report_content += "\n【Line_to_Shape】\n"
            if all_line_to_shape_lists[i]:
                for item in all_line_to_shape_lists[i]:
                    report_content += "".join(item) + "\n"
            report_content += "\n【Via_to_Via】\n"
            if all_via_to_via_lists[i]:
                for item in all_via_to_via_lists[i]:
                    report_content += "".join(item) + "\n"

            # 自動產生檔名並保存到指定路徑
            default_filename = tab_name.replace(" ", "_") + ".txt"  # 將空格替換為底線
            save_directory = os.path.join(os.getcwd(), "Spacing reports")  # 指定保存路徑為當前目錄下的 "reports" 資料夾
            os.makedirs(save_directory, exist_ok=True)  # 如果資料夾不存在，則建立
            save_path = os.path.join(save_directory, default_filename)

            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(report_content)

            except Exception as e:
                messagebox.showerror("Error", f"Error saving report: {e}")

    def process_file(file_path,
                     target_net_name,
                     line_to_line_list,
                     line_to_via_list,
                     line_to_shape_list,
                     via_to_via_list
                     ):
        regex_target_net_name = wildcard_to_regex(target_net_name) 

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",") 
                if len(parts) >= 6 and parts[0] == "Net":
                    if re.match(regex_target_net_name, parts[1]):
                        line_to_line_list.append(f"{parts[1]},{parts[2]}")
                        line_to_via_list.append(f"{parts[1]},{parts[3]}")
                        line_to_shape_list.append(f"{parts[1]},{parts[4]}")
                        via_to_via_list.append(f"{parts[1]},{parts[5]}")

        line_to_line_list.sort()
        line_to_via_list.sort()
        line_to_shape_list.sort()
        via_to_via_list.sort()

    def display_results(result_list, text_area):
        text_area.delete(1.0, tk.END)
        for item in result_list:
            text_area.insert(tk.END, item + "\n")


    for i in range(4):
        net_name_label = Label(frame, text="輸入net name")
        net_name_label.grid(row=0, column=i*4, padx=5, pady=5, sticky='w')

        net_name_field = Entry(frame)
        net_name_field.grid(row=0, column=i*4+1, padx=5, pady=5)
        net_name_field.insert(0, default_net_names[i])
        net_name_fields.append(net_name_field)

        # Add titles and ScrolledText widgets
        line_to_line_label = Label(frame, text="Line to Line")
        line_to_line_label.grid(row=1, column=i*4, padx=5, pady=5, sticky='w')
        line_to_line_area = scrolledtext.ScrolledText(frame, height=10, width=60)
        line_to_line_area.grid(row=2, column=i*4, columnspan=2, padx=5, pady=5, sticky="nsew")
        line_to_line_areas.append(line_to_line_area)

        line_to_via_label = Label(frame, text="Line to VIA")
        line_to_via_label.grid(row=3, column=i*4, padx=5, pady=5, sticky='w')
        line_to_via_area = scrolledtext.ScrolledText(frame, height=10, width=60)
        line_to_via_area.grid(row=4, column=i*4, columnspan=2, padx=5, pady=5, sticky="nsew")
        line_to_via_areas.append(line_to_via_area)

        line_to_shape_label = Label(frame, text="Line to Shape")
        line_to_shape_label.grid(row=5, column=i*4, padx=5, pady=5, sticky='w')
        line_to_shape_area = scrolledtext.ScrolledText(frame, height=10, width=60)
        line_to_shape_area.grid(row=6, column=i*4, columnspan=2, padx=5, pady=5, sticky="nsew")
        line_to_shape_areas.append(line_to_shape_area)

        via_to_via_label = Label(frame, text="VIA to VIA")
        via_to_via_label.grid(row=7, column=i*4, padx=5, pady=5, sticky='w')
        via_to_via_area = scrolledtext.ScrolledText(frame, height=10, width=60)
        via_to_via_area.grid(row=8, column=i*4, columnspan=2, padx=5, pady=5, sticky="nsew")
        via_to_via_areas.append(via_to_via_area)

        frame.grid_columnconfigure(i*4, weight=1)
        frame.grid_columnconfigure(i*4+1, weight=1)
        frame.grid_columnconfigure(i*4+2, weight=1)
        frame.grid_columnconfigure(i*4+3, weight=1)

    # Attach the process_tab function to the frame
    frame.process_tab = process_tab

    return frame

# Create 8 tabs and add them to the tab control
for i in range(8):
    tab_content = create_tab_content([
        predefined_net_names1[i],
        predefined_net_names2[i],
        predefined_net_names3[i],
        predefined_net_names4[i]
    ])
    tab_name = f"Tab {i+1}"
    tab_control.add(tab_content, text=tab_name)
    tab_contents.append(tab_content)
    tab_names.append(tab_name)

# Process button
process_button = Button(window, text="Process", command=process_data)
process_button.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)

def Spacing_Checker():
    window.mainloop()

if __name__ == "__main__":
    Spacing_Checker()
    