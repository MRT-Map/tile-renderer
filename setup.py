from mypyc.build import mypycify
from setuptools import setup

setup(
    ext_modules=mypycify(
        [
            "renderer/math_utils.py",
        ]
    )
)
