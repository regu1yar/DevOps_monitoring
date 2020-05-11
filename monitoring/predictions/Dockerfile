FROM python:3.6

RUN apt-get update && apt-get install -y vim curl jq locales \
 && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
 && locale-gen
RUN pip3 install selenium bs4 graphyte
RUN mkdir /code
COPY wait-for-grid.sh /code/wait-for-grid.sh
COPY run.py /code/run.py
COPY runner.sh /code/runner.sh
WORKDIR /code
CMD ["./wait-for-grid.sh", "./runner.sh"]