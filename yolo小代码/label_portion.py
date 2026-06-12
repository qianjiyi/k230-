import os
import shutil
import random
import glob
import yaml

# ================= 配置区域 =================
# [1] 源数据目录：包含图片和对应的 .txt 标注文件
SOURCE_DIR = r"C:\Users\lenovo\Desktop\yolo\data"

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

def check_data_integrity(folder_path):
    """
    检查图片和标签是否一一对应。
    返回: (is_valid, missing_list, valid_pairs)
    """
    if not os.path.exists(folder_path):
        print(f"错误: 找不到路径 '{folder_path}'")
        print("请检查代码开头的 SOURCE_DIR 变量是否填写正确。")
        return False, [], []

    if not os.path.isdir(folder_path):
        print(f"错误: '{folder_path}' 不是一个有效的文件夹路径。")
        return False, [], []

    missing_txt_list = []
    valid_pairs = []
    processed_files = set()

    print(f"正在扫描目录: {folder_path}")

    # 收集所有图片文件
    all_images = []
    for ext in IMG_EXTS:
        files = glob.glob(os.path.join(folder_path, ext))
        files += glob.glob(os.path.join(folder_path, ext.upper()))
        all_images.extend(files)

    found_images_count = 0
    
    for image_path in all_images:
        filename = os.path.basename(image_path)
        
        # 去重逻辑
        if filename in processed_files:
            continue
        processed_files.add(filename)
        
        found_images_count += 1
        base_name = os.path.splitext(filename)[0]
        txt_path = os.path.join(folder_path, f"{base_name}.txt")
        
        if os.path.exists(txt_path):
            valid_pairs.append((filename, f"{base_name}.txt"))
        else:
            missing_txt_list.append(filename)

    # 输出检查结果
    if missing_txt_list:
        print(f"\n[警告] 发现 {len(missing_txt_list)} 张图片缺少对应的 .txt 文件：\n")
        for img_name in missing_txt_list:
            print(img_name)
        print("\n程序已终止，未执行数据集划分。")
        return False, missing_txt_list, []
    else:
        if found_images_count == 0:
            print("未在该文件夹中找到任何图片文件。")
            return False, [], []
        else:
            print(f"[成功] 已检查 {found_images_count} 张图片，所有图片均找到对应的 .txt 文件。")
            return True, [], valid_pairs

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def split_dataset(valid_pairs):
    """执行数据集划分和文件复制"""
    
    random.seed(SEED)
    random.shuffle(valid_pairs)
    
    total = len(valid_pairs)
    ratio_sum = TRAIN_RATIO + VAL_RATIO + TEST_RATIO
    
    if ratio_sum <= 0:
        print("错误: 划分比例之和必须大于0")
        return

    n_train = int(total * (TRAIN_RATIO / ratio_sum))
    n_val = int(total * (VAL_RATIO / ratio_sum))
    n_test = total - n_train - n_val

    sets = {
        'train': {'img': os.path.join(OUTPUT_DIR, 'train', 'images'), 'lab': os.path.join(OUTPUT_DIR, 'train', 'labels')},
        'val':   {'img': os.path.join(OUTPUT_DIR, 'val', 'images'),   'lab': os.path.join(OUTPUT_DIR, 'val', 'labels')},
        'test':  {'img': os.path.join(OUTPUT_DIR, 'test', 'images'),  'lab': os.path.join(OUTPUT_DIR, 'test', 'labels')}
    }

    for s in sets.values():
        ensure_dir(s['img'])
        ensure_dir(s['lab'])

    print(f"\n开始划分数据集...")
    print(f"训练集: {n_train} 张")
    print(f"验证集: {n_val} 张")
    print(f"测试集: {n_test} 张")

    def copy_item(item, set_name):
        img_name, lab_name = item
        src_img = os.path.join(SOURCE_DIR, img_name)
        src_lab = os.path.join(SOURCE_DIR, lab_name)
        
        dst_img = os.path.join(sets[set_name]['img'], img_name)
        dst_lab = os.path.join(sets[set_name]['lab'], lab_name)
        
        shutil.copy2(src_img, dst_img)
        if os.path.exists(src_lab):
            shutil.copy2(src_lab, dst_lab)

    idx = 0
    for _ in range(n_train):
        copy_item(valid_pairs[idx], 'train')
        idx += 1
    for _ in range(n_val):
        copy_item(valid_pairs[idx], 'val')
        idx += 1
    for _ in range(n_test):
        copy_item(valid_pairs[idx], 'test')
        idx += 1

    # 生成 classes.txt 和 dataset.yaml
    classes_file = os.path.join(SOURCE_DIR, 'classes.txt')
    class_names = []
    
    if os.path.exists(classes_file):
        with open(classes_file, 'r', encoding='utf-8') as f:
            class_names = [line.strip() for line in f if line.strip()]
    else:
        pass 

    yaml_path = os.path.join(OUTPUT_DIR, 'dataset.yaml')
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(f"train: ./train/images\n")
        f.write(f"val: ./val/images\n")
        f.write(f"test: ./test/images\n\n")
        f.write(f"nc: {len(class_names)}\n")
        f.write(f"names:\n")
        names_to_write = class_names if class_names else ["class0"] 
        for name in names_to_write:
            f.write(f"  - {name}\n")

    print(f"\n[成功] 数据集划分完成。")
    print(f"输出目录: {OUTPUT_DIR}")

if __name__ == "__main__":
    # 1. 先检查数据完整性
    is_valid, missing, valid_pairs = check_data_integrity(SOURCE_DIR)
    # 2. 只有当检查通过且有数据时，才执行划分
    if is_valid and valid_pairs:
        split_dataset(valid_pairs)
    #释放内存
    del is_valid, missing, valid_pairs