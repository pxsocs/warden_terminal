FROM python:3.8.0-slim

WORKDIR /build
COPY . /build

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# Install Tor
RUN apt-get install -y tor
RUN apt-get install -y git

# These are Tor ports
EXPOSE 9050
EXPOSE 9150
EXPOSE 3002

ENTRYPOINT ["sh","/build/docker_launcher.sh"]
CMD ["""]