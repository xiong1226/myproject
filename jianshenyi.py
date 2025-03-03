import tkinter as tk
from tkinter import ttk
import random
import math
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

class BloodPressureMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("智能健身衣模拟器")
        self.root.geometry("800x600")

        self.background_image = Image.open("1.jpg")  # 确保图片路径正确
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(self.root, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.stop_event = threading.Event()
        self.log_queue = queue.Queue()
        self.thread_pool = ThreadPoolExecutor(max_workers=10)  # 线程池，最多同时运行10个线程

        self.diastolic_pressures = []
        self.systolic_pressures = []
        self.timestamps = []
        self.statuses = []  # 新增列表用于存储血压状态
        self.heart_rates = []  # 新增列表用于存储心率数据
        self.heart_rate_statuses = []  # 新增列表用于存储心率状态
        self.temperatures = []  # 新增列表用于存储体温数据
        self.temperature_statuses = []  # 新增列表用于存储体温状态
        self.calories_burned = []  # 新增列表用于存储卡路里消耗数据

        self.create_widgets()
        self.setup_layout()
        self.process_queue()

    def create_widgets(self):
        # 创建参数设置板块
        self.param_frame_left = ttk.LabelFrame(self.root, text="参数设置 (左)")
        self.param_frame_left.grid(row=0, column=0, padx=20, pady=0, sticky="nsew")

        self.param_label6 = ttk.Label(self.param_frame_left, text="采样周期 (秒):")
        self.param_label6.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.param_entry6 = ttk.Entry(self.param_frame_left)
        self.param_entry6.grid(row=0, column=1, padx=10, pady=10)

        self.param_label7 = ttk.Label(self.param_frame_left, text="线程数量:")
        self.param_label7.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.param_spinbox7 = ttk.Spinbox(self.param_frame_left, from_=1, to=10, increment=1, width=5)
        self.param_spinbox7.grid(row=1, column=1, padx=10, pady=10)

        self.param_label1 = ttk.Label(self.param_frame_left, text="舒张压均值:")
        self.param_label1.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.param_entry1 = ttk.Entry(self.param_frame_left, state=tk.DISABLED)
        self.param_entry1.grid(row=2, column=1, padx=10, pady=10)

        self.param_frame_right = ttk.LabelFrame(self.root, text="参数设置 (右)")
        self.param_frame_right.grid(row=0, column=1, padx=20, pady=0, sticky="nsew")

        self.param_label2 = ttk.Label(self.param_frame_right, text="舒张压方差:")
        self.param_label2.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.param_entry2 = ttk.Entry(self.param_frame_right, state=tk.DISABLED)
        self.param_entry2.grid(row=0, column=1, padx=10, pady=10)

        self.param_label3 = ttk.Label(self.param_frame_right, text="收缩压均值:")
        self.param_label3.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.param_entry3 = ttk.Entry(self.param_frame_right, state=tk.DISABLED)
        self.param_entry3.grid(row=1, column=1, padx=10, pady=10)

        self.param_label4 = ttk.Label(self.param_frame_right, text="收缩压方差:")
        self.param_label4.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.param_entry4 = ttk.Entry(self.param_frame_right, state=tk.DISABLED)
        self.param_entry4.grid(row=2, column=1, padx=10, pady=10)

        # 创建日志板块
        self.log_frame = ttk.LabelFrame(self.root, text="日志")
        self.log_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        self.log_text = tk.Text(self.log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # 添加日志背景图片
        log_background_image = Image.open("1.jpg")  # 确保图片路径正确
        log_background_photo = ImageTk.PhotoImage(log_background_image)
        self.log_background_label = tk.Label(self.log_frame, image=log_background_photo)
        self.log_background_label.image = log_background_photo  # 保持对图片的引用，防止被垃圾回收
        self.log_background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 创建开始和停止按钮
        start_icon = Image.open("ooo.png")  # 确保图片路径正确
        start_icon = start_icon.resize((30, 30), Image.LANCZOS)
        self.start_photo = ImageTk.PhotoImage(start_icon)
        self.start_button = ttk.Button(self.root, text="开始", command=self.start_logging)
        self.start_button.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        stop_icon = Image.open("ooo.png")  # 确保图片路径正确
        stop_icon = stop_icon.resize((30, 30), Image.LANCZOS)
        self.stop_photo = ImageTk.PhotoImage(stop_icon)
        self.stop_button = ttk.Button(self.root, text="停止", command=self.stop_logging, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # 创建清理日志按钮
        clear_icon = Image.open("ooo.png")  # 确保图片路径正确
        clear_icon = clear_icon.resize((30, 30), Image.LANCZOS)
        self.clear_photo = ImageTk.PhotoImage(clear_icon)
        self.clear_button = ttk.Button(self.root, text="清理日志", command=self.clear_log)
        self.clear_button.grid(row=2, column=2, padx=10, pady=10, sticky="w")

        # 创建绘图按钮
        plot_icon = Image.open("ooo.png")  # 确保图片路径正确
        plot_icon = plot_icon.resize((30, 30), Image.LANCZOS)
        self.plot_photo = ImageTk.PhotoImage(plot_icon)
        self.plot_button = ttk.Button(self.root, text="绘图", command=self.plot_data)
        self.plot_button.grid(row=2, column=3, padx=10, pady=10, sticky="w")

    def setup_layout(self):
        self.root.grid_rowconfigure(0, weight=2)  # 参数设置区域权重更大
        self.root.grid_rowconfigure(1, weight=1)  # 日志区域权重更小
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        style = ttk.Style()
        style.configure('TButton', foreground='blue')
        style.configure('TLabel', foreground='black', font=('Arial', 10))
        style.configure('TEntry', foreground='black', font=('Arial', 10))

    def generate_random_value(self, mean, variance):
        std_dev = math.sqrt(variance)
        return random.gauss(mean, std_dev)

    def determine_blood_pressure_status(self, systolic, diastolic):
        if systolic < 120 and diastolic < 80:
            return "正常血压"
        elif 120 <= systolic < 130 and diastolic < 80:
            return "高血压前期"
        elif (130 <= systolic < 140) or (80 <= diastolic < 90):
            return "高血压 1级"
        elif systolic >= 140 or diastolic >= 90:
            return "高血压 2级"
        elif systolic >= 180 or diastolic >= 120:
            return "高血压危象"
        else:
            return "未知状态"

    def determine_heart_rate_status(self, heart_rate):
        if 60 <= heart_rate <= 100:
            return "正常心率"
        elif heart_rate < 60:
            return "心动过缓"
        else:
            return "心动过速"

    def determine_temperature_status(self, temperature):
        if 36.1 <= temperature <= 37.2:
            return "正常体温"
        elif temperature < 36.1:
            return "体温过低"
        else:
            return "体温过高"

    def start_logging(self):
        try:
            sampling_period = float(self.param_entry6.get())
            if sampling_period <= 0:
                raise ValueError("采样周期必须大于0")
        except ValueError as e:
            self.log_queue.put(f"输入错误: {e}\n")
            return

        self.stop_event.clear()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # 获取用户选择的线程数量
        num_threads = int(self.param_spinbox7.get())

        # 启动指定数量的线程
        for _ in range(num_threads):
            self.thread_pool.submit(self.generate_data)

    def stop_logging(self):
        self.stop_event.set()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        # 计算均值和方差
        if self.diastolic_pressures:
            diastolic_mean = sum(self.diastolic_pressures) / len(self.diastolic_pressures)
            diastolic_variance = sum((x - diastolic_mean) ** 2 for x in self.diastolic_pressures) / len(self.diastolic_pressures)
            self.param_entry1.config(state=tk.NORMAL)
            self.param_entry1.delete(0, tk.END)
            self.param_entry1.insert(0, f"{diastolic_mean:.2f}")
            self.param_entry1.config(state=tk.DISABLED)

        if self.systolic_pressures:
            systolic_mean = sum(self.systolic_pressures) / len(self.systolic_pressures)
            systolic_variance = sum((x - systolic_mean) ** 2 for x in self.systolic_pressures) / len(self.systolic_pressures)
            self.param_entry3.config(state=tk.NORMAL)
            self.param_entry3.delete(0, tk.END)
            self.param_entry3.insert(0, f"{systolic_mean:.2f}")
            self.param_entry3.config(state=tk.DISABLED)

            self.param_entry2.config(state=tk.NORMAL)
            self.param_entry2.delete(0, tk.END)
            self.param_entry2.insert(0, f"{diastolic_variance:.2f}")
            self.param_entry2.config(state=tk.DISABLED)

            self.param_entry4.config(state=tk.NORMAL)
            self.param_entry4.delete(0, tk.END)
            self.param_entry4.insert(0, f"{systolic_variance:.2f}")
            self.param_entry4.config(state=tk.DISABLED)

        # 保存数据到CSV文件
        self.save_to_csv()
        
        # 绘制数据点
        self.plot_data()

    def generate_data(self):
        while not self.stop_event.is_set():
            try:
                sampling_period = float(self.param_entry6.get())

                if sampling_period <= 0:
                    raise ValueError("采样周期必须大于0")

                # 根据概率分布生成血压状态
                rand_val = random.random()
                if rand_val < 0.26:
                    status = "高血压"
                elif rand_val < 0.91:
                    status = "正常血压"
                else:
                    status = "低血压"

                # 根据状态生成血压值
                if status == "高血压":
                    systolic_pressure = random.uniform(140, 200)  # 高血压收缩压范围
                    diastolic_pressure = random.uniform(90, 120)  # 高血压舒张压范围
                elif status == "正常血压":
                    systolic_pressure = random.uniform(90, 139)  # 正常血压收缩压范围
                    diastolic_pressure = random.uniform(60, 89)  # 正常血压舒张压范围
                else:
                    systolic_pressure = random.uniform(70, 89)  # 低血压收缩压范围
                    diastolic_pressure = random.uniform(40, 59)  # 低血压舒张压范围

                # 调整数据点更接近 y = 2/3x
                diastolic_pressure = systolic_pressure * 2 / 3 + random.gauss(0, 5)

                # 确保生成的压力值在合理的范围内
                systolic_pressure = max(0, systolic_pressure)
                diastolic_pressure = max(0, diastolic_pressure)

                self.diastolic_pressures.append(diastolic_pressure)
                self.systolic_pressures.append(systolic_pressure)
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                self.timestamps.append(timestamp)

                self.statuses.append(status)  # 将状态添加到列表中

                # 生成心率数据
                heart_rate = random.randint(40, 120)  # 心率范围40-120
                heart_rate_status = self.determine_heart_rate_status(heart_rate)

                self.heart_rates.append(heart_rate)
                self.heart_rate_statuses.append(heart_rate_status)

                # 生成体温数据
                temperature = round(random.uniform(35.5, 38.0), 1)  # 体温范围35.5-38.0
                temperature_status = self.determine_temperature_status(temperature)

                self.temperatures.append(temperature)
                self.temperature_statuses.append(temperature_status)

                # 生成卡路里消耗数据
                calories_burned = random.uniform(0, 500)  # 卡路里消耗范围0-500
                self.calories_burned.append(calories_burned)

                log_message = (f"时间: {timestamp} - "
                               f"舒张压: {diastolic_pressure:.2f}, 收缩压: {systolic_pressure:.2f}, "
                               f"心率: {heart_rate}, 心率状态: {heart_rate_status}, "
                               f"体温: {temperature}, 体温状态: {temperature_status}, "
                               f"卡路里消耗: {calories_burned:.2f}, "
                               f"血压状态: {status}\n")
                self.log_queue.put(log_message)

                time.sleep(sampling_period)
            except ValueError as e:
                error_message = f"输入错误: {e}\n"
                self.log_queue.put(error_message)
                break

    def process_queue(self):
        try:
            while True:
                log_message = self.log_queue.get_nowait()
                self.update_log(log_message)
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)

    def update_log(self, message):
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.diastolic_pressures.clear()
        self.systolic_pressures.clear()
        self.timestamps.clear()
        self.statuses.clear()  # 清空状态列表

    def save_to_csv(self):
        # 对数据进行保留一位小数的处理
        rounded_diastolic_pressures = [round(dp, 1) for dp in self.diastolic_pressures]
        rounded_systolic_pressures = [round(sp, 1) for sp in self.systolic_pressures]
        rounded_calories_burned = [round(cb, 1) for cb in self.calories_burned]  # 卡路里消耗数据保留一位小数

        data = {
            '时间': self.timestamps,
            '舒张压': rounded_diastolic_pressures,
            '收缩压': rounded_systolic_pressures,
            '心率': self.heart_rates,
            '心率状态': self.heart_rate_statuses,
            '体温': self.temperatures,
            '体温状态': self.temperature_statuses,
            '卡路里消耗': rounded_calories_burned,  # 新增卡路里消耗列
            '血压状态': self.statuses
        }
        df = pd.DataFrame(data)

        if self.diastolic_pressures:
            diastolic_mean = sum(rounded_diastolic_pressures) / len(rounded_diastolic_pressures)
            diastolic_variance = sum((x - diastolic_mean) ** 2 for x in rounded_diastolic_pressures) / len(rounded_diastolic_pressures)
            df['舒张压均值'] = round(diastolic_mean, 1)
            df['舒张压方差'] = round(diastolic_variance, 1)

        if self.systolic_pressures:
            systolic_mean = sum(rounded_systolic_pressures) / len(rounded_systolic_pressures)
            systolic_variance = sum((x - systolic_mean) ** 2 for x in rounded_systolic_pressures) / len(rounded_systolic_pressures)
            df['收缩压均值'] = round(systolic_mean, 1)
            df['收缩压方差'] = round(systolic_variance, 1)

        df.to_csv("blood_pressure_data.csv", index=False, encoding='utf-8-sig')
        print("数据已保存到 blood_pressure_data.csv")

    def plot_data(self):
        plt.figure(figsize=(10, 6))

        plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        colors = []
        for systolic, diastolic in zip(self.systolic_pressures, self.diastolic_pressures):
            if systolic >= 140 or diastolic >= 90:
                colors.append('red')  # 高血压
            elif systolic < 90 or diastolic < 60:
                colors.append('black')  # 低血压
            else:
                colors.append('blue')  # 正常血压
        plt.scatter(self.diastolic_pressures, self.systolic_pressures, c=colors, label='生成的数据点')
        
        # 绘制 y = 2/3x 的基准线
        x = range(0, 200)
        y = [2/3 * xi for xi in x]
        plt.plot(y, x, color='red', label='y = 2/3x')
        plt.xlabel('收缩压')
        plt.ylabel('舒张压')
        plt.title('血压数据点分布')
        plt.legend()
        plt.grid(True)
        plt.show()

        # 绘制心率数据
        plt.figure(figsize=(10, 6))
        plt.plot(self.timestamps, self.heart_rates, label='心率')
        plt.axhline(y=60, color='red', linestyle='--', label='正常心率下限')
        plt.axhline(y=100, color='red', linestyle='--', label='正常心率上限')
        plt.xlabel('时间')
        plt.ylabel('心率 (次/分钟)')
        plt.title('心率变化')
        plt.legend()
        plt.grid(True)
        plt.show()

        # 绘制体温数据
        plt.figure(figsize=(10, 6))
        plt.plot(self.timestamps, self.temperatures, label='体温')
        plt.axhline(y=36.1, color='red', linestyle='--', label='正常体温下限')
        plt.axhline(y=37.2, color='red', linestyle='--', label='正常体温上限')
        plt.xlabel('时间')
        plt.ylabel('体温 (°C)')
        plt.title('体温变化')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = BloodPressureMonitor(root)
    root.mainloop()