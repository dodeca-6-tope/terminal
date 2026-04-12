from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            "ttyz.cbuf",
            sources=["src/ttyz/cbuf.c"],
            extra_compile_args=["-O2"],
        ),
    ],
)
