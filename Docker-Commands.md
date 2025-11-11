# Setup
  - Install Docker Decktop: https://www.docker.com/products/docker-desktop
  - Install git if not installed: your_package_manager install git
  - Clone the GitHub repository to your local system: git clone https://github.com/AJAUDET/SecureDrop

  - Build Local Docker Image: docker build -t securedrop-docker_user_container .
  - Run Command: chmod +x launch_user.sh
  - Auto Login To Instance: ./launch_user.sh <username> <password> <email>
  - Auto Register New User: ./launch_user.sh --init
    - You will be prompted for a password and email

# Once inside container
  - You will be logged into an instance of securedrop and be fully registered
  - When you run ./launch_user.sh <username> <password> <email> it creates a new container for you and will automatically start broadcasting your presence
