# Setup
  - Install Docker Decktop: https://www.docker.com/products/docker-desktop
  - Install git if not installed: your_package_manager install git
  - Clone the GitHub repository to your local system: git clone https://github.com/AJAUDET/SecureDrop

  - Build Local Docker Image: docker build -t securedrop-docker_user_container .
  - Run Command: chmod +x launch_user.sh
  - Join the Swarm: docker swarm join --token SWMTKN-1-5oef7q60sv7ssor9ifydx96dc8e9sqswkttnux3i7f2earla82-1o9pkumw9ovow2qgg6p8v9pa1 192.168.65.3:2377
  - Auto Login To Instance: ./launch_user.sh <username> <password> <email>
  - Auto Register New User: ./launch_user.sh <username>
    - You will be prompted for a password and email
   - Auto Register New User: ./launch_user.sh <username> <password>
    - You will be prompted for an email

# Once inside container
  - You will be logged into an instance of securedrop and be fully registered
  - When you run ./launch_user.sh <username> <password> <email> it creates a new container for you and will automatically start broadcasting your presence
