# WebShooter


## Introduction
Web Crawling Framework


## Installation

```
pip install git+https://github.com/respect5716/webshooter.git
```

## Tutorial
* [static crawling](https://github.com/respect5716/webshooter/blob/main/tutorials/static_crawler.ipynb)


## Dockefile

```
docker build -t webshooter:latest .
docker run -it --name webshooter -v $PWD:/app -p 8888:8888 webshooter:latest bash
```