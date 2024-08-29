import tkinter as tk
from tkinter import ttk
import subprocess

def run_script(script_name):
    try:
        subprocess.Popen(["python", script_name])
    except Exception as e:
        tk.messagebox.showerror("Error", f"Failed to run script: {e}")

root = tk.Tk()
root.title("Script Launcher")

# 創建一個 Combobox 來選擇要執行的腳本
script_options = ["Impedance_Checker_V1.1.py", "Length_Checker_V1.1.py", "Spacing_Checker_V1.1.py"]
selected_script = tk.StringVar()
script_combobox = ttk.Combobox(root, textvariable=selected_script, values=script_options)
script_combobox.set(script_options[0])  # 預設選擇第一個腳本
script_combobox.pack(pady=20)

# 創建一個按鈕來執行選定的腳本
run_button = ttk.Button(root, text="Run Script", command=lambda: run_script(selected_script.get()))
run_button.pack()

root.mainloop()