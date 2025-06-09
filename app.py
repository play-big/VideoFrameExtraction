import subprocess
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class VideoFrameExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("视频抽帧工具 - Mac 版")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._init_ui_components()
        self._center_window(600, 400)

    def _init_ui_components(self):
        self.style.configure('Red.TButton', foreground='red')
        # 状态显示区域
        self.status_text = tk.Text(self.root, height=8, width=70, state="disabled")
        self.status_text.grid(row=3, column=0, columnspan=3, padx=10, pady=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3, pady=15)
        self._create_widgets()

    def _center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self):
        self.video_path_var = tk.StringVar()
        ttk.Label(self.root, text="视频路径:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.video_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="选择视频", command=self.choose_video).grid(row=0, column=2, padx=5, pady=5)

        self.interval_var = tk.StringVar(value="10")
        ttk.Label(self.root, text="抽帧间隔（每X帧抽1帧）:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.interval_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(self.root, text="开始处理", command=self.start_processing, style='Red.TButton').grid(row=2, column=1, pady=20)

    def start_processing(self):
        self.start_button = self.root.nametowidget('.!button')
        self.start_button['state'] = 'disabled'
        self.progress["value"] = 0
        
        try:
            video_path = self.video_path_var.get()
            interval = int(self.interval_var.get())
            
            if not video_path or interval < 1:
                messagebox.showerror("错误", "参数校验失败")
                return

            self.processing_thread = threading.Thread(
                target=self.run_ffmpeg_process, 
                args=(video_path, interval)
            )
            self.processing_thread.start()
            
        except ValueError:
            messagebox.showerror("错误", "间隔必须为整数")
        except Exception as e:
            messagebox.showerror("错误", f"未知异常: {str(e)}")

    def run_ffmpeg_process(self, video_path, interval):
        try:
            total_frames = self._get_total_frames(video_path)
            if total_frames <= 0:
                raise ValueError("无法获取有效视频帧数")
            
            output_path = os.path.join(
                os.path.dirname(video_path),
                f"抽帧_{os.path.basename(video_path)}"
            )
            
            remove_frames = total_frames // interval
            remain_frames = total_frames - remove_frames
            self._update_status(f"总帧数: {total_frames} → 将保留 {remain_frames} 帧")

            ffmpeg_cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"select=not(mod(n\\,{interval})),setpts='PTS-STARTPTS'",  # 修复时间基准
                "-vsync", "vfr",  # 添加可变帧率参数
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-f", "mp4",  # 强制指定输出格式
                "-y",
                output_path
            ]

            process = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE)
            
            while process.poll() is None:
                raw_line = process.stderr.readline().decode('utf-8', errors='replace')
                if not raw_line:
                    continue

                for line in raw_line.split('\r'):
                    line = line.strip()
                    if not line or any(x in line for x in ["Stream mapping", "libx264", "Output #0", "Metadata:"]):
                        continue

                    if "frame=" in line:
                        frame_match = re.search(r'frame=\s*(\d+)\s', line)
                        if frame_match and frame_match.group(1).isdigit() and total_frames > 0:
                            frame_num = int(frame_match.group(1))
                            progress = min(int((frame_num / total_frames) * 100), 99)
                            self.root.after(10, self._update_progress, progress)

                    if "kb/s" not in line and "time=" not in line:
                        self.root.after(10, self._update_status, f"处理中: {line}")
                        
        except Exception as e:
            self.root.after(10, self._update_status, f"错误: {str(e)}")
        finally:
            self.root.after(10, self._update_progress, 100)
            self.root.after(10, lambda: self.start_button.config(state='normal'))

    def _get_total_frames(self, video_path):
        probe_cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=nb_frames",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        try:
            result = subprocess.run(probe_cmd, check=True, 
                                  capture_output=True, text=True, timeout=10)
            return int(result.stdout.strip() or 0)
        except subprocess.TimeoutExpired:
            raise Exception("视频分析超时，请检查文件格式")

    def _update_progress(self, value):
        self.progress["value"] = value
        self.root.update_idletasks()

    def choose_video(self):
        file_path = filedialog.askopenfilename(
            title="选择输入视频",
            filetypes=[("视频文件", ("*.mp4", "*.mov", "*.avi", "*.mkv"))]
        )
        if file_path:
            self.video_path_var.set(file_path)
            self._update_status(f"已选择输入视频: {file_path}")

    def _update_status(self, text):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, text + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoFrameExtractorGUI(root)
    root.mainloop()