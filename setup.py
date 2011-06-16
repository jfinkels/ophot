"""A photography portfolio website which allows an administrator user to upload
photos and edit settings.

"""
from setuptools import setup

setup(
    author='Jeffrey Finkelstein',
    author_email='jeffrey.finkelstein@gmail.com',
    description='Photography portfolio website',
    include_package_data=True,
    install_requires=['Flask', 'Flask-WTF', 'Flask-Uploads', 'PIL',
                      'configobj'],
    keywords='photography website',
    license='GNU AGPLv3',
    long_description=__doc__,
    name='Ophot',
    packages=['ophot'],
    setup_requires=['setuptools_hg'],
    test_suite='ophot.tests.alltests.alltests',
    url='https://github.com/jfinkels/ophot',
    version='0.1',
    zip_safe=False
)
