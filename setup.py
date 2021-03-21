from distutils.core import setup
setup(
  name='ftp_downloader',
  packages=['ftp_downloader'],
  version='0.2',
  license='MIT',
  description='Simple async ftp downloader based on aioftp. Download only modified files.',
  author='Aleksandr Sokolov',
  author_email='bigpewm@gmail.com',
  url='https://github.com/bigpe/FtpDownloader',
  download_url='https://github.com/bigpe/FtpDownloader/archive/pypi-0.1.tar.gz',
  keywords=['ftp', 'python3.7', 'asyncio ', 'aioftp', 'ftp-client', 'download', 'ftp'],
  install_requires=[
          'aioftp',
          'colorama',
          'cursor',
      ],
  classifiers=[  # Optional
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
