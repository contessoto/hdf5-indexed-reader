from setuptools import setup, find_packages

setup(
    name="hdf5-indexed-reader",
    version="1.0.0",
    description="Python port of hdf5-indexed-reader for efficient remote HDF5 access.",
    author="Jules",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
