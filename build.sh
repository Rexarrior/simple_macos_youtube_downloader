#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "[BUILD] Installing py2app..."
pip install py2app

echo "[BUILD] Building app..."
python3 setup.py py2app

echo "[BUILD] Done! App is in dist/"
ls -la dist/
