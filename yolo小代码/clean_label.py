import os
import glob

# ====== 用户只需修改此处变量 ======
TARGET_DIR =  r"C:\Users\lenovo\Desktop\yolo\data" # ← 直接在此处修改为您的绝对路径
# 示例：
#   Windows: r"D:\Photos"
#   macOS/Linux: "/Users/name/Pictures"
# =================================

def remove_orphaned_txt(target_dir):
    # 验证目录是否存在
    if not os.path.isdir(target_dir):
        print(f"错误：目录不存在 - {target_dir}")
        return
    
    # 获取目标目录下所有文件
    all_files = os.listdir(target_dir)
    
    # 提取所有图片文件的【基础名】(不含扩展名)
    image_extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp')
    image_bases = set()
    
    for ext in image_extensions:
        # 在目标目录下搜索图片
        for img_path in glob.glob(os.path.join(target_dir, ext)):
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            image_bases.add(base_name)
    
    # 遍历目标目录下所有 .txt 文件
    txt_count = 0
    deleted_count = 0
    
    for txt_file in glob.glob(os.path.join(target_dir, "*.txt")):
        base_name = os.path.splitext(os.path.basename(txt_file))[0]
        txt_count += 1
        
        if base_name not in image_bases:  # 无对应图片
            try:
                os.remove(txt_file)
                print(f"已删除: {os.path.basename(txt_file)}")
                deleted_count += 1
            except Exception as e:
                print(f"删除失败 {os.path.basename(txt_file)}: {str(e)}")
    
    print(f"\n处理完成 | 总txt: {txt_count} | 删除: {deleted_count} | 保留: {txt_count - deleted_count}")

if __name__ == "__main__":
    # 规范化路径格式（自动处理斜杠问题）
    clean_path = os.path.abspath(TARGET_DIR)
    print(f"正在处理目录: {clean_path}\n")
    remove_orphaned_txt(clean_path)