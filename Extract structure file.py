import os
import shutil

# =========================
# 1. 母目录（包含多个子目录）
# =========================
source_base_dir = r""

# =========================
# 2. 目标目录（统一存放 model_0.cif）
# =========================
target_dir = r""

# 如果目标目录不存在，则创建
os.makedirs(target_dir, exist_ok=True)

copied_count = 0

# =========================
# 3. 遍历子目录并复制文件
# =========================
for subdir in os.listdir(source_base_dir):
    subdir_path = os.path.join(source_base_dir, subdir)

    if not os.path.isdir(subdir_path):
        continue

    for file in os.listdir(subdir_path):
        if file.endswith("model_0.cif"):
            src_file = os.path.join(subdir_path, file)

            # 【已修改】直接使用原文件名，不再添加子目录前缀
            # 注意：如果不同子目录中有同名文件，后者会覆盖前者
            dst_file = os.path.join(target_dir, file)

            shutil.copy2(src_file, dst_file)
            copied_count += 1

print(f"完成！共复制 {copied_count} 个 model_0.cif 文件")