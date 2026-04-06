import os
import re
import subprocess
from pathlib import Path
from tqdm import tqdm  # 进度条
import shutil  # 用于清理临时文件夹


# -------------------------------
# SRT -> LRC 转换函数
# -------------------------------
def srt_to_lrc(srt_path, lrc_path):
    """
    简单将 SRT 转成 LRC 格式
    """
    try:
        with open(srt_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
        if not content.strip():
            return False  # 空文件
    except Exception:
        return False  # 异常文件

    lrc_lines = []
    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 3:
            time_line = lines[1]
            text_lines = lines[2:]
            match = re.match(r"(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> .*", time_line)
            if match:
                h, m, s, ms = match.groups()
                total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
                lrc_time = f"[{int(total_seconds // 60):02d}:{total_seconds % 60:05.2f}]"
                text = " ".join(text_lines)
                lrc_lines.append(f"{lrc_time}{text}")

    if lrc_lines:
        with open(lrc_path, "w", encoding="utf-8") as f:
            for line in lrc_lines:
                f.write(line + "\n")
        return True
    return False


# -------------------------------
# 主流程
# -------------------------------
def main(overwrite=False):
    folder_on_phone = "/sdcard/Download"  # 手机上 SRT 根目录
    
    local_temp = Path("./srt_temp")  # 本地临时目录
    # 清理本地临时目录
    if local_temp.exists():
        shutil.rmtree(local_temp)
    local_temp.mkdir(exist_ok=True)

    # 扫描手机 SRT 文件
    try:
        output = subprocess.check_output(f'adb shell find {folder_on_phone} -type f -name "*.srt"', shell=True)
        srt_files = output.decode().splitlines()
    except subprocess.CalledProcessError:
        print("手机目录错误或手机未连接！")
        return

    print(f"找到 {len(srt_files)} 个 SRT 文件")

    for remote_path in tqdm(srt_files, desc="处理文件"):
        file_name = os.path.basename(remote_path)
        local_srt = local_temp / file_name
        local_lrc = local_temp / (local_srt.stem + ".lrc")
        remote_lrc_path = remote_path.rsplit(".", 1)[0] + ".lrc"

        # 检查手机是否已存在 LRC
        if not overwrite:
            check = subprocess.run(f'adb shell ls "{remote_lrc_path}"', shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if check.returncode == 0:
                print(f"跳过已存在 LRC: {remote_lrc_path}")
                continue

        # 拉取 SRT
        subprocess.run(f'adb pull "{remote_path}" "{local_srt}"', shell=True, stdout=subprocess.DEVNULL)

        # 跳过空文件或异常文件
        success = srt_to_lrc(str(local_srt), str(local_lrc))
        if not success:
            print(f"跳过空或异常文件: {remote_path}")
            continue

        # 创建手机目录
        remote_dir = os.path.dirname(remote_lrc_path)
        subprocess.run(f'adb shell mkdir -p "{remote_dir}"', shell=True, stdout=subprocess.DEVNULL)

        # 推回手机
        subprocess.run(f'adb push "{local_lrc}" "{remote_lrc_path}"', shell=True, stdout=subprocess.DEVNULL)

    # 清理临时目录
    shutil.rmtree(local_temp)
    print("全部处理完成 ✅")


if __name__ == "__main__":
    # 默认不覆盖已有 LRC，设置 overwrite=True 可覆盖
    main(overwrite=False)
