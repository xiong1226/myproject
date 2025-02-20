import logging
import pandas as pd

# 配置日志记录
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def write_data_to_file(data, file_path):
    """
    将数据写入指定Excel文件，并记录日志。
    
    :param data: 要写入的数据，可以是DataFrame或列表
    :param file_path: 文件路径
    """
    try:
        if isinstance(data, pd.DataFrame):
            data.to_excel(file_path, index=False)
        elif isinstance(data, list):
            df = pd.DataFrame(data, columns=['Data'])
            df.to_excel(file_path, index=False)
        else:
            raise ValueError("数据类型不支持，必须是DataFrame或列表")
        logging.info(f"数据已成功写入文件: {file_path}")
    except Exception as e:
        logging.error(f"写入文件时发生错误: {e}")

# 示例数据
example_data = ["数据行1", "数据行2", "数据行3"]
# 示例文件路径
example_file_path = "output.xlsx"

# 调用函数写入数据
write_data_to_file(example_data, example_file_path)