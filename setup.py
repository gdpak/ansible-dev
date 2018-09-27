from setuptools import setup, find_packages

setup(
    name='ansible_dev',
    version='0.1',
    py_modules=['ansible_dev'],
    install_requires=[
        'Click',
        'colorama',
        'docutils',
        'configparser',
    ],
    entry_points={
        'console_scripts': [
            'ansible-dev=ansible_dev.cli.run:cli',
        ],
    },
    include_package_data=True,
    packages = find_packages(),
)
