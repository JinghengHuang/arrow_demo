
from setuptools import setup, find_packages

setup(
    name="arrow-gateway-engine",
    version="0.1.0",
    description="Your project description",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)