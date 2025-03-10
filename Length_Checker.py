import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Frame, Notebook, Entry, Button, Label
import os
import re
import shutil


class GUIApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Length Checker V1.2")
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
            "*P*E5_*TX*", "*P*E2_*X*", "*MDI*",
            "*SATA*_*X*", "CLK*", "", "", ""
        ]
        predefined_net_names2 = [
            "*P*E5_*RX*", "*P*E1_*X*", "",
            "", "", "", "", ""
        ]
        predefined_net_names3 = [
            "*P*E4_*X*", "*USB2*_D*", "", "",
            "", "", "", ""
        ]
        predefined_net_names4 = [
            "*P*E3_*X*", "*USB3*_*X*", "", "",
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

        # Clear the "Length reports" directory before processing tabs
        save_directory = os.path.join(os.getcwd(), "Length reports")
        os.makedirs(save_directory, exist_ok=True)  # 如果資料夾不存在，則建立
        for filename in os.listdir(save_directory):
            file_path = os.path.join(save_directory, filename)
            try:
                if os.path.isfile(file_path):  # 如果路徑內有檔案
                    os.unlink(file_path) 
                elif os.path.isdir(file_path):  # 如果路徑內有資料夾
                    shutil.rmtree(file_path)

            except Exception as e:
                print(f"Failed to delete {file_path}.")
        
        for i, tab_content in enumerate(self.tab_contents):
            tab_content.process_tab(output_file_path, self.tab_names[i], brd_name)  # 將 brd_name 傳給 process_tab
        
        self.combine_reports()  # 在處理完所有 tab 後自動整合報告

    @staticmethod
    def combine_reports():
        save_directory = os.path.join(os.getcwd(), "Length reports")
        combined_report_path = os.path.join(save_directory, "length_constraint_report.txt")

        try:
            with open(combined_report_path, "w", encoding="utf-8") as combined_file:
                for i in range(8):  # 處理 Tab 1 到 Tab 8
                    tab_filename = f"Tab_{i+1}.txt"
                    tab_filepath = os.path.join(save_directory, tab_filename)
                
                    if os.path.exists(tab_filepath):
                        with open(tab_filepath, "r", encoding="utf-8") as tab_file:
                            combined_file.write(tab_file.read())
                            combined_file.write("\n\n")  # 在每個報告之間添加分隔

            if os.stat(combined_report_path).st_size == 0:  # 判斷檔案資料是否為空
                with open(combined_report_path, "w", encoding="utf-8") as combined_file:
                    combined_file.write("The constrain settings are all correct!!\n\n") 

        except Exception as e:
            messagebox.showerror("Error", f"Error combining reports: {e}")
        print("Conbine_Reports output successfully.")

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
                try:
                    values[2] = int(float(values[2]))  # 將 part[7] (也就是 values[2]) 轉換為 int
                except ValueError:
                    print(f"Warning: Could not find the length of {values[1]}.")
                file.write(",".join(str(v) for v in values) + "\n")  # 將每一組數據用","組成一個字串，並換行，然後寫入到 .txt 文件中
            print("Convert RPT to TXT successfully.")
        
        return brd_name  # 返回 brd_name
    
    @staticmethod
    def extract_values(line):
        line = re.sub(r'\*\*', '', line)  # Remove "**" from the line
        parts = re.split(r'\s+', line.strip())  # 將file內的data依","方式做split
        if len(parts) >= 8:   # 假如split後有8個parts
            return [parts[0], parts[2], parts[7]]  # 則return指定位置part[]
        return None

    @staticmethod
    def add_unique(data, values):
        if values not in data:  # 假如values不在data list內
            data.append(values)  # 則將values添加到data list尾中

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


class TabContent(Frame):
    def __init__(self, parent, default_net_name1, default_net_name2, default_net_name3, default_net_name4):
        super().__init__(parent)
        
        self.net_name_fields = []
        self.length_fields = []
        self.match_areas = []
        self.no_match_areas = []

        for i in range(4):
            net_name_label = Label(self, text="輸入 net name")
            net_name_label.grid(row=0, column=i*2, padx=5, pady=5, sticky='w')
            
            net_name_field = Entry(self)
            net_name_field.grid(row=0, column=i*2+1, padx=5, pady=5)
            if i == 0:
                net_name_field.insert(0, default_net_name1)
            elif i == 1:
                net_name_field.insert(0, default_net_name2)
            elif i == 2:
                net_name_field.insert(0, default_net_name3)
            elif i == 3:
                net_name_field.insert(0, default_net_name4)
            self.net_name_fields.append(net_name_field)
            
            length_label = Label(self, text="設定線長")
            length_label.grid(row=1, column=i*2, padx=5, pady=5, sticky='w')
            
            length_field = Entry(self)
            length_field.grid(row=1, column=i*2+1, padx=5, pady=5)
            self.length_fields.append(length_field)
            
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

    def process_tab(self, file_path, tab_name, brd_name):
        all_match_lists = []
        all_no_match_lists = []

        for i in range(4):
            target_second_line = self.net_name_fields[i].get()
            target_third_line = self.length_fields[i].get()
            match_list = []
            no_match_list = []

            try:
                self.process_file(file_path, target_second_line, target_third_line, match_list, no_match_list)
                self.display_results(match_list, self.match_areas[i], no_match_list, self.no_match_areas[i])
                
                all_match_lists.append(match_list)
                all_no_match_lists.append(no_match_list)

            except Exception as e:
                messagebox.showerror("Error", f"Error processing file: {e}")

        self.output_report(all_no_match_lists, all_match_lists, tab_name, brd_name)
    
    def output_report(self, all_no_match_lists, all_match_lists, tab_name, brd_name):
        
        # 自動產生檔名並保存到指定路徑
        default_filename = tab_name.replace(" ", "_") + ".txt"  # 將空格替換為底線
        save_directory = os.path.join(os.getcwd(), "Length reports")  # 指定保存路徑為當前目錄下的 "reports" 資料夾
        save_path = os.path.join(save_directory, default_filename)

        if any(all_no_match_lists):
            report_content = f"Board File : {brd_name}\n\n"
            # report_content += f"{tab_name} Report\n\n"

            for i in range(4):
                report_content += f"\n{self.net_name_fields[i].get()}:{self.length_fields[i].get()}\n\n"
                # report_content += "Match List:\n"
                # if all_match_lists[i]:
                #     report_content += "\n".join(all_match_lists[i]) + "\n\n"
                # else:
                #     report_content += "\n\n"
                report_content += "【Mismatch List】\n"
                if all_no_match_lists[i]:
                    for item in all_no_match_lists[i]:
                        report_content += ",".join(item) + "\n"
                else:
                    report_content += "\n\n"
               
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
                        if target_third_line and target_third_line == parts[2]:
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

def length_checker():
    app = GUIApplication()
    app.mainloop()

if __name__ == "__main__":
    app = GUIApplication()
    app.mainloop()
