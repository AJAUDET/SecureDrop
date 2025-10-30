# Setup
  - Install Docker Decktop: https://www.docker.com/products/docker-desktop
  - Install git if not installed: your_package_manager install git
  - Clone the GitHub repository to your local system: git clone https://github.com/AJAUDET/SecureDrop

  - Build Local Docker Image: docker build -t securedrop-docker_user_container .
  - Run Undefined Image Instance: ./launch_user.sh
  - Run Defined Image Instance: ./launch_user.sh <username>
  - Auto Login To Instance: ./launch_user.sh <username> <password>

# Once inside container
  - You will be logged into a bash terminal
    - If you log in with no credentials
      - Use "python3 securedrop.py" to run the secure_drop app to register a user (one time process for registration fot this user)
    - If you login using only Username
      - Use "python3 securedrop.py" to run the secure_drop app to log in to this user (one time process for password creation if none found)
    - If you login using Username and Password
      - You will need to run "python3 securedrop.py" but then you will automatically connect into your securedrop.py instance without the need to verify login
