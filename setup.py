from setuptools import setup, find_packages

setup(
    name='systemd-analyze-visual',
    version='0.1.0',
    description='Enhanced systemd-analyze with visual output',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'dbus-python>=1.2.16',
    ],
    entry_points={
        'console_scripts': [
            'systemd-analyze-visual=systemd_analyze_visual.cli:main',
        ],
    },
    python_requires='>=3.8',
)