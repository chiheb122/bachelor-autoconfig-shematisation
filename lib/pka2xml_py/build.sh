#!/bin/bash
echo "🔧 Installing dependencies..."
pip install pybind11 setuptools wheel || exit 1

echo "⚙️ Building the project..."
python3 setup.py build_ext --inplace || {
    echo "❌ Build failed"
    exit 1
}

echo "✅ Build finished. Ready to use."
