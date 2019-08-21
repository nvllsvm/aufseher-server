import setuptools


setuptools.setup(
    name='aufseher',
    version='0.0.0',
    install_requires=[
        'aiohttp',
        'configargparse'
    ],
    packages=['aufseher'],
    entry_points={
        'console_scripts': ['aufseher = aufseher.__main__:main']
    }
)
