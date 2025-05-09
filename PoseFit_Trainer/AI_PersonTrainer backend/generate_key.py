#!/usr/bin/env python3
"""
Secret Key Generator for PoseFit API

This script generates a secure random secret key and updates the .env file.
Run it before deploying to production to ensure a secure application.
"""

import os
import secrets
import shutil
from pathlib import Path


def generate_secret_key(length=32):
    """Generate a secure random string of bytes in hex format."""
    return secrets.token_hex(length)


def update_env_file(secret_key):
    """Update or create .env file with the generated secret key."""
    env_path = Path(".env")
    env_example_path = Path("env.example")

    # If .env doesn't exist but env.example does, create from example
    if not env_path.exists() and env_example_path.exists():
        shutil.copy(env_example_path, env_path)
        print(f"Created .env file from env.example")

    # If .env still doesn't exist, create new file
    if not env_path.exists():
        with open(env_path, "w") as f:
            f.write(f"SECRET_KEY={secret_key}\n")
            f.write("ACCESS_TOKEN_EXPIRE_MINUTES=30\n")
        print(f"Created new .env file with SECRET_KEY")
        return

    # Read existing .env file
    with open(env_path, "r") as f:
        lines = f.readlines()

    # Check if SECRET_KEY exists in the file
    secret_key_exists = False
    for i, line in enumerate(lines):
        if line.startswith("SECRET_KEY="):
            lines[i] = f"SECRET_KEY={secret_key}\n"
            secret_key_exists = True
            break

    # If SECRET_KEY doesn't exist, add it
    if not secret_key_exists:
        lines.append(f"SECRET_KEY={secret_key}\n")

    # Write updated content back to .env file
    with open(env_path, "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    # Generate a secure secret key
    secret_key = generate_secret_key(32)

    # Update .env file
    update_env_file(secret_key)

    print(f"Generated new SECRET_KEY and updated .env file")
    print(f"Please restart the application for changes to take effect")
