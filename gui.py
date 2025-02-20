import tkinter as tk
from tkinter import messagebox
import random
import math

# 生成随机血压值的函数
def generate_blood_pressure():
    try:
        # 获取用户输入的参数
        diastolic_mean = float(diastolic_mean_entry.get())
        diastolic_std = float(diastolic_std_entry.get())
        systolic_mean = float(systolic_mean_entry.get())
        systolic_std = float(systolic_std_entry.get())
        
        # 生成随机血压值
        diastolic_pressure = random.gauss(diastolic_mean, diastolic_std)
        systolic_pressure = random.gauss(systolic_mean, systolic_std)
        
        # 确保血压值为正数
        diastolic_pressure = max(0, diastolic_pressure)
        systolic_pressure = max(0, systolic_pressure)
        
        # 显示生成的血压值
        result_label.config(text=f"生成的血压值:\n舒张压: {diastolic_pressure:.2f} mmHg\n收缩压: {systolic_pressure:.2f} mmHg")
    except ValueError:
        messagebox.showerror("输入错误", "请输入有效的数字")

# 创建主窗口
root = tk.Tk()
root.title("血压计模拟器")

# 创建标签和输入框
tk.Label(root, text="舒张压均值 (mmHg):").grid(row=0, column=0, padx=10, pady=5)
diastolic_mean_entry = tk.Entry(root)
diastolic_mean_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="舒张压方差 (mmHg):").grid(row=1, column=0, padx=10, pady=5)
diastolic_std_entry = tk.Entry(root)
diastolic_std_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="收缩压均值 (mmHg):").grid(row=2, column=0, padx=10, pady=5)
systolic_mean_entry = tk.Entry(root)
systolic_mean_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="收缩压方差 (mmHg):").grid(row=3, column=0, padx=10, pady=5)
systolic_std_entry = tk.Entry(root)
systolic_std_entry.grid(row=3, column=1, padx=10, pady=5)

# 创建生成血压值的按钮
generate_button = tk.Button(root, text="生成血压值", command=generate_blood_pressure)
generate_button.grid(row=4, column=0, columnspan=2, pady=10)

# 创建显示结果的标签
result_label = tk.Label(root, text="生成的血压值:\n舒张压: - mmHg\n收缩压: - mmHg")
result_label.grid(row=5, column=0, columnspan=2, pady=10)

# 运行主循环
root.mainloop()