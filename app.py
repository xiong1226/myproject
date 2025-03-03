from flask import Flask, render_template, request, jsonify
import threading
import time
import queue
import random
import math
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# 全局变量
stop_event = threading.Event()
log_queue = queue.Queue()
diastolic_pressures = []
systolic_pressures = []
timestamps = []
statuses = []
heart_rates = []
heart_rate_statuses = []
temperatures = []
temperature_statuses = []
calories_burned = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_logging', methods=['POST'])
def start_logging():
    global stop_event, log_queue
    stop_event.clear()
    sampling_period = float(request.form['sampling_period'])
    num_threads = int(request.form['num_threads'])

    for _ in range(num_threads):
        threading.Thread(target=generate_data, args=(sampling_period,)).start()

    return jsonify({"status": "started"})

@app.route('/stop_logging', methods=['POST'])
def stop_logging():
    global stop_event, log_queue
    stop_event.set()

    # 计算均值和方差
    if diastolic_pressures:
        diastolic_mean = sum(diastolic_pressures) / len(diastolic_pressures)
        diastolic_variance = sum((x - diastolic_mean) ** 2 for x in diastolic_pressures) / len(diastolic_pressures)

    if systolic_pressures:
        systolic_mean = sum(systolic_pressures) / len(systolic_pressures)
        systolic_variance = sum((x - systolic_mean) ** 2 for x in systolic_pressures) / len(systolic_pressures)

    # 保存数据到CSV文件
    save_to_csv()

    # 绘制数据点
    plot_data()

    return jsonify({"status": "stopped"})

@app.route('/get_logs', methods=['GET'])
def get_logs():
    logs = []
    while not log_queue.empty():
        logs.append(log_queue.get_nowait())
    return jsonify({"logs": logs})

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    global diastolic_pressures, systolic_pressures, timestamps, statuses, heart_rates, heart_rate_statuses, temperatures, temperature_statuses, calories_burned
    diastolic_pressures.clear()
    systolic_pressures.clear()
    timestamps.clear()
    statuses.clear()
    heart_rates.clear()
    heart_rate_statuses.clear()
    temperatures.clear()
    temperature_statuses.clear()
    calories_burned.clear()
    return jsonify({"status": "cleared"})

def generate_data(sampling_period):
    while not stop_event.is_set():
        try:
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

            diastolic_pressures.append(diastolic_pressure)
            systolic_pressures.append(systolic_pressure)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            timestamps.append(timestamp)

            statuses.append(status)  # 将状态添加到列表中

            # 生成心率数据
            heart_rate = random.randint(40, 120)  # 心率范围40-120
            heart_rate_status = determine_heart_rate_status(heart_rate)

            heart_rates.append(heart_rate)
            heart_rate_statuses.append(heart_rate_status)

            # 生成体温数据
            temperature = round(random.uniform(35.5, 38.0), 1)  # 体温范围35.5-38.0
            temperature_status = determine_temperature_status(temperature)

            temperatures.append(temperature)
            temperature_statuses.append(temperature_status)

            # 生成卡路里消耗数据
            calories_burned = random.uniform(0, 500)  # 卡路里消耗范围0-500
            calories_burned.append(calories_burned)

            log_message = (f"时间: {timestamp} - "
                           f"舒张压: {diastolic_pressure:.2f}, 收缩压: {systolic_pressure:.2f}, "
                           f"心率: {heart_rate}, 心率状态: {heart_rate_status}, "
                           f"体温: {temperature}, 体温状态: {temperature_status}, "
                           f"卡路里消耗: {calories_burned:.2f}, "
                           f"血压状态: {status}\n")
            log_queue.put(log_message)

            time.sleep(sampling_period)
        except Exception as e:
            error_message = f"输入错误: {e}\n"
            log_queue.put(error_message)
            break

def determine_heart_rate_status(heart_rate):
    if 60 <= heart_rate <= 100:
        return "正常心率"
    elif heart_rate < 60:
        return "心动过缓"
    else:
        return "心动过速"

def determine_temperature_status(temperature):
    if 36.1 <= temperature <= 37.2:
        return "正常体温"
    elif temperature < 36.1:
        return "体温过低"
    else:
        return "体温过高"

def save_to_csv():
    rounded_diastolic_pressures = [round(dp, 1) for dp in diastolic_pressures]
    rounded_systolic_pressures = [round(sp, 1) for sp in systolic_pressures]
    rounded_calories_burned = [round(cb, 1) for cb in calories_burned]

    data = {
        '时间': timestamps,
        '舒张压': rounded_diastolic_pressures,
        '收缩压': rounded_systolic_pressures,
        '心率': heart_rates,
        '心率状态': heart_rate_statuses,
        '体温': temperatures,
        '体温状态': temperature_statuses,
        '卡路里消耗': rounded_calories_burned,
        '血压状态': statuses
    }
    df = pd.DataFrame(data)

    if diastolic_pressures:
        diastolic_mean = sum(rounded_diastolic_pressures) / len(rounded_diastolic_pressures)
        diastolic_variance = sum((x - diastolic_mean) ** 2 for x in rounded_diastolic_pressures) / len(rounded_diastolic_pressures)
        df['舒张压均值'] = round(diastolic_mean, 1)
        df['舒张压方差'] = round(diastolic_variance, 1)

    if systolic_pressures:
        systolic_mean = sum(rounded_systolic_pressures) / len(rounded_systolic_pressures)
        systolic_variance = sum((x - systolic_mean) ** 2 for x in rounded_systolic_pressures) / len(rounded_systolic_pressures)
        df['收缩压均值'] = round(systolic_mean, 1)
        df['收缩压方差'] = round(systolic_variance, 1)

    df.to_csv("blood_pressure_data.csv", index=False, encoding='utf-8-sig')
    print("数据已保存到 blood_pressure_data.csv")

def plot_data():
    plt.figure(figsize=(10, 6))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    colors = []
    for systolic, diastolic in zip(systolic_pressures, diastolic_pressures):
        if systolic >= 140 or diastolic >= 90:
            colors.append('red')
        elif systolic < 90 or diastolic < 60:
            colors.append('black')
        else:
            colors.append('blue')
    plt.scatter(diastolic_pressures, systolic_pressures, c=colors, label='生成的数据点')
    
    x = range(0, 200)
    y = [2/3 * xi for xi in x]
    plt.plot(y, x, color='red', label='y = 2/3x')
    plt.xlabel('收缩压')
    plt.ylabel('舒张压')
    plt.title('血压数据点分布')
    plt.legend()
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # 绘制心率数据
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, heart_rates, label='心率')
    plt.axhline(y=60, color='red', linestyle='--', label='正常心率下限')
    plt.axhline(y=100, color='red', linestyle='--', label='正常心率上限')
    plt.xlabel('时间')
    plt.ylabel('心率 (次/分钟)')
    plt.title('心率变化')
    plt.legend()
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    heart_rate_plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # 绘制体温数据
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, temperatures, label='体温')
    plt.axhline(y=36.1, color='red', linestyle='--', label='正常体温下限')
    plt.axhline(y=37.2, color='red', linestyle='--', label='正常体温上限')
    plt.xlabel('时间')
    plt.ylabel('体温 (°C)')
    plt.title('体温变化')
    plt.legend()
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    temperature_plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return plot_url, heart_rate_plot_url, temperature_plot_url

if __name__ == "__main__":
    app.run(debug=True)