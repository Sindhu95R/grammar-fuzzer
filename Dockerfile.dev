FROM ubuntu:bionic

RUN sed -i 's:^path-exclude=/usr/share/man:#path-exclude=/usr/share/man:' \
        /etc/dpkg/dpkg.cfg.d/excludes

RUN apt-get update && \
    apt-get -y install python3.6 && \
    apt-get -y install python3-pip && \
    apt-get install -y  man manpages-posix

WORKDIR '/usr/src'

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3","main.py"]