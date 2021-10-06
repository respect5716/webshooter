FROM --platform=linux/amd64 python:3.7

VOLUME /app
WORKDIR /app

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install git+https://github.com/respect5716/webshooter.git


EXPOSE 8888

CMD ["/bin/bash"]
