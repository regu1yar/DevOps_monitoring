FROM python:latest

RUN apt-get update && apt-get install -y vim curl jq
RUN pip3 install graphyte betterconf requests python-dateutil
RUN mkdir /code
COPY run.py /code/run.py
COPY runner.sh /code/runner.sh
COPY settings.json /code/settings.json
WORKDIR /code
CMD ["./runner.sh"]
