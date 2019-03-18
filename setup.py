import os
from setuptools import setup

from mdtoc import __version__

setup(
    name="mdtoc",
    version=__version__,
    description="Adds table of contents to Markdown files",
    long_description=open(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")
    ).read(),
    long_description_content_type="text/markdown",
    author="Scott Frazer",
    author_email="scott.d.frazer@gmail.com",
    packages=["mdtoc"],
    install_requires=["xtermcolor", "requests<3.0.0"],
    scripts={"bin/mdtoc"},
    license="MIT",
    keywords="Markdown, table of contents, toc",
    url="http://github.com/scottfrazer/mdtoc",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Topic :: Utilities",
        "Topic :: Text Processing",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
    ],
)
