import setuptools


setuptools.setup(
    name='aufseher',
    install_requires=[
        'tornado>=5',
        'pycurl',
        'pyyaml'
    ],
    py_modules=['aufseher'],
    entry_points={
        'console_scripts': ['aufseher = aufseher:main']
    },
    setuptools_requires=['setuptools_scm'],
    use_setuptools_scm=True
)
