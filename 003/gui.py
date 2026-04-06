import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import threading

from core import scan_files, process_files

DEFAULT_PHONE_PATH = "/sdcard/Movies"
DEFAULT_LOCAL_PATH = "D:/"

cached_files = []


def log(msg, end="\n\n"):
    text_log.insert(tk.END, msg + end)
    text_log.see(tk.END)


def update_progress(current, total):
    percent = int(current / total * 100)
    progress_bar["value"] = percent
    label_progress.config(text=f"{percent}% ({current}/{total})")
    root.update_idletasks()


def choose_folder():
    if var_source.get() == "local":
        folder = filedialog.askdirectory()
        if folder:
            entry_path.delete(0, tk.END)
            entry_path.insert(0, folder)
    else:
        messagebox.showinfo("提示", "手机模式无需选择文件夹")


def on_source_change():
    if var_source.get() == "phone":
        entry_path.delete(0, tk.END)
        entry_path.insert(0, DEFAULT_PHONE_PATH)
    else:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, DEFAULT_LOCAL_PATH)


def scan():
    folder = entry_path.get().strip()
    overwrite = var_overwrite.get()
    source_type = var_source.get()

    if not folder:
        messagebox.showwarning("提示", "请输入路径")
        return

    def task():
        try:
            log("🔍 开始扫描...")
            srt_files, exists, need = scan_files(folder, overwrite, source_type)

            global cached_files
            cached_files = srt_files

            log(f"📂 总 SRT: {len(srt_files)}")
            log(f"⏭ 已存在 LRC: {exists}")
            log(f"🆕 待处理: {need}")
            log("=====================================================================")

            messagebox.showinfo("扫描完成", "请点击开始处理")

        except Exception as e:
            messagebox.showerror("错误", str(e))

    threading.Thread(target=task).start()


def start():
    overwrite = var_overwrite.get()
    source_type = var_source.get()

    if not cached_files:
        messagebox.showwarning("提示", "请先扫描")
        return

    progress_bar["value"] = 0
    label_progress.config(text="0%")

    def task():
        process_files(
            cached_files,
            overwrite=overwrite,
            log=log,
            progress=update_progress,
            source_type=source_type
        )

    threading.Thread(target=task).start()


# GUI
root = tk.Tk()
root.title("SRT → LRC 工具（增强版）")
root.geometry("1000x800")

tk.Label(root, text="源类型").pack()

var_source = tk.StringVar(value="phone")
frame_source = tk.Frame(root)
frame_source.pack()

tk.Radiobutton(frame_source, text="手机", variable=var_source, value="phone", command=on_source_change).pack(
    side=tk.LEFT)
tk.Radiobutton(frame_source, text="电脑", variable=var_source, value="local", command=on_source_change).pack(
    side=tk.LEFT)

tk.Label(root, text="路径").pack()
entry_path = tk.Entry(root, width=60)
entry_path.pack()
entry_path.insert(0, DEFAULT_PHONE_PATH)

tk.Button(root, text="选择文件夹", command=choose_folder).pack()

var_overwrite = tk.BooleanVar()
tk.Checkbutton(root, text="覆盖已有", variable=var_overwrite).pack()

frame_btn = tk.Frame(root)
frame_btn.pack(pady=5)

tk.Button(frame_btn, text="扫描", command=scan).pack(side=tk.LEFT, padx=5)
tk.Button(frame_btn, text="开始处理", command=start).pack(side=tk.LEFT, padx=5)

# 进度条
progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
progress_bar.pack(pady=10)

label_progress = tk.Label(root, text="0%")
label_progress.pack()

# 日志
text_log = tk.Text(root, height=20)
text_log.pack(fill=tk.BOTH, expand=True)

root.mainloop()
