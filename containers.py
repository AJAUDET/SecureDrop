#   Author: AJ Audet (AJAUDET)
#   Purpose: Automatic creation of instances for securedrop
#   ALT : lets us connect users over the docker network, in seperate instances not just locally

import subprocess
import yaml
import os
from pathlib import Path

# Run shell commands safely and print output
def run_command(cmd, env=None, check=True, capture_output=False):
    print(f"→ {' '.join(cmd)}")
    return subprocess.run(cmd, env=env, check=check, capture_output=capture_output, text=True)

# List running or all container names
def list_containers(all_containers=False):
    cmd = ["docker", "ps", "--format", "{{.Names}}"]
    if all_containers:
        cmd.insert(2, "-a")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return set(result.stdout.splitlines())

def container_exists(name):
    return name in list_containers(all_containers=True)

def container_is_running(name):
    return name in list_containers(all_containers=False)

# Pull latest SecureDrop code from GitHub
def update_repo(repo_dir="."):
    repo_path = Path(repo_dir)
    if not (repo_path / ".git").exists():
        print("📦 Cloning SecureDrop repository...")
        run_command(["git", "clone", "https://github.com/AJAUDET/SecureDrop.git", str(repo_path)])
    else:
        print("🔄 Pulling latest SecureDrop code...")
        run_command(["git", "-C", str(repo_path), "pull", "--rebase"])

# Rebuild Docker images for backend + user-template
def rebuild_images():
    print("\n⚙️ Rebuilding Docker images...")
    run_command(["docker", "compose", "build"])

# Start backend if not already running
def ensure_backend():
    print("\n🧠 Checking backend container...")
    if "securedrop-backend" not in list_containers(all_containers=True):
        print("🚀 Starting backend container...")
        run_command(["docker", "compose", "up", "-d", "backend"])
    elif not container_is_running("securedrop-backend"):
        print("♻️ Restarting stopped backend...")
        run_command(["docker", "start", "securedrop-backend"])
    else:
        print("✅ Backend already running.")

# Start or restart a SecureDrop user container
def start_user_container(user_id, user_name):
    env = os.environ.copy()
    env["USER_ID"] = str(user_id)
    env["USER_NAME"] = user_name
    container_name = f"securedrop-{user_name}"

    if container_exists(container_name):
        if container_is_running(container_name):
            print(f"✅ Container '{container_name}' already running — restarting cleanly.")
            run_command(["docker", "restart", container_name])
        else:
            print(f"♻️ Container '{container_name}' exists but stopped — restarting.")
            run_command(["docker", "start", container_name])
        return

    # Create a fresh instance
    print(f"🚀 Creating new container for user '{user_name}' (ID: {user_id})")
    run_command([
        "docker", "compose",
        "run", "-d",
        "--name", container_name,
        "user-template"
    ], env=env)

# Remove containers for users no longer in users.yaml
def remove_unused_containers(valid_users):
    print("\n🧹 Checking for stale user containers...")
    existing = list_containers(all_containers=True)
    for name in existing:
        if name.startswith("securedrop-") and name != "securedrop-backend":
            username = name.replace("securedrop-", "")
            if username not in valid_users:
                print(f"🗑️ Removing container for deleted user '{username}'")
                run_command(["docker", "rm", "-f", name])
    print("✅ Cleanup complete.")

def main():
    repo_dir = Path(".")
    update_repo(repo_dir)
    rebuild_images()

    # Load users.yaml
    with open(repo_dir / "users.yaml") as f:
        users = yaml.safe_load(f).get("users", [])

    if not users:
        print("⚠️ No users found in users.yaml.")
        return

    ensure_backend()

    valid_usernames = set(user["name"] for user in users)

    print("\n🔧 Syncing SecureDrop user containers...")
    for user in users:
        start_user_container(user["id"], user["name"])

    remove_unused_containers(valid_usernames)

    print("\n✅ All SecureDrop containers are now up-to-date with GitHub and users.yaml.")

if __name__ == "__main__":
    main()