FROM python:3

WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade py-cord --pre
RUN pip3 install -r requirements.txt

COPY ./Bot .
COPY ./legal ./legal/

CMD ["python", "fuelBot.py"]
