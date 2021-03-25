# Dcoker use
1. "docker build -t (image tag name) ."
2. "docker run --name (container name) (docker_image)"
    * Add `-d` for backword if work no problem  
    * Add `-v` for save any data in container  
     `-v (user dir):(container dir)` becareful it will cover files to exited dir

# About Dockerfile
```
FROM python

COPY 火車幣_savedata.py .


RUN pip install bs4 && \
    pip install html5lib && \
    pip install requests

CMD ["python", "-u", "火車幣_savedata.py"]
```
* use `-u` in CMD for print immediately