# Setup
  - Install Docker Decktop: https://www.docker.com/products/docker-desktop
  - Install git if not installed: <package manager> install git
  - Clone the GitHub repository to your local system: git clone https://github.com/AJAUDET/SecureDrop

  - Create Local Docker Containers: docker-compose up -d 
  - Pause Local Docker Containers: docker-compose stop
  - Terminate Local Docker Containers: docker-compose down

# Commands to access a Docker Container
  - docker exec -it host bash
  - docker exec -it receiver bash
