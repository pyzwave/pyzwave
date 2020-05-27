"""Setup module for pyzwave"""

from setuptools import setup
import pyzwave

with open("README.md", "r") as fh:
    longDescription = fh.read()  # pylint: disable=invalid-name

setup(
    name="python-zwave",
    version=pyzwave.__version__,
    description="Library implementing a Z-Wave stack",
    long_description=longDescription,
    long_description_content_type="text/markdown",
    url="http://github.com/pyzwave/pyzwave",
    author="Micke Prag",
    author_email="micke.prag@telldus.se",
    license="GPL-3.0",
    packages=["pyzwave", "pyzwave.commandclass", "pyzwave.const"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Home Automation",
    ],
    python_requires=">=3.6",
    project_urls={
        "Documentation": "https://pyzwave.readthedocs.io",
        "Source": "http://github.com/pyzwave/pyzwave",
    },
)
