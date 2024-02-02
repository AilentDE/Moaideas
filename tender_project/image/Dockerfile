FROM python:3.12-slim

RUN pip install requests bs4 html5lib apscheduler pytz

# RUN apt-get update -y \
#     && apt-get install -y tzdata

# ENV TZ=Asia/Taipei

# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
#     && echo $TZ > /etc/timezone \
#     && dpkg-reconfigure -f noninteractive tzdata    

COPY app.py .

CMD ["python", "-u", "app.py"]