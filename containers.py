#   Author: AJ Audet (AJAUDET)
#   Purpose: Automatic creation of instances for securedrop
#   ALT : lets us connect users over the docker network, in seperate instances not just locally

import os
import yaml
import subprocess

# Helper to run shell commands safely
def run_command(cmd, env=None, check=True, capture_output=False):
    """"""
    print(f"→ {' '.join(cmd)}")
    return subprocess.run(cmd, env=env, check=check, capture_output=capture_output, text=True)

# Return True if a container (running or stopped) exists
def container_exists(name):
    result = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}}"],
        capture_output=True, text=True, check=True
    )
    return name in result.stdout.splitlines()

# Return True if a container is currently running
def container_is_running(name):
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True, text=True, check=True
    )
    return name in result.stdout.splitlines()

# Restart an existing container (even if stopped)
def restart_container(name):
    print(f"Restarting container: {name}")
    subprocess.run(["docker", "start", "-a", name], check=True)

# Remove a stopped container before recreating
def remove_container(name):

    print(f"Removing old container: {name}")
    subprocess.run(["docker", "rm", "-f", name], check=True)


# Start or restart a SecureDrop user container
def start_user_container(user_id, user_name):

    env = os.environ.copy()
    env["USER_ID"] = str(user_id)
    env["USER_NAME"] = user_name

    container_name = f"securedrop-{user_name}"

    if container_exists(container_name):
        if container_is_running(container_name):
            print(f"Container '{container_name}' already running — restarting cleanly.")
            run_command(["docker", "restart", container_name])
        else:
            print(f"Container '{container_name}' exists but stopped — restarting.")
            restart_container(container_name)
        return

    # Create a fresh instance
    print(f"Creating new container for user '{user_name}' (ID: {user_id})")
    run_command([
        "docker", "compose",
        "run", "-d",
        "--name", container_name,
        "user-template"
    ], env=env)

def main():
    with open("users.yaml") as f:
        users = yaml.safe_load(f).get("users", [])

    if not users:
        print("No users found in users.yaml")
        return

    print("Starting SecureDrop user containers...")
    for user in users:
        user_id = user["id"]
        user_name = user["name"]
        start_user_container(user_id, user_name)

    print("\nAll user containers are now running or restarted successfully.")
