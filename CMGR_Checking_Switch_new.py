import tkinter as tk
from tkinter import ttk


def run_script(script_name):
    try:
        if script_name == "Impedance_Checker":
            from Impedance_Checker_new import impedance_checker  # 延遲導入
            impedance_checker()
        elif script_name == "Length_Checker":
            from Length_Checker_new import length_checker  # 延遲導入
            length_checker()
        elif script_name == "Spacing_Checker":
            from Spacing_Checker_new import spacing_checker  # 延遲導入
            spacing_checker()

    except Exception as e:
        tk.messagebox.showerror("Error", f"Failed to run script: {e}")


root = tk.Tk()
root.title("CMGR_Checking_Switch")
root.geometry("400x100")

# 創建一個 Combobox 來選擇要執行的腳本
script_options = ["Impedance_Checker", "Length_Checker", "Spacing_Checker"]
selected_script = tk.StringVar()
script_combobox = ttk.Combobox(root, textvariable=selected_script, values=script_options, width=25)
script_combobox.set(script_options[0])  # 預設選擇第一個腳本
script_combobox.pack(pady=20)

# 創建一個按鈕來執行選定的腳本
run_button = ttk.Button(root, text="Run Function", command=lambda: run_script(selected_script.get()))
run_button.pack()

root.mainloop()