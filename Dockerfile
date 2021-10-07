FROM --platform=linux/amd64 python:3.7

VOLUME /app
WORKDIR /app

RUN apt-get update -y \
    && apt-get install -y wget git unzip

# chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update -y \
    && apt-get install -y google-chrome-stable
    
# chromedriver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install git+https://github.com/respect5716/webshooter.git


EXPOSE 8888

CMD ["/bin/bash"]
