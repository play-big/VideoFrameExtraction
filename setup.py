from setuptools import setup

APP = ['app-mac.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'app.icns',
    'plist': {
        'CFBundleName': "视频抽帧工具",
        'CFBundleVersion': "1.0.0",
        'LSMinimumSystemVersion': "10.15.0"
    },
    'excludes': ['Carbon', 'PySide'],
    'includes': ['PyQt5']
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)