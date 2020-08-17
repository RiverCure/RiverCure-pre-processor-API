FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev && \
    apt-get install -y libgdal-dev libboost-all-dev libcgal-dev gmsh

WORKDIR /usr/src/app

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python3", "./app.py" ]