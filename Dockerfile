FROM python:3

WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./Bot .


CMD ["python", "fuelBot.py"]
