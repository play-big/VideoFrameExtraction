import subprocess
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import math # 新增导入
import sys
import json
from datetime import datetime
import platform
import traceback

class VideoFrameExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("视频抽帧工具 - 蛋包饭@快手") # 用户已修改标题，保持
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._init_ui_components()
        self._center_window(750, 550) # 增加窗口宽度，确保内容显示完整

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
        # 减小视频路径输入框宽度
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

        # 减小状态输出框宽度，并确保其随窗口拉伸
        self.status_text = tk.Text(status_frame, height=10, width=70, state="disabled") 
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # 添加滚动条到Text组件
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # --- 操作按钮 --- 
        self.start_button_widget = ttk.Button(main_frame, text="开始处理", command=self.start_processing, style='Red.TButton')
        self.start_button_widget.grid(row=5, column=0, columnspan=3, pady=15)

        # --- 状态显示区域 ---
        status_var_frame = ttk.LabelFrame(main_frame, text="处理状态", padding="10 10 10 10")
        status_var_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        status_var_frame.columnconfigure(0, weight=1)
        status_var_frame.rowconfigure(0, weight=1)

        # 减小状态输出框宽度，并确保其随窗口拉伸
        self.status_var = tk.StringVar()
        ttk.Label(status_var_frame, textvariable=self.status_var).grid(row=0, column=0, padx=5, pady=2, sticky="w")

    def _center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # _create_widgets 方法的内容已整合到 _init_ui_components
    # def _create_widgets(self):
    #     ...

    def start_processing(self):
        # self.start_button = self.root.nametowidget('.!button') # 旧方式
        # self.start_button['state'] = 'disabled' # 旧方式
        self.start_button_widget['state'] = 'disabled'
        self.select_video_button['state'] = 'disabled' # 选择视频按钮也禁用
        self._update_status("开始处理...") # 添加初始状态
        
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
            frame_rate = video_info.get("frame_rate", 0)
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

            ffmpeg_path = self.get_ffmpeg_path()
            ffmpeg_cmd = [
                ffmpeg_path,
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

            env = os.environ.copy()
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.executable)))
                lib_path = os.path.join(base_path, 'Resources', 'lib')
                env['DYLD_LIBRARY_PATH'] = lib_path
                env['DYLD_FALLBACK_LIBRARY_PATH'] = lib_path

            process = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE, env=env)
            last_progress = -1
            while process.poll() is None:
                raw_line = process.stderr.readline().decode('utf-8', errors='replace')
                if not raw_line:
                    continue
                for line in raw_line.split('\r'):
                    line = line.strip()
                    if not line:
                        continue
                    # 只保留帧进度信息
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
                self.status_text.config(state="normal")
                self.status_text.insert(tk.END, "视频处理成功完成！\n")
                self.status_text.see(tk.END)
                self.status_text.config(state="disabled")
                process_success = True
            else:
                self.status_text.config(state="normal")
                self.status_text.insert(tk.END, f"视频处理失败，错误码: {process.returncode}\n")
                self.status_text.see(tk.END)
                self.status_text.config(state="disabled")
        except Exception as e:
            self.status_text.config(state="normal")
            self.status_text.insert(tk.END, f"处理时发生错误: {str(e)}\n")
            self.status_text.see(tk.END)
            self.status_text.config(state="disabled")
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
                if os.name == 'nt': # Windows
                    os.startfile(folder_path)
                elif os.uname().sysname == 'Darwin': # macOS
                    subprocess.run(['open', folder_path], check=True)
                else: # Linux and other Unix-like
                    subprocess.run(['xdg-open', folder_path], check=True)
            else:
                messagebox.showerror("错误", f"文件夹不存在: {folder_path}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")

    def _get_video_info(self, video_path):
        try:
            ffprobe_path = self.get_ffprobe_path()
            # 获取时长
            cmd = [
                ffprobe_path,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            env = os.environ.copy()
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.executable)))
                lib_path = os.path.join(base_path, 'Resources', 'lib')
                env['DYLD_LIBRARY_PATH'] = lib_path
                env['DYLD_FALLBACK_LIBRARY_PATH'] = lib_path
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            if result.returncode != 0:
                self._update_status(f"获取视频信息失败: {result.stderr}")
                return {"duration": 0, "total_frames": 0, "frame_rate": 0}
            duration = float(result.stdout.strip())
            # 获取总帧数
            cmd_frames = [
                ffprobe_path,
                "-v", "error",
                "-select_streams", "v:0",
                "-count_packets",
                "-show_entries", "stream=nb_read_packets",
                "-of", "csv=p=0",
                video_path
            ]
            result_frames = subprocess.run(cmd_frames, capture_output=True, text=True, env=env)
            if result_frames.returncode != 0:
                self._update_status(f"获取帧数失败: {result_frames.stderr}")
                return {"duration": duration, "total_frames": 0, "frame_rate": 0}
            total_frames = int(result_frames.stdout.strip())
            # 获取帧率
            cmd_fps = [
                ffprobe_path,
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=r_frame_rate",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            result_fps = subprocess.run(cmd_fps, capture_output=True, text=True, env=env)
            if result_fps.returncode != 0:
                self._update_status(f"获取帧率失败: {result_fps.stderr}")
                frame_rate = 0
            else:
                fps_str = result_fps.stdout.strip()
                if "/" in fps_str:
                    num, denom = fps_str.split("/")
                    frame_rate = float(num) / float(denom) if float(denom) != 0 else 0
                else:
                    frame_rate = float(fps_str) if fps_str else 0
            return {
                "duration": duration,
                "total_frames": total_frames,
                "frame_rate": frame_rate
            }
        except Exception as e:
            self._update_status(f"获取视频信息时发生错误: {str(e)}")
            return {"duration": 0, "total_frames": 0, "frame_rate": 0}

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
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.video_path = file_path
            self.video_path_var.set(file_path)
            self._update_status(f"已选择输入视频: {file_path}")
            # 获取并显示视频信息
            video_info = self._get_video_info(file_path)
            if video_info:
                fps = video_info.get("frame_rate", 0)
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

    def check_ffmpeg(self):
        """检查 ffmpeg 是否可用"""
        try:
            # 首先尝试使用系统路径中的 ffmpeg
            subprocess.run(['which', 'ffmpeg'], check=True, capture_output=True)
            self._update_status("使用系统安装的 ffmpeg")
            return True
        except subprocess.CalledProcessError:
            # 如果系统路径中没有，尝试使用打包后的 ffmpeg
            if getattr(sys, 'frozen', False):
                if platform.system() == 'Darwin':  # macOS
                    base_path = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
                    ffmpeg_path = os.path.join(base_path, 'Resources', 'ffmpeg')
                    if os.path.exists(ffmpeg_path):
                        self._update_status("使用打包的 ffmpeg")
                        return True
            self._update_status("错误: 未找到 ffmpeg")
            messagebox.showerror("错误", "未找到 ffmpeg。请确保已安装 ffmpeg 并添加到系统环境变量中。\n\n可以使用以下命令安装：\nbrew install ffmpeg")
            return False
    
    def get_ffmpeg_path(self):
        """获取 ffmpeg 路径"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的应用，使用应用内的 ffmpeg
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.executable)))
            ffmpeg_path = os.path.join(base_path, 'Resources', 'ffmpeg')
            if os.path.exists(ffmpeg_path):
                return ffmpeg_path
        return 'ffmpeg'

    def get_ffprobe_path(self):
        """获取 ffprobe 路径"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的应用，使用应用内的 ffprobe
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.executable)))
            ffprobe_path = os.path.join(base_path, 'Resources', 'ffprobe')
            if os.path.exists(ffprobe_path):
                return ffprobe_path
        return 'ffprobe'

    def process_video(self):
        """处理视频"""
        if not self.video_path:
            self._update_status("错误: 请先选择视频文件")
            return
            
        try:
            # 获取视频信息
            duration, total_frames, error = self._get_video_info(self.video_path)
            if error:
                self._update_status(f"错误: {error}")
                return
                
            if total_frames == 0:
                self._update_status("错误: 无法获取有效视频帧数或视频信息。")
                return
                
            # 计算保留的帧数
            keep_frames = total_frames - (total_frames // 10)
            self._update_status(f"总帧数: {total_frames}。每 10 帧丢弃最后1帧。预计保留约 {keep_frames} 帧。")
            
            # 准备输出路径
            video_name = os.path.basename(self.video_path)
            output_dir = os.path.dirname(self.video_path)
            output_name = f"抽帧_{video_name}"
            output_path = os.path.join(output_dir, output_name)
            
            self._update_status(f"准备处理视频: {video_name}")
            self._update_status(f"输出路径: {output_path}")
            
            # 获取 ffmpeg 路径
            ffmpeg_path = self.get_ffmpeg_path()
            self._update_status(f"ffmpeg路径: {ffmpeg_path}")
            
            # 设置环境变量
            env = os.environ.copy()
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(sys.executable)))
                lib_path = os.path.join(base_path, 'Resources', 'lib')
                env['DYLD_LIBRARY_PATH'] = lib_path
                env['DYLD_FALLBACK_LIBRARY_PATH'] = lib_path
                self._update_status(f"设置库路径: {lib_path}")
            
            # 构建 ffmpeg 命令
            cmd = [
                ffmpeg_path,
                '-i', self.video_path,
                '-vf', f'select=not(mod(n,10)),setpts=N/FRAME_RATE/TB',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-y',
                output_path
            ]
            
            self._update_status(f"执行命令: {' '.join(cmd)}")
            
            # 运行 ffmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=env
            )
            
            # 更新进度条
            self.progress_var.set(0)
            self.progress_bar['maximum'] = total_frames
            
            # 读取输出
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # 解析进度
                    if 'frame=' in output:
                        try:
                            frame = int(output.split('frame=')[1].split()[0])
                            self.progress_var.set(frame)
                            self._update_status(f"处理进度: {frame}/{total_frames}")
                        except:
                            pass
            
            # 检查处理结果
            if process.returncode == 0:
                self._update_status("处理完成！")
            else:
                self._update_status(f"处理失败，返回码: {process.returncode}")
                
        except Exception as e:
            self._update_status(f"处理时发生错误: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoFrameExtractorGUI(root)
    root.mainloop()