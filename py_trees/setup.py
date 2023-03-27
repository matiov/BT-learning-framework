from setuptools import setup, find_packages

package_name = 'py_trees'

setup(
    name=package_name,
    version='0.0.0',
    maintainer='Matteo Iovino',
    maintainer_email='matteo.iovino@se.abb.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'uuid',
        'pydot',
        'inspect-it',
        'more-itertools',
        'threaded',
        'multiprocess',
        'traceback2',
    ],
    tests_require=['pytest'],
)
