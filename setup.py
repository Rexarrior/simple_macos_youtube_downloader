#!/usr/bin/env python3
from setuptools import setup

APP = ["video_downloader.py"]
APP_NAME = "Video Downloader"
BUNDLE_ID = "com.videodownloader"

setup(
    app=APP,
    name=APP_NAME,
    options={
        "py2app": {
            "bundle_identifier": BUNDLE_ID,
        }
    },
)
