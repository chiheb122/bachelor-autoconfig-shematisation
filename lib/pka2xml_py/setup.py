from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "pka2core",
        sources=["cpp_binding/bindings.cpp"],
        include_dirs=[
            pybind11.get_include(),
            "cpp_binding/include",
        ],
        libraries=["cryptopp","z"],  # Assumes installed or static linked
        language="c++"
    )
]

setup(
    name="pka2core",
    version="1.0.0",
    author="Chiheb",
    description="Decrypt/Encrypt .pkt files from Cisco Packet Tracer",
    ext_modules=ext_modules,
    zip_safe=False,
)
