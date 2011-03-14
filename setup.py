from setuptools import setup

setup(
    name='Ophot',
    version='0.1',
    long_description=__doc__,
    packages=['ophot'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'Flask-WTF', 'Flask-Uploads', 'PIL',
                      'configobj']
)
