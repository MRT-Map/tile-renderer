from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
  name = 'tile-renderer',
  packages = ['renderer'],
  version = '1.2',
  license ='gpl-3.0',
  description = 'Leaflet.js tile renderer',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = '7d (from Minecart Rapid Transit Mapping Team)',
  author_email = 'i.third.7d@protonmail.com',
  url = 'https://github.com/MRT-Map/tile-renderer',
  download_url = 'https://github.com/MRT-Map/tile-renderer/archive/refs/tags/v1.1.tar.gz',
  keywords = ['leaflet', 'leaflet.js', 'leafletjs', 'map', 'tiles', 'renderer', 'tile-renderer', 'mapping'],
  python_requires='>=3.8',
  package_data={
    'renderer': ['skins/*', 'skins/assets/*'],
  },
  install_requires=[
    'pillow',
    'blessed',
    'sympy',
    'schema',
    'numpy'
  ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)