from setuptools import setup

setup(
    name='ansible_dev',
    version='0.1',
    py_modules=['ansible_dev'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'ansible-dev=ansible_dev:cli',
        ],
    },
)
