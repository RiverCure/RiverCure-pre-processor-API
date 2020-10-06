# build the flask container
docker build -t jorgemsmarques/rivercure-pre-processor-api .

# start docker container
docker run -d -p 5000:5000 --name rc-pre-processor-api --rm jorgemsmarques/rivercure-pre-processor-api