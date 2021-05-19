# Dcoker usage steps
1. "docker build -t (image tag name) ."
2. "docker run --name (container name) (docker_image)"
    * Add `-d` for backword if work no problem  
    * Add `-v` for save any data in container  
     `-v (user dir):(container dir)` use carefully because it will cover files to exited dir .

# Sample Dockerfile
```
FROM python

COPY 火車幣_savedata.py .


RUN pip install bs4 && \
    pip install html5lib && \
    pip install requests

RUN apt-get update \
    &&  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
    
RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata 

CMD ["python", "-u", "火車幣_savedata.py"]
```
* Last two rows for setting docker container localtime  
* use `-u` in CMD for print immediately  