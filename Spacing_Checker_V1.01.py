import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Frame, Notebook, Entry, Button, Label
import os
import re

class Utils:
    @staticmethod
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

class GUIApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spacing Checker V1.0")
        self.geometry("1280x850")
        #self.resizable(False, False)
        self.tab_contents = []
        
        # File import panel
        import_panel = Frame(self)
        import_panel.pack(side=tk.TOP, padx=0, pady=10, anchor="nw")

        import_button = Button(import_panel, text="Import .rpt file", command=self.import_file)
        import_button.pack(side=tk.LEFT, padx=5)

        self.input_file_path_field = Entry(import_panel, width=50)
        self.input_file_path_field.pack(side=tk.LEFT, padx=5)
                        
        # Tabbed pane
        tab_control = Notebook(self)
        tab_control.pack(expand=1, fill="both")
        
        predefined_net_names = [
            "*PCIE*_*X*", "*USB2*_D*", "*MDI*",
            "*SATA*_*X*", "CLK*", "*I2C*_*SDA*", "*SMB*_*SDA*", ""
        ]
        predefined_net_names2 = [
            "*PE*_*X*", "*USB3*_*X*", "*KR*_*X*",
            "*SAS*", "", "*I2C*_*SCL*", "*SMB*_*SCL*", ""
        ]
        predefined_net_names3 = [
            "*SFP*_*X*", "*USB4*_*X*", "", "",
            "", "", "", ""
        ]
        
        for i in range(8):
            tab_content = TabContent(self, predefined_net_names[i], predefined_net_names2[i], predefined_net_names3[i])
            tab_control.add(tab_content, text=f"Tab {i+1}")
            self.tab_contents.append(tab_content)

        # Process button
        process_button = Button(self, text="Process", command=self.process_data)
        process_button.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)


    def import_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("RPT Files", "*.rpt")])
        if file_path:
            self.input_file_path_field.delete(0, tk.END)
            self.input_file_path_field.insert(0, file_path)
    
    def process_data(self):
        input_file_path = self.input_file_path_field.get()
        
        if not input_file_path:
            messagebox.showwarning("Warning", "Please select a file.")
            return
        
        output_file_path = os.path.join(os.getcwd(), "rpt.txt")
        
        try:
            self.convert_rpt_to_txt(input_file_path, output_file_path)
        except Exception as ex:
            messagebox.showerror("Error", f"Error converting file: {ex}")
            return
        
        for tab_content in self.tab_contents:
            tab_content.process_tab(output_file_path)

    def convert_rpt_to_txt(self, input_file_path, output_file_path):
        data = []
        
        with open(input_file_path, "r", encoding="utf-8") as file:
            is_data_section = False
            
            for line in file:
                line = line.strip()
                if line.startswith("Type"):
                    is_data_section = True
                    next(file)
                    continue
                
                if is_data_section and line.startswith("Net"):
                    values = self.extract_values(line)
                    if values:
                        self.add_unique(data, values)
        
        with open(output_file_path, "w", encoding="utf-8") as file:
            for values in data:
                file.write(",".join(values) + "\n")
            print("Data extracted and written to text file successfully.")
    
    def extract_values(self, line):
        parts = re.split(r'\s+', line.strip())
        if len(parts) >= 52:
            return [parts[0], parts[2], parts[5], parts[9], parts[12], parts[51]]
        return None
    
    def add_unique(self, data_list, new_item):
        if new_item not in data_list:
            data_list.append(new_item)


class TabContent(Frame):
    def __init__(self, parent, default_net_name, default_net_name2, default_net_name3):
        super().__init__(parent)
        
        self.net_name_fields = []
        self.line_to_line_areas = []
        self.line_to_via_areas = []
        self.line_to_shape_areas = []
        self.via_to_via_areas = []

        for i in range(3):
            net_name_label = Label(self, text="輸入net name")
            net_name_label.grid(row=0, column=i*4, padx=5, pady=5, sticky='w')
            
            net_name_field = Entry(self)
            net_name_field.grid(row=0, column=i*4+1, padx=5, pady=5)
            if i == 0:
                net_name_field.insert(0, default_net_name)
            elif i == 1:
                net_name_field.insert(0, default_net_name2)
            elif i == 2:
                net_name_field.insert(0, default_net_name3)
            self.net_name_fields.append(net_name_field)
            
            # Add titles and ScrolledText widgets
            line_to_line_label = Label(self, text="Line to Line")
            line_to_line_label.grid(row=1, column=i*4, padx=5, pady=5, sticky='w')
            line_to_line_area = scrolledtext.ScrolledText(self, height=10, width=60)
            line_to_line_area.grid(row=2, column=i*4, columnspan=2, padx=5, pady=5, sticky="nsew")
            self.line_to_line_areas.append(line_to_line_area)

            line_to_via_label = Label(self, text="Line to VIA")
            line_to_via_label.grid(row=3, column=i*4, padx=5, pady=5, sticky='w')
            line_to_via_area = scrolledtext.ScrolledText(self, height=10, width=60)
            line_to_via_area.grid(row=4, column=i*4, columnspan=2, padx=5, pady=5, sticky="nsew")
            self.line_to_via_areas.append(line_to_via_area)
            
            line_to_shape_label = Label(self, text="Line to Shape")
            line_to_shape_label.grid(row=5, column=i*4, padx=5, pady=5, sticky='w')
            line_to_shape_area = scrolledtext.ScrolledText(self, height=10, width=60)
            line_to_shape_area.grid(row=6, column=i*4, columnspan=2, padx=5, pady=5, sticky="nsew")
            self.line_to_shape_areas.append(line_to_shape_area)

            via_to_via_label = Label(self, text="VIA to VIA")
            via_to_via_label.grid(row=7, column=i*4, padx=5, pady=5, sticky='w')
            via_to_via_area = scrolledtext.ScrolledText(self, height=10, width=60)
            via_to_via_area.grid(row=8, column=i*4, columnspan=2, padx=5, pady=5, sticky="nsew")
            self.via_to_via_areas.append(via_to_via_area)
            
            self.grid_columnconfigure(i*4, weight=1)
            self.grid_columnconfigure(i*4+1, weight=1)
            self.grid_columnconfigure(i*4+2, weight=1)
            self.grid_columnconfigure(i*4+3, weight=1)

    def process_tab(self, file_path):
        for i in range(3):
            target_net_name = self.net_name_fields[i].get()
            line_to_line_list = []
            line_to_via_list = []
            line_to_shape_list = []
            via_to_via_list = []

            try:
                self.process_file(file_path, target_net_name, line_to_line_list, line_to_via_list, line_to_shape_list, via_to_via_list)
                self.display_results(line_to_line_list, self.line_to_line_areas[i])
                self.display_results(line_to_via_list, self.line_to_via_areas[i])
                self.display_results(line_to_shape_list, self.line_to_shape_areas[i])
                self.display_results(via_to_via_list, self.via_to_via_areas[i])
            except Exception as ex:
                messagebox.showerror("Error", f"Error processing file: {ex}")

    def process_file(self, file_path, target_net_name, line_to_line_list, line_to_via_list, line_to_shape_list, via_to_via_list):
        regex_target_net_name = Utils.wildcard_to_regex(target_net_name)
        pattern_target_net_name = re.compile(regex_target_net_name)

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) >= 6 and parts[0] == "Net":
                    if pattern_target_net_name.match(parts[1]):
                        line_to_line_list.append(f"{parts[1]},{parts[2]}")
                        line_to_via_list.append(f"{parts[1]},{parts[3]}")
                        line_to_shape_list.append(f"{parts[1]},{parts[4]}")
                        via_to_via_list.append(f"{parts[1]},{parts[5]}")

        # Sort lists in descending order
        line_to_line_list.sort()
        line_to_via_list.sort()
        line_to_shape_list.sort()
        via_to_via_list.sort()

    def display_results(self, result_list, text_area):
        text_area.delete(1.0, tk.END)
        for item in result_list:
            text_area.insert(tk.END, item + "\n")


if __name__ == "__main__":
    app = GUIApplication()
    app.mainloop()
