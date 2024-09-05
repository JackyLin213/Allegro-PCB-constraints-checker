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
        self.title("Spacing Checker V1.2")
        self.geometry("1280x850")
        # self.resizable(False, False)
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
            brd_name = self.convert_rpt_to_txt(input_file_path, output_file_path)  # 提取 brd_name
            
        except Exception as e:
            messagebox.showerror("Error", f"Error converting file: {e}")
            return
        
        for i, tab_content in enumerate(self.tab_contents):
            tab_content.process_tab(output_file_path, self.tab_names[i], brd_name)  # 將 brd_name 傳給 process_tab
        
        self.combine_reports()  # 在處理完所有 tab 後自動整合報告
    
    @staticmethod
    def combine_reports():
        save_directory = os.path.join(os.getcwd(), "Spacing reports")
        combined_report_path = os.path.join(save_directory, "spacing_constraint_report.txt")

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
        brd_name = None
        
        with open(input_file_path, "r", encoding="utf-8") as file:
            is_data_section = False
            
            for line in file:  # 逐行讀取 .rpt 檔案
                line = line.strip()  # 去除每行前後的空白字符

                if "Design:" in line:
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 2:
                        brd_name = parts[1]

                if line.startswith("Type"):
                    is_data_section = True
                    next(file)
                    continue
                
                if is_data_section and line.startswith("Net"):
                    values = self.extract_values(line)  # 調用 extract_values 函數從該行提取values
                    if values:  # 如果提取到values
                        self.add_unique(data, values)  # 調用 add_unique 函數將values添加到 data 列表中，確保不重複添加
        
        with open(output_file_path, "w", encoding="utf-8") as file:
            if brd_name:  # 如果成功提取到brd_name，則先寫入
                file.write(brd_name + "\n")
            for values in data:
                file.write(",".join(values) + "\n")  # 將每一組數據用","組成一個字串，並換行，然後寫入到 .txt 文件中
            # print("Data extracted and written to text file successfully.")

            return brd_name  # 返回 brd_name
    
    @staticmethod
    def extract_values(line):
        parts = re.split(r'\s+', line.strip())  # 將file內的data依","方式做split
        if len(parts) >= 52:   # 假如split後有52個parts
            return [parts[0], parts[2], parts[5], parts[9], parts[12], parts[51]]  # 則return指定位置part[]
        return None

    @staticmethod
    def add_unique(data, values):
        if values not in data:  # 假如values不在data list內
            data.append(values)  # 則將values添加到data list尾中


class TabContent(Frame):
    def __init__(self, parent, default_net_name1, default_net_name2, default_net_name3, default_net_name4):
        super().__init__(parent)
        
        self.net_name_fields = []
        self.line_to_line_areas = []
        self.line_to_via_areas = []
        self.line_to_shape_areas = []
        self.via_to_via_areas = []

        for i in range(4):
            net_name_label = Label(self, text="輸入net name")
            net_name_label.grid(row=0, column=i*4, padx=5, pady=5, sticky='w')
            
            net_name_field = Entry(self)
            net_name_field.grid(row=0, column=i*4+1, padx=5, pady=5)
            if i == 0:
                net_name_field.insert(0, default_net_name1)
            elif i == 1:
                net_name_field.insert(0, default_net_name2)
            elif i == 2:
                net_name_field.insert(0, default_net_name3)
            elif i == 3:
                net_name_field.insert(0, default_net_name4)
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

    def process_tab(self, file_path, tab_name, brd_name):
        all_line_to_line_lists = []
        all_line_to_via_lists = []
        all_line_to_shape_lists = []
        all_via_to_via_lists = []

        for i in range(4):
            target_net_name = self.net_name_fields[i].get()
            line_to_line_list = []
            line_to_via_list = []
            line_to_shape_list = []
            via_to_via_list = []

            try:
                self.process_file(file_path,
                                  target_net_name,
                                  line_to_line_list,
                                  line_to_via_list,
                                  line_to_shape_list,
                                  via_to_via_list
                                  )
                self.display_results(line_to_line_list, self.line_to_line_areas[i])
                self.display_results(line_to_via_list, self.line_to_via_areas[i])
                self.display_results(line_to_shape_list, self.line_to_shape_areas[i])
                self.display_results(via_to_via_list, self.via_to_via_areas[i])

                all_line_to_line_lists.append(line_to_line_list)
                all_line_to_via_lists.append(line_to_via_list)
                all_line_to_shape_lists.append(line_to_shape_list)
                all_via_to_via_lists.append(via_to_via_list)

            except Exception as e:
                messagebox.showerror("Error", f"Error processing file: {e}")

        self.output_report(all_line_to_line_lists,
                           all_line_to_via_lists,
                           all_line_to_shape_lists,
                           all_via_to_via_lists,
                           tab_name,
                           brd_name
                           )

    def output_report(self,
                      all_line_to_line_lists,
                      all_line_to_via_lists,
                      all_line_to_shape_lists,
                      all_via_to_via_lists,
                      tab_name,
                      brd_name
                      ):
        report_content = f"Board File : {brd_name}\n\n"
        report_content += f"{tab_name} Report\n\n"

        for i in range(4):
            report_content += f"\n{self.net_name_fields[i].get()}:\n\n"
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

                # messagebox.showinfo("Success", "Report saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving report: {e}")
    
    @staticmethod
    def process_file(file_path,
                     target_net_name,
                     line_to_line_list,
                     line_to_via_list,
                     line_to_shape_list,
                     via_to_via_list
                     ):
        regex_target_net_name = Utils.wildcard_to_regex(target_net_name)  # 將輸入的net name轉成regex type

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")  # 將file內的data依","方式做split
                if len(parts) >= 6 and parts[0] == "Net":  # 假如split後有6個part，且part[0] = NET，則繼續
                    if re.match(regex_target_net_name, parts[1]):  # 將regex_second_line和parts[1]做match
                        line_to_line_list.append(f"{parts[1]},{parts[2]}")
                        line_to_via_list.append(f"{parts[1]},{parts[3]}")
                        line_to_shape_list.append(f"{parts[1]},{parts[4]}")
                        via_to_via_list.append(f"{parts[1]},{parts[5]}")

        # Sort lists in descending order
        line_to_line_list.sort()
        line_to_via_list.sort()
        line_to_shape_list.sort()
        via_to_via_list.sort()

    @staticmethod
    def display_results(result_list, text_area):
        text_area.delete(1.0, tk.END)
        for item in result_list:
            text_area.insert(tk.END, item + "\n")


# if __name__ == "__main__":
def Spacing_Checker():
    app = GUIApplication()
    app.mainloop()
