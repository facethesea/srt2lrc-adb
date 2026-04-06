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


def scan_files(folder, overwrite=False, source_type="phone"):
    if source_type == "phone":
        output = subprocess.check_output(
            f'adb shell find {folder} -type f -name "*.srt"',
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

    else:
        folder_path = Path(folder)
        srt_files = list(folder_path.rglob("*.srt"))

        exists = 0
        need = 0

        for path in srt_files:
            lrc_path = path.with_suffix(".lrc")
            if lrc_path.exists():
                exists += 1
            else:
                need += 1

        return srt_files, exists, need


def process_files(srt_files, overwrite=False, log=print, progress=None, source_type="phone"):
    total = len(srt_files)

    if source_type == "phone":
        local_temp = Path("./srt_temp")

        if local_temp.exists():
            shutil.rmtree(local_temp)
        local_temp.mkdir()

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
                    if progress:
                        progress(i, total)
                    continue

            subprocess.run(f'adb pull "{remote_path}" "{local_srt}"', shell=True)

            if not srt_to_lrc(local_srt, local_lrc):
                log(f"⚠ 异常文件: {remote_path}")
                if progress:
                    progress(i, total)
                continue

            subprocess.run(f'adb push "{local_lrc}" "{remote_lrc}"', shell=True)

            if progress:
                progress(i, total)

        shutil.rmtree(local_temp)

    else:
        for i, srt_path in enumerate(srt_files, 1):
            log(f"[{i}/{total}] 处理: {srt_path}")

            srt_path = Path(srt_path)
            lrc_path = srt_path.with_suffix(".lrc")

            if lrc_path.exists() and not overwrite:
                log(f"⏭ 跳过: {lrc_path}")
                if progress:
                    progress(i, total)
                continue

            if not srt_to_lrc(srt_path, lrc_path):
                log(f"⚠ 异常文件: {srt_path}")
                if progress:
                    progress(i, total)
                continue

            log(f"✅ 生成: {lrc_path}")

            if progress:
                progress(i, total)

    log("✅ 全部处理完成")
    log("=====================================================================")
