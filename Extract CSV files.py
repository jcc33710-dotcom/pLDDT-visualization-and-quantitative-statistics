import os
import csv

# =========================
# 1. 修改为你的母目录路径
# =========================
base_dir = r""

# =========================
# 2. 输出 CSV 文件名
# =========================
output_csv = ""

# =========================
# 3. 固定链信息
# =========================
chain_peptide = "A"
chain_receptor1 = "B"
chain_receptor2 = "C"

rows = []

# =========================
# 4. 遍历子目录
# =========================
for subdir in os.listdir(base_dir):
    subdir_path = os.path.join(base_dir, subdir)

    if not os.path.isdir(subdir_path):
        continue

    # system 名称规则：子目录名 _ → -
    system_name = subdir.replace("_", "-")

    # 查找 model_0.cif
    for file in os.listdir(subdir_path):
        if file.endswith("model_0.cif"):
            rows.append([
                file,
                system_name,
                chain_peptide,
                chain_receptor1,
                chain_receptor2
            ])

# =========================
# 5. 写入 CSV
# =========================
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "model_id",
        "system",
        "chain_peptide",
        "chain_receptor1",
        "chain_receptor2"
    ])
    writer.writerows(rows)

print(f"完成！共写入 {len(rows)} 条记录 -> {output_csv}")