#!/bin/bash
echo "🔧 Installing dependencies..."
pip install pybind11 setuptools wheel

echo "⚙️ Building the project..."
python3 setup.py build_ext --inplace

echo "✅ Build finished. Ready to use."
