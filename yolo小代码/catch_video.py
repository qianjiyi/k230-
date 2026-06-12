import cv2
import os

# ================= 配置区域 (请在此处修改) =================

# 1. 视频文件的路径 (支持 .mp4, .avi, .mov 等格式)
# 例如: r"C:\Users\Name\Videos\test.mp4" 或 "./video.mp4"
VIDEO_PATH = r"C:\Users\lenovo\Desktop\yolo\video\(3).mp4"

# 2. 输出图片的文件夹路径
# 如果文件夹不存在，代码会自动创建
# 例如: r"C:\Users\Name\Pictures\screenshots" 或 "./output_images"
OUTPUT_FOLDER = r"C:\Users\lenovo\Desktop\yolo\output_images"

# 3. 截取模式设置
# 模式选择: "time" (按时间秒数) 或 "frame" (按帧数间隔)
MODE = "frame" 

# 4. 间隔数值
# 如果 MODE="time", 值为秒数 (例如: 1 表示每1秒截一张)
# 如果 MODE="frame", 值为帧数 (例如: 30 表示每30帧截一张)
INTERVAL_VALUE = 3

haven = 90
# =========================================================

def main():
    # 检查配置是否填写
    if not VIDEO_PATH:
        return
    if not OUTPUT_FOLDER:
        return

    # 创建输出文件夹
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"已创建输出文件夹: {OUTPUT_FOLDER}")

    # 打开视频
    cap = cv2.VideoCapture(VIDEO_PATH)
    
    if not cap.isOpened():
        print(f"错误: 无法打开视频文件，请检查路径是否正确:\n{VIDEO_PATH}")
        return

    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if fps == 0:
        print("错误: 无法获取视频帧率")
        return

    print(f"视频加载成功:")
    print(f"  - 帧率: {fps:.2f} FPS")
    print(f"  - 总帧数: {total_frames}")
    
    # 计算实际跳过的帧数
    if MODE == "time":
        frame_interval = int(fps * INTERVAL_VALUE)
        print(f"模式: 每 {INTERVAL_VALUE} 秒截取 (即每 {frame_interval} 帧)")
    elif MODE == "frame":
        frame_interval = INTERVAL_VALUE
        print(f"模式: 每 {INTERVAL_VALUE} 帧截取")
    else:
        print("错误: MODE 参数必须是 'time' 或 'frame'")
        cap.release()
        return

    if frame_interval < 1:
        frame_interval = 1

    count = 0       # 当前读取到的帧数
    saved_count = 0 # 已保存的图片数

    print("开始处理...")

    while True:
        ret, frame = cap.read()
        
        if not ret:
            # 视频读取结束
            break
        
        # 判断是否到达截取点
        if count % frame_interval == 0:
            filename = os.path.join(OUTPUT_FOLDER, f"({saved_count+haven:d}).jpg")
            cv2.imwrite(filename, frame)
            saved_count += 1
        
        count += 1
        
        # 可选：每保存10张打印一次进度，避免刷屏
        if saved_count % 10 == 0 and saved_count > 0:
            print(f"已处理 {count}/{total_frames} 帧，已保存 {saved_count} 张图片...")

    cap.release()
    
    print("-" * 30)
    print("处理完成!")
    print(f"总共读取: {count} 帧")
    print(f"成功保存: {saved_count} 张图片")
    print(f"保存位置: {os.path.abspath(OUTPUT_FOLDER)}")

if __name__ == "__main__":
    main()