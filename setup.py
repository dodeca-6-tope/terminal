from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            "ttyz.ext",
            sources=["src/ttyz/csrc/module.c"],
            extra_compile_args=["-O2"],
        ),
    ],
)
