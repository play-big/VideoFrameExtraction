#!/bin/bash

# 设置目标目录
TARGET_DIR="dist/视频抽帧工具.app/Contents/Resources/lib"

# 创建目标目录
mkdir -p "$TARGET_DIR"

# 复制 ffmpeg 和 ffprobe 到 Resources 目录
cp /opt/homebrew/bin/ffmpeg "dist/视频抽帧工具.app/Contents/Resources/"
cp /opt/homebrew/bin/ffprobe "dist/视频抽帧工具.app/Contents/Resources/"

# 复制所有必要的动态库
for lib in $(otool -L /opt/homebrew/bin/ffmpeg | grep -v "@rpath" | grep -v "/System" | grep -v "/usr/lib" | awk '{print $1}' | grep -v "^$"); do
    if [ -f "$lib" ]; then
        cp "$lib" "$TARGET_DIR/"
    fi
done

for lib in $(otool -L /opt/homebrew/bin/ffprobe | grep -v "@rpath" | grep -v "/System" | grep -v "/usr/lib" | awk '{print $1}' | grep -v "^$"); do
    if [ -f "$lib" ]; then
        cp "$lib" "$TARGET_DIR/"
    fi
done

# 修复库的路径
cd "$TARGET_DIR"
for lib in *.dylib; do
    if [ -f "$lib" ]; then
        install_name_tool -change "$lib" "@executable_path/../Resources/lib/$lib" "../ffmpeg"
        install_name_tool -change "$lib" "@executable_path/../Resources/lib/$lib" "../ffprobe"
    fi
done

echo "库文件复制完成！" 