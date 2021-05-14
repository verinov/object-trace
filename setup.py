import pathlib
from setuptools import setup

setup(
    name="object-trace",
    version="0.1.1",
    description="Trace every use of selected objects",
    long_description=(pathlib.Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/verinov/object-trace",
    author="Alexander Verinov",
    author_email="alex@verinov.dev",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=["object_trace"],
    include_package_data=False,
    install_requires=[],
)
