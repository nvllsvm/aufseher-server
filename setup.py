import setuptools


setuptools.setup(
    name='aufseher',
    version='0.0.0',
    install_requires=[
        'tornado>=6',
        'pycurl',
        'pyyaml'
    ],
    py_modules=['aufseher'],
    entry_points={
        'console_scripts': ['aufseher = aufseher:main']
    }
)
