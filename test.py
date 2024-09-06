import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Frame, Notebook, Entry, Button, Label
import os
import re

class ImpedanceCheckerGUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Impedance Checker V1.2")
        self.window.geometry("1250x680")
        self.window.resizable(False, False)

        self.tab_contents = []
        self.tab_names = []

        self.create_import_panel()
        self.create_tabbed_pane()
        self.create_process_button()

    def create_import_panel(self):
        import_panel = Frame(self.window)
        import_panel.pack(side=tk.TOP, padx=0, pady=10, anchor="nw")

        import_button = Button(import_panel, text="Import .rpt file", command=self.import_file)
        import_button.pack(side=tk.LEFT, padx=5)

        self.input_file_path_field = Entry(import_panel, width=50)
        self.input_file_path_field.pack(side=tk.LEFT, padx=5)

    def create_tabbed_pane(self):
        self.tab_control = Notebook(self.window)
        self.tab_control.pack(expand=1, fill="both")

        predefined_net_names = [
            ["*PCIE*_*X*", "*USB2*_D*", "*MDI*", "*SATA*_*X*", "CLK*", "", "", ""],
            ["", "*USB3*_*X*", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""]
        ]

        for i in range(8):
            tab_content = ImpedanceCheckerTab(self.window, predefined_net_names[:, i]) 
            tab_name = f"Tab {i + 1}"
            self.tab_control.add(tab_content, text=tab_name)
            self.tab_contents.append(tab_content)
            self.tab_names.append(tab_name)

    def create_process_button(self):
        process_button = Button(self.window, text="Process", command=self.process_data)
        process_button.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)

    def import_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("RPT Files", "*.rpt")])
        if file_path:
            self.input_file_path_field.delete(0, tk.END)
            self.input_file_path_field.insert(0, file_path)

    def process_data(self):
        input_file_path = self.input_file_path_field.get()
        output_file_path = os.path.join(os.getcwd(), "rpt.txt")

        if not input_file_path:
            messagebox.showwarning("Warning", "Please select a file.")
            return

        try:
            brd_name = convert_rpt_to_txt(input_file_path, output_file_path) 

        except Exception as e:
            messagebox.showerror("Error", f"Error converting file: {e}")
            return

        for i, tab_content in enumerate(self.tab_contents):
            tab_content.process_tab(output_file_path, self.tab_names[i], brd_name)

        self.combine_reports()

    def combine_reports(self):
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


class ImpedanceCheckerTab(Frame):
    def __init__(self, window, default_net_names): 
        super().__init__(window)

        self.net_name_fields = []
        self.impedance_fields = []
        self.match_areas = []
        self.no_match_areas = []

        self.create_tab_content(default_net_names)

    def create_tab_content(self, default_net_names):
        for i in range(4):
            net_name_label = Label(self, text="輸入 net name")
            net_name_label.grid(row=0, column=i * 2, padx=5, pady=5, sticky='w')

            net_name_field = Entry(self)
            net_name_field.grid(row=0, column=i * 2 + 1, padx=5, pady=5)
            net_name_field.insert(0, default_net_names[i]) 
            self.net_name_fields.append(net_name_field)

            impedance_label = Label(self, text="設定阻抗")
            impedance_label.grid(row=1, column=i * 2, padx=5, pady=5, sticky='w')

            impedance_field = Entry(self)
            impedance_field.grid(row=1, column=i * 2 + 1, padx=5, pady=5)
            self.impedance_fields.append(impedance_field)

            pass_label = Label(self, text="PASS")
            pass_label.grid(row=2, column=i * 2, columnspan=2, padx=5, pady=5, sticky='w')

            match_area = scrolledtext.ScrolledText(self, height=15, width=40)
            match_area.grid(row=3, column=i * 2, columnspan=2, padx=5, pady=5)
            self.match_areas.append(match_area)

            fail_label = Label(self, text="FAIL")
            fail_label.grid(row=4, column=i * 2, columnspan=2, padx=5, pady=5, sticky='w')

            no_match_area = scrolledtext.ScrolledText(self, height=15, width=40)
            no_match_area.grid(row=5, column=i * 2, columnspan=2, padx=5, pady=5)
            self.no_match_areas.append(no_match_area)

    def process_tab(self, file_path, tab_name, brd_name):
        all_match_lists = []
        all_no_match_lists = []

        for i in range(4):
            target_second_line = self.net_name_fields[i].get()
            target_third_line = self.impedance_fields[i].get()
            match_list = []
            no_match_list = []

            try:
                process_file(file_path, target_second_line, target_third_line, match_list, no_match_list)
                self.display_results(match_list, self.match_areas[i], no_match_list, self.no_match_areas[i])

                all_match_lists.append(match_list)
                all_no_match_lists.append(no_match_list)

            except Exception as e:
                messagebox.showerror("Error", f"Error processing file: {e}")

        self.output_report(all_no_match_lists, tab_name, brd_name)

    def output_report(self, all_no_match_lists, tab_name, brd_name):
        report_content = f"Board File : {brd_name}\n\n"
        report_content += f"{tab_name} Report\n\n"

        for i in range(4):
            report_content += f"\n{self.net_name_fields[i].get()}:{self.impedance_fields[i].get()}\n\n"
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

    def display_results(self, match_list, match_area, no_match_list, no_match_area):
        match_area.delete(1.0, tk.END)
        no_match_area.delete(1.0, tk.END)

        for item in match_list:
            match_area.insert(tk.END, item + "\n")

        for item in no_match_list:
            no_match_area.insert(tk.END, ",".join(item) + "\n")

# Helper functions 

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

def main():
    window = tk.Tk()
    app = ImpedanceCheckerGUI(window)
    window.mainloop()

if __name__ == "__main__":
    main()