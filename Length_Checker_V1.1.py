import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Frame, Notebook, Entry, Button, Label
import os
import re


class GUIApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Length Checker V1.1")
        self.geometry("1250x680")
        self.resizable(False, False)
        self.tab_contents = []
        self.tab_names = []
        
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
        
        predefined_net_names1 = [
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
        predefined_net_names4 = [
            "", "", "", "",
            "", "", "", ""
        ]
        
        # 定義出 8 個 tab，並分別帶入預設net name
        for i in range(8):
            tab_content = TabContent(self,
                                     predefined_net_names1[i],
                                     predefined_net_names2[i],
                                     predefined_net_names3[i],
                                     predefined_net_names4[i]
                                     )
            tab_name = f"Tab {i+1}"
            tab_control.add(tab_content, text=tab_name)
            self.tab_contents.append(tab_content)
            self.tab_names.append(tab_name)

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
        output_file_path = os.path.join(os.getcwd(), "rpt.txt")
        
        if not input_file_path:
            messagebox.showwarning("Warning", "Please select a file.")
            return
        
        try:
            self.convert_rpt_to_txt(input_file_path, output_file_path)

        except Exception as e:
            messagebox.showerror("Error", f"Error converting file: {e}")
            return
        
        for i, tab_content in enumerate(self.tab_contents):
            tab_content.process_tab(output_file_path, self.tab_names[i])
        
        self.combine_reports()  # 在處理完所有 tab 後自動整合報告

    @staticmethod
    def combine_reports():
        save_directory = os.path.join(os.getcwd(), "Length reports")
        combined_report_path = os.path.join(save_directory, "combined_length__report.txt")

        try:
            with open(combined_report_path, "w", encoding="utf-8") as combined_file:
                for i in range(8):  # 處理 Tab 1 到 Tab 8
                    tab_filename = f"Tab_{i+1}.txt"
                    tab_filepath = os.path.join(save_directory, tab_filename)
                
                    if os.path.exists(tab_filepath):
                        with open(tab_filepath, "r", encoding="utf-8") as tab_file:
                            combined_file.write(tab_file.read())
                            combined_file.write("\n\n")  # 在每個報告之間添加分隔
                            
        except Exception as e:
            messagebox.showerror("Error", f"Error combining reports: {e}")

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
            # print("Data extracted and written to text file successfully.")

    @staticmethod
    def extract_values(line):
        parts = re.split(r'\s+', line.strip())
        if len(parts) >= 4:
            return [parts[0], parts[2], parts[7]]
        return None

    @staticmethod
    def add_unique(data_list, new_item):
        if new_item not in data_list:
            data_list.append(new_item)
    
    def wildcard_to_regex(self, wildcard):
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


class TabContent(Frame):
    def __init__(self, parent, default_net_name, default_net_name2, default_net_name3, default_net_name4):
        super().__init__(parent)
        
        self.net_name_fields = []
        self.impedance_fields = []
        self.match_areas = []
        self.no_match_areas = []

        for i in range(4):
            net_name_label = Label(self, text="輸入 net name")
            net_name_label.grid(row=0, column=i*2, padx=5, pady=5, sticky='w')
            
            net_name_field = Entry(self)
            net_name_field.grid(row=0, column=i*2+1, padx=5, pady=5)
            if i == 0:
                net_name_field.insert(0, default_net_name)
            elif i == 1:
                net_name_field.insert(0, default_net_name2)
            elif i == 2:
                net_name_field.insert(0, default_net_name3)
            elif i == 3:
                net_name_field.insert(0, default_net_name4)
            self.net_name_fields.append(net_name_field)
            
            impedance_label = Label(self, text="設定線長")
            impedance_label.grid(row=1, column=i*2, padx=5, pady=5, sticky='w')
            
            impedance_field = Entry(self)
            impedance_field.grid(row=1, column=i*2+1, padx=5, pady=5)
            self.impedance_fields.append(impedance_field)
            
            # PASS Label above match_area
            pass_label = Label(self, text="PASS")
            pass_label.grid(row=2, column=i*2, columnspan=2, padx=5, pady=5, sticky='w')

            match_area = scrolledtext.ScrolledText(self, height=15, width=40)
            match_area.grid(row=3, column=i*2, columnspan=2, padx=5, pady=5)
            self.match_areas.append(match_area)

            # FAIL Label above no_match_area
            fail_label = Label(self, text="FAIL")
            fail_label.grid(row=4, column=i*2, columnspan=2, padx=5, pady=5, sticky='w')

            no_match_area = scrolledtext.ScrolledText(self, height=15, width=40)
            no_match_area.grid(row=5, column=i*2, columnspan=2, padx=5, pady=5)
            self.no_match_areas.append(no_match_area)

    def process_tab(self, file_path, tab_name):
        all_match_lists = []
        all_no_match_lists = []

        for i in range(4):
            target_second_line = self.net_name_fields[i].get()
            target_third_line = self.impedance_fields[i].get()
            match_list = []
            no_match_list = []

            try:
                self.process_file(file_path, target_second_line, target_third_line, match_list, no_match_list)
                self.display_results(match_list, self.match_areas[i], no_match_list, self.no_match_areas[i])
                
                all_match_lists.append(match_list)
                all_no_match_lists.append(no_match_list)

            except Exception as e:
                messagebox.showerror("Error", f"Error processing file: {e}")

        self.output_report(all_no_match_lists, tab_name)
    
    def output_report(self, all_no_match_lists, tab_name):
        report_content = f"{tab_name} Report\n\n"

        for i in range(4):
            report_content += f"\n{self.net_name_fields[i].get()}:{self.impedance_fields[i].get()}\n\n"
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

            # 自動產生檔名並保存到指定路徑
            default_filename = tab_name.replace(" ", "_") + ".txt"  # 將空格替換為底線
            save_directory = os.path.join(os.getcwd(), "Length reports")  # 指定保存路徑為當前目錄下的 "reports" 資料夾
            os.makedirs(save_directory, exist_ok=True)  # 如果資料夾不存在，則建立
            save_path = os.path.join(save_directory, default_filename)

            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(report_content)

                # messagebox.showinfo("Success", "Report saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving report: {e}")
    
    def process_file(self, file_path, target_second_line, target_third_line, match_list, no_match_list):
        regex_second_line = self.master.wildcard_to_regex(target_second_line)  # 將輸入的net name轉成regex type

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")  # 將file內的data依","方式做split
                if len(parts) == 3 and parts[0] == "Net":  # 假如split後有3個part，且part[0] = NET，則繼續
                    if re.match(regex_second_line, parts[1]):  # 將regex_second_line和parts[1]做match
                        if target_third_line and target_third_line in parts[2]:
                            match_list.append(parts[1])
                        else:
                            no_match_list.append([parts[1], parts[2]])

        # Sort lists in descending order
        match_list.sort()
        no_match_list.sort()
        
    @staticmethod
    def display_results(match_list, match_area, no_match_list, no_match_area):
        match_area.delete(1.0, tk.END)
        no_match_area.delete(1.0, tk.END)
        
        for item in match_list:
            match_area.insert(tk.END, item + "\n")
        
        for item in no_match_list:
            no_match_area.insert(tk.END, ",".join(item) + "\n")


if __name__ == "__main__":
    app = GUIApplication()
    app.mainloop()
