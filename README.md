MONGO instalation
   38  sudo apt install docker.io
   39  sudo service docker status
   40  sudo docker pull mongo
   61  sudo docker ps
   62  sudo docker run -it --name mongodb -p 27017:27017 -d mongo
   63  sudo docker run -it --name mongodb2 -p 27017:27017 -d mongo
