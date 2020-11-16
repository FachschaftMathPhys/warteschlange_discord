FROM python:3.7
MAINTAINER Christian Heusel <christian@heusel.eu>

COPY requirements.txt disc.py ./
RUN pip3 install -r requirements.txt
CMD ["python3", "disc.py"]
