# WebShooter


## Introduction
Web Crawling Framework

![image](https://user-images.githubusercontent.com/65707703/136631964-ae0687ca-3391-4ef6-8f94-007eb0ef6ab1.png)



## Installation

```
pip install git+https://github.com/respect5716/webshooter.git
```

## Tutorial
* [static crawling](https://github.com/respect5716/webshooter/blob/main/tutorials/static_crawler.ipynb)


## Dockefile

```
docker build -t webshooter:latest .
docker run -it --name webshooter -v $PWD:/app -p 8080:8080 webshooter:latest bash
```

## Test
```
python -m pytest tests
```