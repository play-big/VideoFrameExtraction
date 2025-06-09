import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

def download_ffmpeg():
    """Download and extract ffmpeg"""
    print("Downloading ffmpeg...")
    
    # Create ffmpeg directory
    ffmpeg_dir = Path("ffmpeg")
    if ffmpeg_dir.exists():
        shutil.rmtree(ffmpeg_dir)
    ffmpeg_dir.mkdir()
    
    # Download ffmpeg
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = ffmpeg_dir / "ffmpeg.zip"
    
    try:
        print(f"Downloading ffmpeg from {ffmpeg_url} ...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        print("Download finished, extracting...")
        
        # Extract files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        
        # Move ffmpeg.exe and ffprobe.exe to correct location
        extracted_dir = next(ffmpeg_dir.glob("ffmpeg-*"))
        print("Moving files...")
        shutil.move(extracted_dir / "bin" / "ffmpeg.exe", ffmpeg_dir / "ffmpeg.exe")
        shutil.move(extracted_dir / "bin" / "ffprobe.exe", ffmpeg_dir / "ffprobe.exe")
        
        # Clean up
        print("Cleaning up temporary files...")
        shutil.rmtree(extracted_dir)
        zip_path.unlink()
        
        print("ffmpeg download completed!")
        return True
    except Exception as e:
        print(f"Failed to download ffmpeg: {str(e)}")
        print("Please check your network connection or download ffmpeg manually.")
        return False

def build_windows_app():
    try:
        print("Start building Windows application...")
        
        # Download ffmpeg
        if not download_ffmpeg():
            return False
        
        # Clean old build files
        print("Cleaning old build files...")
        if os.path.exists("build"):
            shutil.rmtree("build")
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        
        # Create spec file
        print("Creating spec file...")
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
    name='VideoFrameExtractor',
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
        
        # Run PyInstaller
        print("Running PyInstaller...")
        result = subprocess.run([
            "pyinstaller",
            "视频抽帧工具.spec",
            "--clean",
            "--noconfirm"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("PyInstaller failed!")
            print("Error message:")
            print(result.stderr)
            return False
        
        # Create release directory
        print("Creating release directory...")
        release_dir = Path("release")
        if release_dir.exists():
            shutil.rmtree(release_dir)
        release_dir.mkdir()
        
        # Copy ffmpeg and ffprobe
        print("Copying ffmpeg and ffprobe...")
        ffmpeg_src = "ffmpeg/ffmpeg.exe"
        ffprobe_src = "ffmpeg/ffprobe.exe"
        
        if not os.path.exists(ffmpeg_src) or not os.path.exists(ffprobe_src):
            print("Error: ffmpeg or ffprobe not found.")
            return False
        
        # Copy to release directory
        shutil.copy(ffmpeg_src, release_dir / "ffmpeg.exe")
        shutil.copy(ffprobe_src, release_dir / "ffprobe.exe")
        
        # Copy main program
        print("Copying main program...")
        shutil.copy("dist/视频抽帧工具.exe", release_dir)
        
        # Create startup batch file
        print("Creating startup script...")
        batch_content = """@echo off
echo Starting Video Frame Extractor...
start "" "视频抽帧工具.exe"
"""
        
        with open(release_dir / "start_video_frame_extractor.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        
        print("Build finished!")
        print(f"Release files are in: {release_dir.absolute()}")
        return True
        
    except Exception as e:
        print(f"Error during build: {str(e)}")
        return False

if __name__ == "__main__":
    if not build_windows_app():
        sys.exit(1) 