import subprocess
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import math # 新增导入
import sys  # 新增导入
import platform
import json
from datetime import datetime

def get_ffmpeg_path():
    """获取 ffmpeg 路径"""
    if platform.system() == 'Windows':
        # Windows 系统
        if getattr(sys, 'frozen', False):
            # 打包后的路径
            return os.path.join(os.path.dirname(sys.executable), 'ffmpeg', 'ffmpeg.exe')
        else:
            # 开发环境路径
            return 'ffmpeg'
    else:
        # macOS/Linux 系统
        if getattr(sys, 'frozen', False):
            # 打包后的路径
            return os.path.join(os.path.dirname(sys.executable), '..', 'Resources', 'ffmpeg')
        else:
            # 开发环境路径
            return 'ffmpeg'

class VideoFrameExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("视频抽帧工具 - 蛋包饭@快手") # 用户已修改标题，保持
        self.style = ttk.Style()
        self.style.theme_use('clam')
        # 设置环境变量
        if os.name == 'nt':
            os.environ['PYTHONIOENCODING'] = 'utf-8'
        # 检查依赖
        if not self.check_dependencies():
            messagebox.showerror("错误", "程序初始化失败，请检查依赖项。")
            root.destroy()
            return
        # 设置窗口关闭处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._init_ui_components()
        self._center_window(750, 550) # 增加窗口宽度，确保内容显示完整

    def check_dependencies(self):
        """检查必要的依赖是否已安装"""
        try:
            # 检查 ffmpeg 是否安装
            ffmpeg_path = get_ffmpeg_path()
            if ffmpeg_path:
                # 使用打包的 ffmpeg
                os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']
            
            if os.name == 'nt':
                subprocess.run(['where', 'ffmpeg'], check=True, capture_output=True)
            else:
                subprocess.run(['which', 'ffmpeg'], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            messagebox.showerror(
                "错误",
                "未找到 ffmpeg。请确保已安装 ffmpeg 并添加到系统环境变量中。\n"
                "Windows 用户可以从 https://ffmpeg.org/download.html 下载安装。"
            )
            return False
        except Exception as e:
            messagebox.showerror("错误", f"检查依赖时发生错误: {str(e)}")
            return False

    def _init_ui_components(self):
        self.style.configure('Red.TButton', foreground='red')

        # --- 主框架 --- 
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # --- 视频选择区域 --- 
        video_select_frame = ttk.LabelFrame(main_frame, text="视频文件", padding="10 10 10 10")
        video_select_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        video_select_frame.columnconfigure(1, weight=1)

        self.video_path_var = tk.StringVar()
        ttk.Label(video_select_frame, text="视频路径:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(video_select_frame, textvariable=self.video_path_var, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.select_video_button = ttk.Button(video_select_frame, text="选择视频", command=self.choose_video)
        self.select_video_button.grid(row=0, column=2, padx=5, pady=5)

        # --- 视频信息显示区域 --- 
        video_info_frame = ttk.LabelFrame(main_frame, text="视频信息", padding="10 10 10 10")
        video_info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.fps_var = tk.StringVar(value="帧率: -- 帧/秒")
        ttk.Label(video_info_frame, textvariable=self.fps_var).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        self.duration_var = tk.StringVar(value="总时长: -- 秒")
        ttk.Label(video_info_frame, textvariable=self.duration_var).grid(row=0, column=1, padx=5, pady=2, sticky="w")

        self.total_frames_var = tk.StringVar(value="总帧数: --")
        ttk.Label(video_info_frame, textvariable=self.total_frames_var).grid(row=0, column=2, padx=5, pady=2, sticky="w")

        # --- 参数设置区域 ---
        params_frame = ttk.LabelFrame(main_frame, text="抽帧参数", padding="10 10 10 10")
        params_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.interval_var = tk.StringVar(value="10")
        ttk.Label(params_frame, text="抽帧间隔（每X帧抽1帧）:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(params_frame, textvariable=self.interval_var, width=10).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # --- 进度条 ---
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, length=300, mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

        # --- 状态显示区域 ---
        status_frame = ttk.LabelFrame(main_frame, text="处理状态", padding="10 10 10 10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)

        # 状态文本显示
        self.status_text = tk.Text(status_frame, height=10, width=70, state="disabled") 
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # --- 操作按钮 --- 
        self.start_button_widget = ttk.Button(main_frame, text="开始处理", command=self.start_processing, style='Red.TButton')
        self.start_button_widget.grid(row=5, column=0, columnspan=3, pady=15)

        # --- 状态变量 ---
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=6, column=0, columnspan=3, sticky=tk.W)

    def _center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def start_processing(self):
        self.start_button_widget['state'] = 'disabled'
        self.select_video_button['state'] = 'disabled'
        self._update_status("开始处理...")
        
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
            self.start_button_widget['state'] = 'normal'
            self.select_video_button['state'] = 'normal'
            return
        except Exception as e:
            messagebox.showerror("错误", f"未知异常: {str(e)}")
            self.start_button_widget['state'] = 'normal'
            self.select_video_button['state'] = 'normal'

    def run_ffmpeg_process(self, video_path, interval):
        output_path = ""
        process_success = False
        try:
            video_info = self._get_video_info(video_path)
            total_frames = video_info.get("total_frames", 0)
            frame_rate = video_info.get("fps", 0)
            
            if total_frames <= 0:
                self.root.after(10, self._update_status, "错误: 无法获取有效视频帧数或视频信息。")
                return
            
            output_path = os.path.join(
                os.path.dirname(video_path),
                f"抽帧_{os.path.basename(video_path)}"
            )
            
            num_blocks = total_frames // interval
            estimated_retained_frames = total_frames - num_blocks
            
            self._update_status(f"总帧数: {total_frames}，帧率: {frame_rate:.2f}。每 {interval} 帧丢弃最后1帧。预计保留约 {estimated_retained_frames} 帧。")
            self._update_status(f"准备处理视频: {os.path.basename(video_path)}")
            self._update_status(f"输出路径: {output_path}")

            ffmpeg_cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"select='if(eq(mod(n,{interval}),{interval}-1),0,1)',setpts='PTS-STARTPTS'",
                "-vsync", "vfr",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-f", "mp4",
                "-y",
                output_path
            ]

            # Windows 特定的进程创建参数
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(
                ffmpeg_cmd,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                encoding='utf-8',
                errors='replace'
            )
            
            last_progress = -1
            while process.poll() is None:
                raw_line = process.stderr.readline()
                if not raw_line:
                    continue
                    
                for line in raw_line.split('\r'):
                    line = line.strip()
                    if not line:
                        continue
                        
                    if "frame=" in line:
                        match = re.search(r"frame=\s*(\d+)", line)
                        if match:
                            current_frame = int(match.group(1))
                            progress = min(int((current_frame / total_frames) * 100), 99)
                            if progress != last_progress:
                                self.root.after(0, self._update_progress, current_frame, total_frames)
                                last_progress = progress
                                
            process.wait()
            if process.returncode == 0:
                self.progress_var.set(100)
                self._update_status("视频处理成功完成！")
                process_success = True
            else:
                self._update_status(f"视频处理失败，错误码: {process.returncode}")
                
        except Exception as e:
            self._update_status(f"处理时发生错误: {str(e)}")
        finally:
            self.root.after(10, lambda: self.start_button_widget.config(state='normal'))
            self.root.after(10, lambda: self.select_video_button.config(state='normal'))
            if process_success and output_path:
                if messagebox.askyesno("处理完成", f"视频已处理完成并保存到:\n{output_path}\n\n是否打开输出文件夹？"):
                    self._open_output_folder(output_path)

    def _open_output_folder(self, file_path):
        folder_path = os.path.dirname(file_path)
        try:
            if os.path.exists(folder_path):
                if os.name == 'nt':  # Windows
                    try:
                        os.startfile(folder_path)
                    except Exception:
                        # 如果 os.startfile 失败，尝试使用 explorer
                        subprocess.run(['explorer', folder_path], check=True)
                elif os.uname().sysname == 'Darwin':  # macOS
                    subprocess.run(['open', folder_path], check=True)
                else:  # Linux and other Unix-like
                    subprocess.run(['xdg-open', folder_path], check=True)
            else:
                messagebox.showerror("错误", f"文件夹不存在: {folder_path}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")

    def _get_video_info(self, video_path):
        """使用 ffprobe 获取视频的详细信息"""
        if not os.path.exists(video_path):
            self._update_status(f"错误: 视频文件不存在 {video_path}")
            return {}

        probe_cmd_duration = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        probe_cmd_frames = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=nb_frames", "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        probe_cmd_fps = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]

        info = {}
        try:
            # 获取总时长
            result_duration = subprocess.run(probe_cmd_duration, check=True, capture_output=True, text=True, timeout=10)
            duration_str = result_duration.stdout.strip()
            if duration_str and duration_str != "N/A":
                info["duration"] = float(duration_str)
            else:
                info["duration"] = 0

            # 获取总帧数
            result_frames = subprocess.run(probe_cmd_frames, check=True, capture_output=True, text=True, timeout=10)
            frames_str = result_frames.stdout.strip()
            if frames_str and frames_str != "N/A" and frames_str.isdigit():
                info["total_frames"] = int(frames_str)
            else:
                 # 尝试从流条目中获取 codec_tag_string，有时 nb_frames 不可用但avg_frame_rate和duration可用
                probe_cmd_stream_info = [
                    "ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=avg_frame_rate,duration", "-of", "default=noprint_wrappers=1", video_path
                ]
                result_stream_info = subprocess.run(probe_cmd_stream_info, check=True, capture_output=True, text=True, timeout=10)
                stream_data = {}
                for line in result_stream_info.stdout.strip().split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        stream_data[key.strip()] = value.strip()
                
                if stream_data.get("avg_frame_rate") and stream_data.get("duration") and stream_data["avg_frame_rate"] != "0/0" and stream_data["duration"] != "N/A":
                    num, den = map(int, stream_data["avg_frame_rate"].split('/'))
                    avg_fps = num / den if den != 0 else 0
                    stream_duration = float(stream_data["duration"])
                    if avg_fps > 0 and stream_duration > 0:
                        info["total_frames"] = math.ceil(avg_fps * stream_duration)
                    else:
                        info["total_frames"] = 0
                else:
                    info["total_frames"] = 0

            # 获取帧率
            result_fps = subprocess.run(probe_cmd_fps, check=True, capture_output=True, text=True, timeout=10)
            fps_str = result_fps.stdout.strip()
            if fps_str and '/' in fps_str:
                num, den = map(int, fps_str.split('/'))
                info["fps"] = num / den if den != 0 else 0
            elif fps_str and fps_str != "N/A": # 有时直接是数值
                try:
                    info["fps"] = float(fps_str)
                except ValueError:
                    info["fps"] = 0 
            else:
                info["fps"] = 0

        except subprocess.TimeoutExpired:
            self.root.after(10, self._update_status, "错误: 分析视频信息超时。")
            return {}
        except subprocess.CalledProcessError as e:
            self.root.after(10, self._update_status, f"错误: ffprobe执行失败: {e.stderr}")
            return {}
        except Exception as e:
            self.root.after(10, self._update_status, f"错误: 获取视频信息时发生未知错误: {str(e)}")
            return {}
        return info

    def _get_total_frames(self, video_path): # 旧方法，现在使用 _get_video_info
        video_info = self._get_video_info(video_path)
        return video_info.get("total_frames", 0)

    def _update_progress(self, current_frame, total_frames):
        """更新进度条和状态信息"""
        progress = (current_frame / total_frames) * 100
        self.progress_var.set(progress)
        self.status_var.set(f"处理进度: {current_frame}/{total_frames} ({progress:.1f}%)")
        self.root.update_idletasks()

    def choose_video(self):
        file_path = filedialog.askopenfilename(
            title="选择输入视频",
            filetypes=[("视频文件", ("*.mp4", "*.mov", "*.avi", "*.mkv", "*.flv", "*.wmv"))] # 增加更多格式
        )
        if file_path:
            self.video_path_var.set(file_path)
            self._update_status(f"已选择输入视频: {file_path}")
            # 获取并显示视频信息
            video_info = self._get_video_info(file_path)
            if video_info:
                fps = video_info.get("fps", 0)
                duration = video_info.get("duration", 0)
                total_frames = video_info.get("total_frames", 0)
                self.fps_var.set(f"帧率: {fps:.2f} 帧/秒" if fps else "帧率: -- 帧/秒")
                self.duration_var.set(f"总时长: {duration:.2f} 秒" if duration else "总时长: -- 秒")
                self.total_frames_var.set(f"总帧数: {total_frames}" if total_frames else "总帧数: --")
                if not total_frames > 0:
                     self._update_status("警告: 未能准确获取视频总帧数，进度条可能不准确或处理可能失败。")
            else:
                self.fps_var.set("帧率: -- 帧/秒")
                self.duration_var.set("总时长: -- 秒")
                self.total_frames_var.set("总帧数: --")
                self._update_status("错误: 无法加载视频信息。")

    def _update_status(self, text):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, text + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")

    def on_closing(self):
        """处理窗口关闭事件"""
        if hasattr(self, 'processing_thread') and self.processing_thread.is_alive():
            if messagebox.askokcancel("确认退出", "处理正在进行中，确定要退出吗？"):
                self.root.destroy()
        else:
            self.root.destroy()

    def check_file_permissions(self, file_path):
        """检查文件权限"""
        try:
            if os.name == 'nt':
                import win32security
                import ntsecuritycon as con
                
                # 获取当前用户
                username = os.getenv('USERNAME')
                
                # 获取文件安全描述符
                sd = win32security.GetFileSecurity(
                    file_path, 
                    win32security.DACL_SECURITY_INFORMATION
                )
                
                # 获取 DACL
                dacl = sd.GetSecurityDescriptorDacl()
                
                # 检查写入权限
                return dacl.CheckAccess(
                    win32security.LookupAccountName(None, username)[0],
                    con.FILE_GENERIC_WRITE
                )
            else:
                return os.access(file_path, os.W_OK)
        except Exception:
            return False

def main():
    try:
        root = tk.Tk()
        app = VideoFrameExtractorGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("错误", f"程序发生严重错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()