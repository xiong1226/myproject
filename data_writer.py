import logging
import pandas as pd
import tkinter as tk
from tkinter import scrolledtext

# 配置日志记录
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 创建主窗口
root = tk.Tk()
root.title("Data and Log Viewer")

# 创建文本框来显示数据
data_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=10)
data_text.grid(column=0, row=0, padx=10, pady=10)

# 创建文本框来显示日志
log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=10)
log_text.grid(column=0, row=1, padx=10, pady=10)

def write_data_to_file(data, file_path):
    """
    将数据写入指定文件（支持Excel和TXT），并记录日志。
    
    :param data: 要写入的数据，可以是DataFrame或列表
    :param file_path: 文件路径
    """
    try:
        if isinstance(data, pd.DataFrame):
            if file_path.endswith('.txt'):
                data.to_csv(file_path, index=False, sep='\t', header=True)
            else:
                data.to_excel(file_path, index=False)
        elif isinstance(data, list):
            df = pd.DataFrame(data, columns=['Data'])
            if file_path.endswith('.txt'):
                df.to_csv(file_path, index=False, sep='\t', header=True)
            else:
                df.to_excel(file_path, index=False)
        else:
            raise ValueError("数据类型不支持，必须是DataFrame或列表")
        logging.info(f"数据已成功写入文件: {file_path}")
        # 更新数据文本框
        data_text.delete(1.0, tk.END)
        data_text.insert(tk.END, df.to_string(index=False))
        # 更新日志文本框
        with open('app.log', 'r') as log_file:
            log_text.delete(1.0, tk.END)
            log_text.insert(tk.END, log_file.read())
    except Exception as e:
        logging.error(f"写入文件时发生错误: {e}")
        # 更新日志文本框
        with open('app.log', 'r') as log_file:
            log_text.delete(1.0, tk.END)
            log_text.insert(tk.END, log_file.read())

# 示例数据
example_data = ["数据行1", "数据行2", "数据行3"]
# 示例文件路径
example_file_path = "output.txt"

# 调用函数写入数据
write_data_to_file(example_data, example_file_path)

# 启动主循环
root.mainloop()