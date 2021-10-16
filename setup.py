from setuptools import setup


setup(
    name = 'webshooter',
    version = '0.0.1',
    license = 'MIT',
    author = 'Yoon Yong Sun',
    autorh_email = 'respect5716@gmail.com',
    url = 'https://github.com/respect5716/webshooter',
    description = 'Python package for almost all web scraping scenarios.',
    python_requires = '>=3.6',
    packages = ["webshooter"],
    install_requires = [
        "beautifulsoup4",
        "selenium",
        "pandas",
        "tqdm",
        "requests",
        "ray",
    ],
)