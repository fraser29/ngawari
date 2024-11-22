from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ngawari",
    version="0.1.0",
    author="Fraser M. Callaghan",
    author_email="callaghan.fm@gmail.com",
    description="A simple and functional toolkit for working with data in VTK.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fraser29/ngawari",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy",
        "vtk>=9.3.0",
        "scipy"
    ],
)
