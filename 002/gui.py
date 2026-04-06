import tkinter as tk
from tkinter import messagebox
import threading

from core import scan_files, process_files


def log(msg, end="\n\n"):
    """
    msg: 要输出的消息
    end: 每条日志结尾符（默认两个换行）
    """
    text_log.insert(tk.END, msg + end)
    text_log.see(tk.END)


def scan():
    folder = entry_path.get().strip()
    overwrite = var_overwrite.get()

    if not folder:
        messagebox.showwarning("提示", "请输入路径")
        return

    def task():
        try:
            log("🔍 开始扫描...")
            srt_files, exists, need = scan_files(folder, overwrite)

            global cached_files
            cached_files = srt_files

            log(f"📂 总 SRT: {len(srt_files)}")
            log(f"⏭ 已存在 LRC: {exists}")
            log(f"🆕 待处理: {need}")
            log("=====================================================================")  # 分隔符

            messagebox.showinfo("扫描完成", "请查看日志后点击【开始处理】")

        except Exception as e:
            messagebox.showerror("错误", str(e))

    threading.Thread(target=task).start()


def start():
    overwrite = var_overwrite.get()

    if not cached_files:
        messagebox.showwarning("提示", "请先扫描")
        return

    def task():
        process_files(cached_files, overwrite=overwrite, log=log)

    threading.Thread(target=task).start()


# ---------------- GUI ----------------
root = tk.Tk()
root.title("SRT → LRC 工具")
root.geometry("1000x800")

cached_files = []

# 路径输入
tk.Label(root, text="手机路径").pack()
entry_path = tk.Entry(root, width=50)
entry_path.pack()
entry_path.insert(0, "/sdcard/Movies")

# 选项
var_overwrite = tk.BooleanVar()
tk.Checkbutton(root, text="覆盖已有", variable=var_overwrite).pack()

# 按钮
frame_btn = tk.Frame(root)
frame_btn.pack(pady=5)

tk.Button(frame_btn, text="扫描", command=scan).pack(side=tk.LEFT, padx=5)
tk.Button(frame_btn, text="开始处理", command=start).pack(side=tk.LEFT, padx=5)

# 日志窗口
text_log = tk.Text(root, height=15)
text_log.pack(fill=tk.BOTH, expand=True)

root.mainloop()
