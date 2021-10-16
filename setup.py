from setuptools import setup


setup(
    name = 'webshooter',
    version = '0.0.1',
    description = 'frame work for efficient crawler programming',
    url = 'https://github.com/respect5716/webshooter',
    author = 'Yoon Yong Sun',
    autorh_email = 'respect5716@gmail.com',
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