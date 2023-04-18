from setuptools import setup, find_packages

setup(
    name="environ",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas == 2.0.0",
        "scipy",
        "requests",
        "matplotlib",
        "web3",
    ],
    extras_require={"dev": ["pylint", "black"]},
)
