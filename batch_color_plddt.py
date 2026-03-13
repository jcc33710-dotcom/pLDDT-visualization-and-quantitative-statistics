#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""批量处理 AlphaFold 模型文件，按 pLDDT 着色并保存为 PNG 图片。此版本支持递归遍历子目录，并仅加载文件名匹配 "*_model_0.cif" 的结构文件。"""

import os  # 导入操作系统接口模块
import sys  # 导入系统特定参数和函数模块
from pathlib import Path  # 从 pathlib 模块导入 Path 类，用于处理文件路径

try:
    import pymol2  # 尝试导入 pymol2 库，用于在 Python 中控制 PyMOL
except ImportError:  # 如果导入失败，执行以下代码
    print("请先安装 PyMOL 的 Python API：pip install pymol")  # 打印错误提示信息
    sys.exit(1)  # 退出程序，返回错误代码 1

# 定义着色函数（从 coloraf.py 简化而来）
def color_plddt(pymol_instance, model_name):  # 定义 color_plddt 函数，接受 PyMOL 实例和模型名称
    """ 根据 pLDDT 分数对模型着色（复现 coloraf.py 的逻辑） """
    cmd = pymol_instance.cmd  # 直接使用 coloraf.py 的着色逻辑
    cmd.color("blue", f"({model_name}) and b > 90")
    cmd.color("cyan", f"({model_name}) and b < 90 and b > 70")
    cmd.color("yellow", f"({model_name}) and b < 70 and b > 50")
    cmd.color("orange", f"({model_name}) and b < 50")

    # 设置显示样式
    cmd.hide("everything", model_name)
    cmd.show("cartoon", model_name)
    cmd.show("sticks", f"het and {model_name}")

def batch_color_plddt(input_dir, output_dir=None):  # 定义批量处理函数，接受输入目录和可选的输出目录
    """ 递归遍历 input_dir 下所有子目录，查找文件名匹配 "*_model_0.cif" 的结构文件并处理 """
    input_path = Path(input_dir)  # 将输入目录路径转换为 Path 对象
    if not input_path.exists():  # 检查输入路径是否存在
        print(f"输入目录不存在: {input_path}")  # 打印路径不存在的错误信息
        return  # 返回，不继续执行

    # 构建输出路径：如果未指定，则使用 input_dir 同级的 'plddt_output' 目录
    if output_dir is None:
        output_path = input_path / "plddt_output"  # 默认输出目录为输入目录下的 plddt_output 文件夹
    else:
        output_path = Path(output_dir)  # 使用用户指定的输出目录
    output_path.mkdir(parents=True, exist_ok=True)  # 创建输出目录（包括父目录），exist_ok=True 表示如果目录已存在不报错

    # 递归查找所有满足 "*_model_0.cif" 的文件
    model_files = list(input_path.rglob("*_model_0.cif"))  # 使用 rglob 递归搜索所有子目录中匹配模式的 .cif 文件
    if not model_files:  # 如果没有找到模型文件
        print(f"在 {input_path} 及其子目录中未找到 '*_model_0.cif' 文件")  # 打印未找到文件的提示信息
        return  # 返回，不继续执行

    print(f"找到 {len(model_files)} 个 '*_model_0.cif' 结构文件")  # 打印找到的模型文件数量

    # 启动 PyMOL 实例
    pymol_instance = pymol2.PyMOL()  # 创建 PyMOL 实例对象
    pymol_instance.start()  # 启动 PyMOL 实例
    cmd = pymol_instance.cmd  # 获取 PyMOL 命令接口

    for model_file in model_files:  # 遍历所有匹配的模型文件
        # 生成唯一模型名：使用相对于输入目录的路径作为基础，替换分隔符避免非法字符
        try:
            rel_path = model_file.relative_to(input_path)  # 获取相对于 input_dir 的路径
            safe_name = str(rel_path).replace(os.sep, "__").replace(".cif", "")  # 将路径分隔符替换为 "__"，移除 .cif 后缀
            model_name = safe_name  # 用作 PyMOL 对象名
        except ValueError:  # fallback：若无法计算相对路径，使用 stem（应不会发生）
            model_name = model_file.stem  # 获取文件名（不含扩展名）作为模型名称

        print(f"正在处理: {model_file}")  # 打印当前正在处理的完整文件路径

        # 加载模型
        cmd.load(str(model_file), model_name)  # 加载模型文件到 PyMOL，使用安全名称作为对象名

        # 应用 pLDDT 着色
        color_plddt(pymol_instance, model_name)  # 调用着色函数对模型进行 pLDDT 着色

        # 调整视角（可选）
        cmd.zoom(model_name)  # 调整视角以完全显示模型

        # 构造输出文件名（保留原始目录结构的扁平化表示）
        output_png = output_path / f"{model_name}_plddt.png"  # 构造输出 PNG 文件的完整路径
        output_pdb = output_path / f"{model_name}_plddt.pdb"  # 构造输出 PDB 文件的完整路径（原为 .pse，现改为 .pdb）

        # 保存为 PNG 图片
        cmd.png(str(output_png), width=1200, height=800, dpi=300)  # 将当前视图保存为 PNG 图片，设置宽度、高度和分辨率
        print(f"已保存图片: {output_png}")  # 打印保存成功的提示信息

        # 保存着色后的模型数据（改为保存为 PDB 文件）
        cmd.save(str(output_pdb), model_name)  # 保存当前模型为 PDB 文件（保留原子坐标和 B-factor/pLDDT 值）
        print(f"已保存 PDB: {output_pdb}")  # 打印 PDB 文件保存成功的提示信息

        # 清理当前模型（释放内存）
        cmd.delete(model_name)  # 删除当前模型以释放内存

    pymol_instance.stop()  # 停止 PyMOL 实例
    print("批量处理完成！")  # 打印批量处理完成的提示信息

if __name__ == "__main__":  # 如果脚本直接运行（而不是被导入）
    import argparse  # 导入 argparse 模块用于解析命令行参数

    parser = argparse.ArgumentParser(description="批量处理 AlphaFold 模型并按 pLDDT 着色（仅处理 *_model_0.cif 文件）")  # 创建参数解析器对象
    parser.add_argument("input_dir", help="包含子目录的根目录，用于递归查找 *_model_0.cif 文件")  # 添加必需的输入目录参数
    parser.add_argument("--output_dir", "-o", help="输出图片和会话文件的目录（默认为 <input_dir>/plddt_output）")  # 添加可选的输出目录参数

    args = parser.parse_args()  # 解析命令行参数
    batch_color_plddt(args.input_dir, args.output_dir)  # 调用批量处理函数，传入解析后的参数


