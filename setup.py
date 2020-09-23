from setuptools import setup, find_packages

setup(name='isiver_utils',
    version='0.1.0',
    description='Isiver utility package for finance related endeavours',
    author='Ollie Sellers, Isaac Rayment',
    author_email='olliejsellers@gmail.com, isaacrayment123@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'yfinance',
        'mplfinance',
        'datetime',
        'pandas_datareader',
        'scipy',
        'pickle'
        ],
    zip_safe=True)
