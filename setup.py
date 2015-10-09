from setuptools import setup, find_packages
setup(
    name = 'pyqwc',
    package_data = {'': ['*.rst']},
    version = '0.1',
    description = 'A soap interface to the Quickbooks Web Connector.',
    author = 'Bill Barry',
    author_email = 'bill@billbarry.org',
    url = 'https://github.com/BillBarry/pyqwc', # 
    download_url = 'https://github.com/peterldowns/mypackage/tarball/0.1', # I'll explain this in a second
    keywords = ['QuickBooks', 'soap', 'json'],
    classifiers = [],
    license= "MIT",
    packages = find_packages() 
    )
