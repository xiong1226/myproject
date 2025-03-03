import tkinter as tk
from tkinter import ttk, scrolledtext
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

# 全局变量
step_count = 0
distance = 0.0
calories = 0.0
start_time = time.time()

# 运动评级阈值
HEART_RATE_THRESHOLD = {'low': 60, 'high': 100}  # 心率阈值
BREATH_RATE_THRESHOLD = {'low': 12, 'high': 20}  # 呼吸频率阈值

# 欢迎界面
def welcome_screen():
    welcome_window = tk.Toplevel()
    welcome_window.title("欢迎使用智能健身衣")
    welcome_window.geometry("300x200")

    label = ttk.Label(welcome_window, text="欢迎使用智能健身衣", font=("Arial", 16))
    label.pack(pady=20)

    enter_button = ttk.Button(welcome_window, text="进入", command=lambda: [welcome_window.destroy(), main_screen()])
    enter_button.pack(pady=10)

    exit_button = ttk.Button(welcome_window, text="退出", command=lambda: [welcome_window.destroy(), exit_screen()])
    exit_button.pack(pady=10)

# 主界面
def main_screen():
    global step_count, distance, calories, start_time

    main_window = tk.Toplevel()
    main_window.title("智能健身衣 - 主界面")
    main_window.geometry("800x600")

    # 实时数据显示
    frame_data = ttk.LabelFrame(main_window, text="实时数据")
    frame_data.pack(padx=10, pady=10, fill='x')

    labels = ['心率', '呼吸率', '体温', '血压', '步数', '运动距离', '消耗的卡路里', '运动时长', '运动评级']
    entries = {}

    for i, label in enumerate(labels):
        ttk.Label(frame_data, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
        entries[label] = ttk.Label(frame_data, text="0")
        entries[label].grid(row=i, column=1, padx=5, pady=2)

    # 肌电图绘制
    frame_emg = ttk.LabelFrame(main_window, text="肌电图")
    frame_emg.pack(padx=10, pady=10, fill='both', expand=True)

    fig, ax = plt.subplots(figsize=(5, 2))
    canvas = FigureCanvasTkAgg(fig, master=frame_emg)
    canvas.get_tk_widget().pack(fill='both', expand=True)

    # 模拟肌电图数据
    emg_data = [0] * 10  # 初始化肌电图数据

    def update_data():
        global step_count, distance, calories, start_time

        # 更新步数、距离、卡路里和运动时长
        step_count += random.randint(1, 3)
        distance += step_count * 0.0008  # 假设每步0.8米
        calories += step_count * 0.05  # 假设每步消耗0.05卡路里
        elapsed_time = time.time() - start_time

        # 生成随机数据
        heart_rate = random.randint(80, 120)
        breath_rate = random.randint(15, 25)
        body_temp = random.uniform(36.5, 37.5)
        blood_pressure = f"{random.randint(110, 130)}/{random.randint(70, 80)}"

        # 更新实时数据
        entries['心率'].config(text=str(heart_rate))
        entries['呼吸率'].config(text=str(breath_rate))
        entries['体温'].config(text=f"{body_temp:.1f}°C")
        entries['血压'].config(text=blood_pressure)
        entries['步数'].config(text=str(step_count))
        entries['运动距离'].config(text=f"{distance:.2f} 米")
        entries['消耗的卡路里'].config(text=f"{calories:.2f} 卡")
        entries['运动时长'].config(text=f"{int(elapsed_time // 60)} 分 {int(elapsed_time % 60)} 秒")

        # 运动评级
        if heart_rate > HEART_RATE_THRESHOLD['high'] and breath_rate > BREATH_RATE_THRESHOLD['high']:
            rating = "运动剧烈"
        elif heart_rate < HEART_RATE_THRESHOLD['low'] and breath_rate < BREATH_RATE_THRESHOLD['low']:
            rating = "运动过缓"
        else:
            rating = "运动适中"
        entries['运动评级'].config(text=rating)

        # 更新肌电图数据
        emg_data.pop(0)  # 移除最旧的数据点
        emg_data.append(random.uniform(0.5, 1.5))  # 添加新的数据点

        # 绘制肌电图
        ax.clear()
        ax.plot(emg_data, color='blue')
        ax.set_ylim(0, 2)  # 设置Y轴范围
        ax.set_title("肌电图")
        canvas.draw()

        # 每隔1秒更新一次
        main_window.after(1000, update_data)

    update_data()

    # 操作按钮
    frame_buttons = ttk.Frame(main_window)
    frame_buttons.pack(padx=10, pady=(0, 10))

    log_button = ttk.Button(frame_buttons, text="生成工作日志", command=lambda: [main_window.destroy(), log_screen()])
    log_button.grid(row=0, column=0, padx=5, pady=5)

    back_button = ttk.Button(frame_buttons, text="返回主界面", command=lambda: [main_window.destroy(), welcome_screen()])
    back_button.grid(row=0, column=1, padx=5, pady=5)

    exit_button = ttk.Button(frame_buttons, text="退出", command=lambda: [main_window.destroy(), exit_screen()])
    exit_button.grid(row=0, column=2, padx=5, pady=5)

# 工作日志界面
def log_screen():
    log_window = tk.Toplevel()
    log_window.title("智能健身衣 - 工作日志")
    log_window.geometry("600x400")

    log_text = scrolledtext.ScrolledText(log_window, width=40, height=10)
    log_text.pack(padx=5, pady=5, fill='both', expand=True)

    def update_log():
        log_text.insert(tk.END, f"心率: {random.randint(80, 120)}, 呼吸率: {random.randint(15, 25)}, 体温: {random.uniform(36.5, 37.5):.1f}°C, 血压: {random.randint(110, 130)}/{random.randint(70, 80)}\n")
        log_text.see(tk.END)
        log_window.after(1000, update_log)

    update_log()

    # 操作按钮
    frame_buttons = ttk.Frame(log_window)
    frame_buttons.pack(padx=10, pady=(0, 10))

    back_button = ttk.Button(frame_buttons, text="返回主界面", command=lambda: [log_window.destroy(), main_screen()])
    back_button.grid(row=0, column=0, padx=5, pady=5)

    exit_button = ttk.Button(frame_buttons, text="退出", command=lambda: [log_window.destroy(), exit_screen()])
    exit_button.grid(row=0, column=1, padx=5, pady=5)

# 退出界面
def exit_screen():
    exit_window = tk.Toplevel()
    exit_window.title("感谢使用")
    exit_window.geometry("300x200")

    label = ttk.Label(exit_window, text="感谢您的使用，开启下一段健身之旅", font=("Arial", 12))
    label.pack(pady=50)

    exit_button = ttk.Button(exit_window, text="退出", command=exit_window.quit)
    exit_button.pack(pady=10)

# 启动欢迎界面
welcome_screen()

# 运行主循环
tk.mainloop()