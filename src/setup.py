from setuptools import setup, find_packages

setup(
    name='thememapper.diazo',
    version='0.1',
    description='thememapper module containing diazo server for development',
    author='Brandon Tilstra',
    author_email='tilstra@gmail.com',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['thememapper'],
    include_package_data=True,
    long_description=open('README.rst').read(),
    license='LICENSE.txt',
    url='http://pypi.python.org/pypi/thememapper/',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet",
      ],
    install_requires=['setuptools','Flask','requests','urlparse'],
    zip_safe=False
)