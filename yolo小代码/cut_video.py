import os
from moviepy import VideoFileClip

# ================= 用户配置区域 (请在此处修改) =================
# 输入视频文件路径
INPUT_VIDEO = r"C:\Users\lenovo\Desktop\yolo\video\2.mp4"

# 输出文件夹路径
OUTPUT_DIR = r"C:\Users\lenovo\Desktop\yolo\video"

# 切割时间点 (秒)
# 例如：10.5 表示在第 10.5 秒处切割
# 第一部分：0 秒 -> t 秒
# 第二部分：t 秒 -> 视频结束
CUT_TIME_SECONDS = 3
# ===============================================================

def split_video_at_time(input_path, output_folder, cut_time):
    if not os.path.exists(input_path):
        print(f"错误: 找不到文件 '{input_path}'")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"已创建输出文件夹: {output_folder}")

    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)

    output_path_1 = os.path.join(output_folder, f"{name}_part1{ext}")
    output_path_2 = os.path.join(output_folder, f"{name}_part2{ext}")

    print(f"正在加载视频: {input_path} ...")
    
    try:
        # 先加载视频仅为了获取时长和帧率，随后立即关闭，避免占用进程
        video_meta = VideoFileClip(input_path)
        duration = video_meta.duration
        fps = video_meta.fps
        video_meta.close()
        
        print(f"视频总时长: {duration:.2f} 秒")
        print(f"将在第 {cut_time} 秒处切割...")

        if cut_time <= 0 or cut_time >= duration:
            print(f"错误: 切割时间 ({cut_time}) 必须在 0 到 {duration:.2f} 之间。")
            return

        # --- 切割第一部分 (0 到 cut_time) ---
        print("正在生成第一部分视频...")
        
        # 独立加载视频对象用于第一部分
        video_p1 = VideoFileClip(input_path)
        clip1 = video_p1[0:cut_time]
        
        clip1.write_videofile(
            output_path_1, 
            codec='libx264', 
            audio_codec='aac',
            temp_audiofile='temp_audio_part1.m4a', 
            remove_temp=True,
            preset='medium',
            logger=None
        )
        clip1.close()
        video_p1.close()
        print(f"第一部分已保存: {output_path_1}")

        # --- 切割第二部分 (cut_time 到 结束) ---
        print("正在生成第二部分视频...")
        
        # 重新加载一个全新的视频对象用于第二部分
        # 避免复用之前可能已经状态异常的 video 对象，防止 'Proc not detected'
        video_p2 = VideoFileClip(input_path)
        clip2 = video_p2[cut_time:duration]
        
        clip2.write_videofile(
            output_path_2, 
            codec='libx264', 
            audio_codec='aac',
            temp_audiofile='temp_audio_part2.m4a', 
            remove_temp=True,
            preset='medium',
            logger=None,
            fps=fps
        )
        clip2.close()
        video_p2.close()
        print(f"第二部分已保存: {output_path_2}")

        print("视频切割成功！")

    except Exception as e:
        print(f"\n[错误] 发生异常: {e}")
        # 确保出错时释放资源
        try:
            for obj_name in ['video_meta', 'video_p1', 'video_p2', 'clip1', 'clip2']:
                if obj_name in locals():
                    obj = locals()[obj_name]
                    if obj is not None:
                        obj.close()
        except:
            pass

if __name__ == "__main__":
    split_video_at_time(INPUT_VIDEO, OUTPUT_DIR, CUT_TIME_SECONDS)