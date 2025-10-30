# Setup
  - Install Docker Decktop: https://www.docker.com/products/docker-desktop
  - Install git if not installed: your_package_manager install git
  - Clone the GitHub repository to your local system: git clone https://github.com/AJAUDET/SecureDrop

  - Build Local Docker Image: docker build -t securedrop-docker_user_container .
  - Run Undefined Image Instance: ./launch_user.sh
  - Run Defined Image Instance: ./launch_user.sh <username>
  - Auto Login To Instance: ./launch_user.sh <username> <password>
