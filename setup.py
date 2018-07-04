import setuptools

setuptools.setup(
    name='aufseher',
    version='0.1.0',
    install_requires=['tornado>=5',
                      'pycurl',
                      'pyyaml'],
    py_modules=['aufseher'],
    entry_points={
        'console_scripts': ['aufseher = aufseher:main']
    }
)
