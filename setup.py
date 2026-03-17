from setuptools import setup

APP = ["claude2x.py"]
DATA_FILES = [("frames", ["frames/frame_{:03d}.png".format(i) for i in range(24)])]
OPTIONS = {
    "argv_emulation": False,
    "packages": ["rumps", "pytz"],
    "plist": {
        "CFBundleName": "Claude2x",
        "CFBundleDisplayName": "Claude 2x",
        "CFBundleIdentifier": "com.claude2x.app",
        "CFBundleVersion": "1.0.1",
        "CFBundleShortVersionString": "1.0.1",
        "LSUIElement": True,
        "NSHighResolutionCapable": True,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
