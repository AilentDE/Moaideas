FROM python:3.12-slim

RUN pip install requests \
    && pip install bs4 \
    && pip install html5lib \
    && pip install apscheduler

# RUN apt-get update -y \
#     && apt-get install -y tzdata

# ENV TZ=Asia/Taipei

# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
#     && echo $TZ > /etc/timezone \
#     && dpkg-reconfigure -f noninteractive tzdata 

COPY app.py .

CMD ["python", "-u", "app.py"]