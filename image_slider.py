import cv2
import os

# 图片路径列表
image_folder = 'source'
image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

# 检查图片是否存在
for path in image_paths:
    if not os.path.exists(path):
        raise FileNotFoundError(f"图片 {path} 不存在")

# 初始化变量
current_image_index = 0
is_playing = True

# 鼠标回调函数
def mouse_callback(event, x, y, flags, param):
    global is_playing
    if event == cv2.EVENT_LBUTTONDOWN:
        is_playing = not is_playing

# 创建窗口并设置鼠标回调
cv2.namedWindow('Image Slider')
cv2.setMouseCallback('Image Slider', mouse_callback)

while True:
    # 读取当前图片
    image = cv2.imread(image_paths[current_image_index])
    
    # 显示图片
    cv2.imshow('Image Slider', image)
    
    # 如果正在播放，切换到下一张图片
    if is_playing:
        current_image_index = (current_image_index + 1) % len(image_paths)
    
    # 按下 'q' 键退出
    if cv2.waitKey(1000) & 0xFF == ord('q'):
        break

# 关闭窗口
cv2.destroyAllWindows()