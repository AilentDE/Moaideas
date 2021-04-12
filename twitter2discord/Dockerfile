FROM python

COPY app.py .

COPY .env .

RUN pip install python-dotenv &&\
    pip install pip requests

CMD ["python", "-u", "app.py"]