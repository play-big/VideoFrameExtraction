import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

def download_ffmpeg():
    """下载并解压 ffmpeg"""
    print("正在下载 ffmpeg...")
    
    # 创建 ffmpeg 目录
    ffmpeg_dir = Path("ffmpeg")
    if ffmpeg_dir.exists():
        shutil.rmtree(ffmpeg_dir)
    ffmpeg_dir.mkdir()
    
    # 下载 ffmpeg
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = ffmpeg_dir / "ffmpeg.zip"
    
    try:
        print(f"正在从 {ffmpeg_url} 下载 ffmpeg...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        print("下载完成，正在解压...")
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        
        # 移动 ffmpeg.exe 和 ffprobe.exe 到正确位置
        extracted_dir = next(ffmpeg_dir.glob("ffmpeg-*"))
        print("正在移动文件...")
        shutil.move(extracted_dir / "bin" / "ffmpeg.exe", ffmpeg_dir / "ffmpeg.exe")
        shutil.move(extracted_dir / "bin" / "ffprobe.exe", ffmpeg_dir / "ffprobe.exe")
        
        # 清理临时文件
        print("正在清理临时文件...")
        shutil.rmtree(extracted_dir)
        zip_path.unlink()
        
        print("ffmpeg 下载完成！")
        return True
    except Exception as e:
        print(f"下载 ffmpeg 失败: {str(e)}")
        print("请检查网络连接或手动下载 ffmpeg")
        return False

def build_windows_app():
    try:
        print("开始打包 Windows 应用程序...")
        
        # 下载 ffmpeg
        if not download_ffmpeg():
            return False
        
        # 清理旧的构建文件
        print("正在清理旧的构建文件...")
        if os.path.exists("build"):
            shutil.rmtree("build")
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        
        # 创建 spec 文件
        print("正在创建 spec 文件...")
        spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app-windows.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='视频抽帧工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)
"""
        
        with open("视频抽帧工具.spec", "w", encoding="utf-8") as f:
            f.write(spec_content)
        
        # 运行 PyInstaller
        print("正在运行 PyInstaller...")
        result = subprocess.run([
            "pyinstaller",
            "视频抽帧工具.spec",
            "--clean",
            "--noconfirm"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("PyInstaller 运行失败！")
            print("错误信息：")
            print(result.stderr)
            return False
        
        # 创建发布目录
        print("正在创建发布目录...")
        release_dir = Path("release")
        if release_dir.exists():
            shutil.rmtree(release_dir)
        release_dir.mkdir()
        
        # 复制 ffmpeg 和 ffprobe
        print("正在复制 ffmpeg 和 ffprobe...")
        ffmpeg_src = "ffmpeg/ffmpeg.exe"
        ffprobe_src = "ffmpeg/ffprobe.exe"
        
        if not os.path.exists(ffmpeg_src) or not os.path.exists(ffprobe_src):
            print("错误：未找到 ffmpeg 或 ffprobe")
            return False
        
        # 复制到发布目录
        shutil.copy(ffmpeg_src, release_dir / "ffmpeg.exe")
        shutil.copy(ffprobe_src, release_dir / "ffprobe.exe")
        
        # 复制主程序
        print("正在复制主程序...")
        shutil.copy("dist/视频抽帧工具.exe", release_dir)
        
        # 创建启动批处理文件
        print("正在创建启动脚本...")
        batch_content = """@echo off
echo 正在启动视频抽帧工具...
start "" "视频抽帧工具.exe"
"""
        
        with open(release_dir / "启动视频抽帧工具.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        
        print("打包完成！")
        print(f"发布文件位于: {release_dir.absolute()}")
        return True
        
    except Exception as e:
        print(f"打包过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    if not build_windows_app():
        sys.exit(1) 