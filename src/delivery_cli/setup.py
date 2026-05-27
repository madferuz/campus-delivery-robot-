"""
setup.py for delivery_cli
-------------------------
Builds the `delivery-cli` console script entry point so users can run
the click-based CLI from anywhere after running:

    pip install -e src/delivery_cli

Inside a catkin workspace `catkin_make` will not run this file by
itself; we install the CLI separately because click + entry_points are
a pip concept.
"""

from setuptools import setup, find_packages

setup(
    name="delivery_cli",
    version="1.0.0",
    description="Command line interface for the Campus Delivery Robot.",
    author="Campus Delivery Team - Member 7",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "delivery-cli = delivery_cli.main:cli",
        ],
    },
)
