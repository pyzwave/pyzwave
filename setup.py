"""Setup module for pyzwave"""

from setuptools import setup
import pyzwave

setup(
    name="pyzwave",
    version=pyzwave.__version__,
    description="Library implementing a Z-Wave stack",
    url="http://github.com/pyzwave/pyzwave",
    author="Micke Prag",
    author_email="micke.prag@telldus.se",
    license="GPL-3.0",
    packages=["pyzwave"],
)
