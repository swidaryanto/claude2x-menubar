from setuptools import setup

APP = ["claude2x.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "packages": ["rumps", "PIL", "pytz", "numpy"],
    "plist": {
        "CFBundleName": "Claude2x",
        "CFBundleDisplayName": "Claude 2x",
        "CFBundleIdentifier": "com.claude2x.app",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "LSUIElement": True,  # hides from Dock, menubar-only
        "NSHighResolutionCapable": True,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
