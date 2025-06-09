@echo off
setlocal enabledelayedexpansion

echo 正在准备打包环境...

:: 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python，请先安装 Python 3.8 或更高版本
    echo 请按任意键退出...
    pause >nul
    exit /b 1
)

:: 检查 pip 是否可用
pip --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 pip，请确保 Python 安装正确
    echo 请按任意键退出...
    pause >nul
    exit /b 1
)

:: 检查并安装必要的包
echo 正在检查必要的包...
pip install --upgrade pip
if errorlevel 1 (
    echo 错误：pip 升级失败
    echo 请按任意键退出...
    pause >nul
    exit /b 1
)

pip install pyinstaller
if errorlevel 1 (
    echo 错误：PyInstaller 安装失败
    echo 请按任意键退出...
    pause >nul
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo 错误：依赖包安装失败
    echo 请按任意键退出...
    pause >nul
    exit /b 1
)

:: 运行打包脚本
echo 正在打包应用程序...
python build-windows.py
if errorlevel 1 (
    echo 错误：打包失败！
    echo 请检查上方错误信息
    echo 请按任意键退出...
    pause >nul
    exit /b 1
)

:: 创建发布包
echo 正在创建发布包...
cd release
powershell Compress-Archive -Path * -DestinationPath ..\视频抽帧工具-Windows.zip -Force
if errorlevel 1 (
    echo 错误：创建发布包失败
    echo 请按任意键退出...
    pause >nul
    exit /b 1
)
cd ..

echo.
echo 打包完成！
echo 发布包已生成：视频抽帧工具-Windows.zip
echo 用户只需解压后双击"启动视频抽帧工具.bat"即可运行程序
echo.
echo 请按任意键退出...
pause >nul 