from setuptools import setup, find_packages

setup(
    name="defi_econ",
    packages=find_packages(),
    install_requires=["numpy", "pandas", "scipy", "requests", "matplotlib", "openpyxl"],
    extras_require={"dev": ["pylint", "black"]},
)
