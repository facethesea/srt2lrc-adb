import os
import re
import subprocess
from pathlib import Path
import shutil


def srt_to_lrc(srt_path, lrc_path):
    try:
        with open(srt_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
        if not content.strip():
            return False
    except Exception:
        return False

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
            f.write("\n".join(lrc_lines))
        return True
    return False


# ✅ 扫描函数
def scan_files(folder_on_phone, overwrite=False):
    output = subprocess.check_output(
        f'adb shell find {folder_on_phone} -type f -name "*.srt"',
        shell=True
    )
    srt_files = output.decode().splitlines()

    exists = 0
    need = 0

    for path in srt_files:
        lrc_path = path.rsplit(".", 1)[0] + ".lrc"
        check = subprocess.run(
            f'adb shell ls "{lrc_path}"',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if check.returncode == 0:
            exists += 1
        else:
            need += 1

    return srt_files, exists, need


# ✅ 处理函数
def process_files(srt_files, overwrite=False, log=print):
    local_temp = Path("./srt_temp")

    if local_temp.exists():
        shutil.rmtree(local_temp)
    local_temp.mkdir()

    total = len(srt_files)

    for i, remote_path in enumerate(srt_files, 1):
        log(f"[{i}/{total}] 处理: {remote_path}")

        file_name = os.path.basename(remote_path)
        local_srt = local_temp / file_name
        local_lrc = local_temp / (local_srt.stem + ".lrc")
        remote_lrc = remote_path.rsplit(".", 1)[0] + ".lrc"

        if not overwrite:
            check = subprocess.run(
                f'adb shell ls "{remote_lrc}"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if check.returncode == 0:
                log(f"⏭ 跳过: {remote_lrc}")
                continue

        subprocess.run(f'adb pull "{remote_path}" "{local_srt}"', shell=True)

        if not srt_to_lrc(local_srt, local_lrc):
            log(f"⚠ 异常文件: {remote_path}")
            continue

        subprocess.run(f'adb push "{local_lrc}" "{remote_lrc}"', shell=True)

    shutil.rmtree(local_temp)
    log("✅ 全部处理完成")
    log("=====================================================================")  # 分隔符
