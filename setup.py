from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in real_fitness/__init__.py
from real_fitness import __version__ as version

setup(
	name="real_fitness",
	version=version,
	description="A Custom App for A Gym ",
	author="Lewin Villar",
	author_email="lewinvillar@tzcode.tech",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
