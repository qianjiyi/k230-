import os
import shutil
import random
import glob

# ================= 配置区域 =================
# [1] 源数据目录：包含图片文件
SOURCE_DIR = r"C:\Users\lenovo\Desktop\yolo\output_images"

# [2] 输出根目录：划分后的数据将存放于此
OUTPUT_DIR = r"C:\Users\lenovo\Desktop\yolo\data_split_output"

# [3] 划分比例
TRAIN_RATIO = 0.7
VAL_RATIO = 0.2
TEST_RATIO = 0.1

# [4] 随机种子
SEED = 42

# [5] 支持的图片格式
IMG_EXTS = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.webp', '*.tiff']
# ===========================================

def ensure_dir(path):
    """创建目录（如果不存在）"""
    os.makedirs(path, exist_ok=True)

def split_dataset():
    """
    执行数据集划分：
    1. 扫描源目录所有图片
    2. 随机打乱并按比例分配
    3. 仅复制图片到 train/val/test/images 文件夹
    """
    
    # 1. 收集所有图片文件
    all_images = []
    for ext in IMG_EXTS:
        # 处理大小写
        files = glob.glob(os.path.join(SOURCE_DIR, ext))
        files += glob.glob(os.path.join(SOURCE_DIR, ext.upper()))
        all_images.extend(files)
    
    # 提取文件名列表
    image_files = [os.path.basename(img_path) for img_path in all_images]
    
    if not image_files:
        print(f"错误: 在 '{SOURCE_DIR}' 中未找到任何图片文件。")
        return

    print(f"正在扫描目录: {SOURCE_DIR}")
    print(f"[成功] 已找到 {len(image_files)} 张图片，开始划分...")

    # 2. 随机打乱并计算数量
    random.seed(SEED)
    random.shuffle(image_files)

    total = len(image_files)
    ratio_sum = TRAIN_RATIO + VAL_RATIO + TEST_RATIO
    if ratio_sum <= 0:
        print("错误: 划分比例之和必须大于0")
        return

    n_train = int(total * (TRAIN_RATIO / ratio_sum))
    n_val = int(total * (VAL_RATIO / ratio_sum))
    n_test = total - n_train - n_val

    # 3. 定义目标路径 (仅保留 images 路径)
    sets = { 
        'train': os.path.join(OUTPUT_DIR, 'train', 'images'),
        'val':   os.path.join(OUTPUT_DIR, 'val', 'images'),
        'test':  os.path.join(OUTPUT_DIR, 'test', 'images')
    }

    # 创建文件夹
    for target_path in sets.values():
        ensure_dir(target_path)

    print(f"\n开始划分数据集...")
    print(f"训练集: {n_train} 张")
    print(f"验证集: {n_val} 张")
    print(f"测试集: {n_test} 张")

    # 4. 复制文件
    idx = 0
    
    # 复制训练集
    for _ in range(n_train):
        src_img = os.path.join(SOURCE_DIR, image_files[idx])
        dst_img = os.path.join(sets['train'], image_files[idx])
        shutil.copy2(src_img, dst_img)
        idx += 1
    
    # 复制验证集
    for _ in range(n_val):
        src_img = os.path.join(SOURCE_DIR, image_files[idx])
        dst_img = os.path.join(sets['val'], image_files[idx])
        shutil.copy2(src_img, dst_img)
        idx += 1
    
    # 复制测试集
    for _ in range(n_test):
        src_img = os.path.join(SOURCE_DIR, image_files[idx])
        dst_img = os.path.join(sets['test'], image_files[idx])
        shutil.copy2(src_img, dst_img)
        idx += 1

    print(f"\n[成功] 数据集划分完成（仅包含图片）。")
    print(f"输出目录: {OUTPUT_DIR}")

if __name__ == "__main__":
    split_dataset()