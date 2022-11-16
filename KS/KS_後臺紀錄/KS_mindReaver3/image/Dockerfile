FROM python:3.9.13-slim

RUN pip install requests \
    && pip install bs4 \
    && pip install html5lib \
    && pip install pymongo

RUN apt-get update -y \
    && apt-get install -y tzdata

ENV TZ=Asia/Taipei

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata 

COPY app.py .

CMD ["python", "-u", "app.py"]