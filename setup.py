from setuptools import setup

setup(name='OffsetHysterese',
      version='0.0.1',
      description='CraftBeerPi4 Plugin with two temp offset areas',
      author='HappyHibo',
      author_email='',
      url='https://github.com/happyhibo/cbpi4-OffsetHysterese',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'OffsetHysterese': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-OffsetHysterese'],
     )
