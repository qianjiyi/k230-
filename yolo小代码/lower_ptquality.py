import os
from PIL import Image

# ================= 用户配置区域 (请在此处修改) =================
# 输入文件夹路径 (包含原始图片的文件夹)
# 可以使用相对路径 (如 "./images") 或绝对路径 (如 r"C:\Users\Name\Pics")
INPUT_DIR = r"C:\Users\lenovo\Desktop\yolo\output_images"

# 输出文件夹路径 (处理后的图片将保存到这里)
OUTPUT_DIR = r"C:\Users\lenovo\Desktop\yolo\output_lower"

# 目标最大边长 (像素)
# 脚本会保持宽高比，将图片的长边缩放到此数值。
# 例如设置为 1024，则宽或高中较大的那个会变成 1024，另一边按比例缩小。
TARGET_MAX_SIZE = 1024
# ===============================================================

def resize_images_in_folder(input_folder, output_folder, max_size):
    """
    降低文件夹内所有图片的分辨率。
    """
    
    # 支持的图片扩展名
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff')
    
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print(f"错误: 输入文件夹 '{input_folder}' 不存在。\n请创建该文件夹并放入图片，或修改代码中的 INPUT_DIR 路径。")
        return

    # 创建输出文件夹（如果不存在）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"已创建输出文件夹: {output_folder}")

    # 获取文件列表
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(supported_extensions)]
    
    if not files:
        print(f"未在文件夹 '{input_folder}' 中找到任何支持的图片文件。")
        return

    print(f"找到 {len(files)} 张图片，开始处理 (目标最大边长: {max_size}px)...")

    count = 0
    success_count = 0
    
    for filename in files:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        try:
            with Image.open(input_path) as img:
                # 获取原始尺寸
                original_width, original_height = img.size
                
                # 计算新尺寸 (保持宽高比)
                if original_width > original_height:
                    new_width = max_size
                    new_height = int(original_height * (max_size / original_width))
                else:
                    new_height = max_size
                    new_width = int(original_width * (max_size / original_height))
                
                # 如果图片本身比设定值小，则不放大
                if new_width >= original_width and new_height >= original_height:
                    # 直接复制原图到输出目录，或者跳过，这里选择复制以保持输出目录完整
                    img.save(output_path)
                    print(f"跳过 (无需缩放): {filename} ({original_width}x{original_height})")
                else:
                    # 执行缩放 (LANCZOS 是高质量降采样滤波器)
                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # 处理模式转换 (主要针对 JPEG 不支持透明通道的问题)
                    if filename.lower().endswith(('.jpg', '.jpeg')):
                        if resized_img.mode in ("RGBA", "P"):
                            resized_img = resized_img.convert("RGB")
                        # 保存 JPEG 时优化质量
                        resized_img.save(output_path, "JPEG", quality=85, optimize=True)
                    else:
                        # 其他格式直接保存
                        resized_img.save(output_path, optimize=True)
                    
                    print(f"成功处理: {filename} [{original_width}x{original_height}] -> [{new_width}x{new_height}]")
                
                success_count += 1
                count += 1

        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")

    print(f"\n处理完成！共处理 {success_count} 个文件。结果保存在: {output_folder}")

if __name__ == "__main__":
    resize_images_in_folder(INPUT_DIR, OUTPUT_DIR, TARGET_MAX_SIZE)