import os
import subprocess
from datetime import datetime

# 锁定你的 Obsidian 根目录，防止跨目录修改
VAULT_PATH = os.path.expanduser("~/obsidian-vault")

def manage_obsidian_knowledge(action: str, target_file: str, content: str = "", commit_msg: str = "") -> str:
    """
    OpenClaw 工具函数：安全处理 Obsidian 文件的读、写与 Git 同步。
    
    :param action: 执行动作 ('read' 读取, 'append' 追加, 'overwrite' 覆写)
    :param target_file: 相对路径，例如 "20-Areas/考研记录.md" 或 "00-Inbox/2026-06-18.md"
    :param content: 准备写入或覆写的 Markdown 内容（读取时留空）
    :param commit_msg: Git 提交摘要（5个字左右极简概括）
    :return: 执行状态的文本反馈，直接返回给大模型
    """
    
    # 1. 基础安全防御：拦截非法路径跳跃 (防 ../ 攻击)
    if ".." in target_file or target_file.startswith("/"):
        return "❌ 拒绝执行：检测到非法的目录跨越尝试。"

    full_path = os.path.join(VAULT_PATH, target_file)
    
    # 自动创建缺失的父级目录（支持自动拓荒逻辑）
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # 2. 执行读取：为动态合并（考研计划/进度）提供上下文
    if action == "read":
        if not os.path.exists(full_path):
            return "提示：目标文件当前不存在，可视为全新内容。"
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"❌ 读取失败: {str(e)}"

    # 3. 执行写入：追加 (Append) 或 覆写 (Overwrite)
    try:
        if action == "append":
            # 如果文件已存在且有内容，追加时自动加两个换行符保证 Markdown 排版
            prefix = "\n\n" if os.path.exists(full_path) and os.path.getsize(full_path) > 0 else ""
            with open(full_path, "a", encoding="utf-8") as f:
                f.write(prefix + content)
        elif action == "overwrite":
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            return f"❌ 错误：未知的 action 指令 '{action}'。"
    except Exception as e:
        return f"❌ 写入失败，请检查文件权限: {str(e)}"

    # 4. 执行 Git 自动化工作流 (静默执行)
    if not commit_msg:
        commit_msg = f"更新 {os.path.basename(target_file)}"
        
    try:
        # 检查是否初始化了 Git
        if not os.path.exists(os.path.join(VAULT_PATH, ".git")):
            return f"✅ 文件 [{target_file}] 已更新，但该目录未配置 Git，跳过推送。"

        # 依次执行 Git 流水线，捕获输出以便报错时诊断
        subprocess.run(["git", "add", "."], cwd=VAULT_PATH, check=True, capture_output=True)
        
        # 如果没有内容变更（例如只触发了格式化），直接返回
        status_check = subprocess.run(["git", "status", "--porcelain"], cwd=VAULT_PATH, capture_output=True, text=True)
        if not status_check.stdout.strip():
            return f"✅ 文件 [{target_file}] 写入成功，但无实质变更需 Commit。"

        subprocess.run(["git", "commit", "-m", f"[{action}] {commit_msg}"], cwd=VAULT_PATH, check=True, capture_output=True)
        subprocess.run(["git", "push"], cwd=VAULT_PATH, check=True, capture_output=True)
        
        return f"✅ 成功{'追加' if action == 'append' else '覆写'}并 Push 至仓库。文件: {target_file}"
        
    except subprocess.CalledProcessError as e:
        # 提取核心报错信息
        err_detail = e.stderr.decode('utf-8').strip() if e.stderr else str(e)
        return f"⚠️ 文件已成功写入本地，但 Git 同步失败，请手动处理冲突。报错片段: {err_detail[:100]}..."


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="管理 Obsidian 知识库")
    parser.add_argument("--action", required=True, choices=["read", "append", "overwrite"], help="操作类型")
    parser.add_argument("--target_file", required=True, help="文件相对路径")
    parser.add_argument("--content", default="", help="写入内容")
    parser.add_argument("--commit_msg", default="", help="Git 提交摘要")
    args = parser.parse_args()
    result = manage_obsidian_knowledge(args.action, args.target_file, args.content, args.commit_msg)
    print(result)