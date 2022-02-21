FROM python:3

WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade py-cord --pre

COPY ./Bot .
COPY ./legal ./legal/

CMD ["python", "fuelBot.py"]
