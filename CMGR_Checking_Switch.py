import tkinter as tk
from tkinter import ttk


from Impedance_Checker import Impedance_Checker
from Length_Checker import Length_Checker
from Spacing_Checker import Spacing_Checker


def run_script(script_name):
    try:
        if script_name == "Impedance_Checker":
            Impedance_Checker()
        elif script_name == "Length_Checker":
            Length_Checker()
        elif script_name == "Spacing_Checker":
            Spacing_Checker()

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
