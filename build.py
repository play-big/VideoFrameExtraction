import os
import sys
import shutil
import subprocess
import platform

def check_ffmpeg():
    """检查 ffmpeg 是否在系统路径中"""
    try:
        if platform.system() == 'Windows':
            subprocess.run(['where', 'ffmpeg'], check=True, capture_output=True)
        else:
            subprocess.run(['which', 'ffmpeg'], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def copy_ffmpeg():
    """复制 ffmpeg 和 ffprobe 到应用程序包中"""
    if platform.system() == 'Windows':
        # Windows 系统
        ffmpeg_dir = os.path.join('dist', '视频抽帧工具', 'ffmpeg')
        os.makedirs(ffmpeg_dir, exist_ok=True)
        shutil.copy('ffmpeg.exe', ffmpeg_dir)
        shutil.copy('ffprobe.exe', ffmpeg_dir)
    else:
        # macOS/Linux 系统
        resources_dir = os.path.join('dist', '视频抽帧工具.app', 'Contents', 'Resources')
        lib_dir = os.path.join(resources_dir, 'lib')
        os.makedirs(lib_dir, exist_ok=True)
        
        # 复制 ffmpeg 和 ffprobe
        shutil.copy('/opt/homebrew/bin/ffmpeg', resources_dir)
        shutil.copy('/opt/homebrew/bin/ffprobe', resources_dir)
        os.chmod(os.path.join(resources_dir, 'ffmpeg'), 0o755)
        os.chmod(os.path.join(resources_dir, 'ffprobe'), 0o755)
        
        # 获取 ffmpeg 和 ffprobe 的依赖库
        ffmpeg_deps = subprocess.check_output(['otool', '-L', '/opt/homebrew/bin/ffmpeg']).decode()
        ffprobe_deps = subprocess.check_output(['otool', '-L', '/opt/homebrew/bin/ffprobe']).decode()
        
        # 合并依赖库列表
        all_deps = set()
        for line in ffmpeg_deps.split('\n') + ffprobe_deps.split('\n'):
            if '/opt/homebrew/' in line:
                lib_path = line.split()[0]
                all_deps.add(lib_path)
        
        # 复制依赖库
        for dep in all_deps:
            if os.path.exists(dep):
                lib_name = os.path.basename(dep)
                shutil.copy(dep, lib_dir)
                os.chmod(os.path.join(lib_dir, lib_name), 0o755)
        
        # 修改 ffmpeg 和 ffprobe 的库搜索路径
        for binary in ['ffmpeg', 'ffprobe']:
            binary_path = os.path.join(resources_dir, binary)
            # 获取当前依赖
            deps = subprocess.check_output(['otool', '-L', binary_path]).decode()
            for line in deps.split('\n'):
                if '/opt/homebrew/' in line:
                    old_path = line.split()[0]
                    lib_name = os.path.basename(old_path)
                    new_path = f'@executable_path/../Resources/lib/{lib_name}'
                    subprocess.run(['install_name_tool', '-change', old_path, new_path, binary_path])
            
            # 修改二进制文件本身的路径
            subprocess.run(['install_name_tool', '-id', f'@executable_path/../Resources/{binary}', binary_path])
            
            # 修改库文件的路径
            for lib in os.listdir(lib_dir):
                if lib.endswith('.dylib'):
                    lib_path = os.path.join(lib_dir, lib)
                    # 获取库的依赖
                    lib_deps = subprocess.check_output(['otool', '-L', lib_path]).decode()
                    for line in lib_deps.split('\n'):
                        if '/opt/homebrew/' in line:
                            old_path = line.split()[0]
                            dep_name = os.path.basename(old_path)
                            new_path = f'@executable_path/../Resources/lib/{dep_name}'
                            subprocess.run(['install_name_tool', '-change', old_path, new_path, lib_path])
                    # 修改库本身的路径
                    subprocess.run(['install_name_tool', '-id', f'@executable_path/../Resources/lib/{lib}', lib_path])

def build():
    """构建可执行文件"""
    try:
        # 安装必要的打包依赖
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        
        # 根据操作系统设置构建参数
        if platform.system() == 'Windows':
            separator = ';'
            icon_param = '--icon=app.ico'
        else:
            separator = ':'
            icon_param = '--icon=app.icns' if os.path.exists('app.icns') else ''
        
        # 构建命令
        build_cmd = [
            'pyinstaller',
            '--name=视频抽帧工具',
            '--windowed',  # 不显示控制台窗口
            icon_param,  # 图标
            f'--add-data=README.md{separator}.',  # 添加说明文件
            '--noconfirm',  # 不询问确认
            '--clean',  # 清理临时文件
            'app-mac.py' if platform.system() == 'Darwin' else 'app-windows.py'
        ]
        
        # 移除空参数
        build_cmd = [x for x in build_cmd if x]
        
        # 执行构建
        subprocess.run(build_cmd, check=True)
        
        # 复制 ffmpeg
        if not copy_ffmpeg():
            print("警告: 未能复制 ffmpeg，请确保 ffmpeg 在系统路径中")
        
        # 复制 README.md
        if platform.system() == 'Windows':
            shutil.copy2('README.md', 'dist/视频抽帧工具/README.md')
        else:
            shutil.copy2('README.md', 'dist/视频抽帧工具.app/Contents/Resources/README.md')
        
        print("构建完成！")
        if platform.system() == 'Windows':
            print("可执行文件位于 dist/视频抽帧工具 目录中")
        else:
            print("可执行文件位于 dist/视频抽帧工具.app 目录中")
        
    except Exception as e:
        print(f"构建过程中出错: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    if not check_ffmpeg():
        print("错误: 未找到 ffmpeg，请确保已安装并添加到系统路径")
        sys.exit(1)
    
    if build():
        print("打包成功！")
    else:
        print("打包失败！")
        sys.exit(1) 