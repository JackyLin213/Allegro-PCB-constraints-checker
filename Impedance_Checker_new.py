import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Frame, Notebook, Entry, Button, Label
import os
import re

# Global variables to store tab contents and names
tab_contents = []
tab_names = []

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
    save_directory = os.path.join(os.getcwd(), "Impedance reports")
    combined_report_path = os.path.join(save_directory, "impedance_constraint_report.txt")

    try:
        with open(combined_report_path, "w", encoding="utf-8") as combined_file:
            for i in range(8):
                tab_filename = f"Tab_{i + 1}.txt"
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
    if len(parts) >= 4:
        return [parts[0], parts[2], parts[3]]
    return None

def add_unique(data, values):
    if values not in data:
        data.append(values)

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

# Create the main GUI window
window = tk.Tk()
window.title("Impedance Checker V1.2")
window.geometry("1250x680")
window.resizable(False, False)

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
    "*PCIE*_*X*", "*USB2*_D*", "*MDI*",
    "*SATA*_*X*", "CLK*", "", "", ""
]
predefined_net_names2 = [
    "", "*USB3*_*X*", "",
    "", "", "", "", ""
]
predefined_net_names3 = [
    "", "", "", "",
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
    impedance_fields = []
    match_areas = []
    no_match_areas = []

    def process_tab(file_path, tab_name, brd_name):
        all_match_lists = []
        all_no_match_lists = []

        for i in range(4):
            target_second_line = net_name_fields[i].get()
            target_third_line = impedance_fields[i].get()
            match_list = []
            no_match_list = []

            try:
                process_file(file_path, target_second_line, target_third_line, match_list, no_match_list)
                display_results(match_list, match_areas[i], no_match_list, no_match_areas[i])

                all_match_lists.append(match_list)
                all_no_match_lists.append(no_match_list)

            except Exception as e:
                messagebox.showerror("Error", f"Error processing file: {e}")

        output_report(all_no_match_lists, all_match_lists, tab_name, brd_name)

    def output_report(all_no_match_lists, all_match_lists, tab_name, brd_name):
        report_content = f"Board File : {brd_name}\n\n"
        report_content += f"{tab_name} Report\n\n"

        for i in range(4):
            report_content += f"\n{net_name_fields[i].get()}:{impedance_fields[i].get()}\n\n"
            # report_content += "Match List:\n"
            # if all_match_lists[i]:
            #     report_content += "\n".join(all_match_lists[i]) + "\n\n"
            # else:
            #     report_content += "No matches found.\n\n"
            report_content += "【No Match List】\n"
            if all_no_match_lists[i]:
                for item in all_no_match_lists[i]:
                    report_content += ",".join(item) + "\n"
            else:
                report_content += "No mismatches found.\n\n"

            default_filename = tab_name.replace(" ", "_") + ".txt" 
            save_directory = os.path.join(os.getcwd(), "Impedance reports") 
            os.makedirs(save_directory, exist_ok=True) 
            save_path = os.path.join(save_directory, default_filename)

            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(report_content)

            except Exception as e:
                messagebox.showerror("Error", f"Error saving report: {e}")

    def process_file(file_path, target_second_line, target_third_line, match_list, no_match_list):
        regex_second_line = wildcard_to_regex(target_second_line)

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",") 
                if len(parts) == 3 and parts[0] == "Net":
                    if re.match(regex_second_line, parts[1]):
                        if target_third_line and target_third_line in parts[2]:
                            match_list.append(parts[1])
                        else:
                            no_match_list.append([parts[1], parts[2]])

        match_list.sort()
        no_match_list.sort()

    def display_results(match_list, match_area, no_match_list, no_match_area):
        match_area.delete(1.0, tk.END)
        no_match_area.delete(1.0, tk.END)

        for item in match_list:
            match_area.insert(tk.END, item + "\n")

        for item in no_match_list:
            no_match_area.insert(tk.END, ",".join(item) + "\n")


    for i in range(4):
        net_name_label = Label(frame, text="輸入 net name")
        net_name_label.grid(row=0, column=i * 2, padx=5, pady=5, sticky='w')

        net_name_field = Entry(frame)
        net_name_field.grid(row=0, column=i * 2 + 1, padx=5, pady=5)
        net_name_field.insert(0, default_net_names[i])
        net_name_fields.append(net_name_field)

        impedance_label = Label(frame, text="設定阻抗")
        impedance_label.grid(row=1, column=i * 2, padx=5, pady=5, sticky='w')

        impedance_field = Entry(frame)
        impedance_field.grid(row=1, column=i * 2 + 1, padx=5, pady=5)
        impedance_fields.append(impedance_field)

        pass_label = Label(frame, text="PASS")
        pass_label.grid(row=2, column=i * 2, columnspan=2, padx=5, pady=5, sticky='w')

        match_area = scrolledtext.ScrolledText(frame, height=15, width=40)
        match_area.grid(row=3, column=i * 2, columnspan=2, padx=5, pady=5)
        match_areas.append(match_area)

        fail_label = Label(frame, text="FAIL")
        fail_label.grid(row=4, column=i * 2, columnspan=2, padx=5, pady=5, sticky='w')

        no_match_area = scrolledtext.ScrolledText(frame, height=15, width=40)
        no_match_area.grid(row=5, column=i * 2, columnspan=2, padx=5, pady=5)
        no_match_areas.append(no_match_area)

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
    tab_name = f"Tab {i + 1}"
    tab_control.add(tab_content, text=tab_name)
    tab_contents.append(tab_content)
    tab_names.append(tab_name)

# Process button
process_button = Button(window, text="Process", command=process_data)
process_button.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)

def Impedance_Checker():
    window.mainloop()

if __name__ == "__main__":
    Impedance_Checker()
    