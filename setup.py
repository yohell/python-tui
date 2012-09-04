from distutils.core import setup

import tui

setup(name='tui',
      version=tui.__version__,
      description='Quickly add competent and helpful configuration to your python programs.',
      platforms='OS Independent',
      author='Joel Hedlund',
      author_email='yohell@ifm.liu.se',
      url='https://sourceforge.net/projects/python-tui/',
      download_url='https://sourceforge.net/projects/python-tui/',
      packages=['tui'],
      license=open('LICENSE.txt').read(),
      long_description='\n' + open('README.txt').read(),
      classifiers=[
          #'Development Status :: 5 - Production/Stable',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: User Interfaces',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.3',
          'Programming Language :: Python :: 2.4',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          ],
      )