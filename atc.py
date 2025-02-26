import random
import string
import os
import requests

# Replace with your actual GitHub links
GITHUB_KEYS_URL = "https://raw.githubusercontent.com/yourusername/yourrepo/main/approved_keys.txt"
GITHUB_SCRIPT_URL = "https://raw.githubusercontent.com/otherusername/otherrepo/main/script.py"  # Change this

# Path to store the generated key
KEY_FILE = "/sdcard/.atc-key.txt"
SCRIPT_FILE = "/sdcard/remote_script.py"

def generate_fixed_key():
    """Generate and store a fixed key if not already created."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return f.read().strip()  # Return the existing key

    key = f"{random.randint(10000, 99999)}-ATC-{random.randint(10000, 99999)}"

    with open(KEY_FILE, "w") as f:
        f.write(key)  # Save the key

    return key

def check_key_approval():
    """Check if the stored key is in the approved list from GitHub."""
    try:
        response = requests.get(GITHUB_KEYS_URL)
        if response.status_code == 200:
            approved_keys = response.text.splitlines()
            
            user_key = generate_fixed_key()  # Ensure we have a key
            
            if user_key in approved_keys:
                print(f"✅ Key Approved: {user_key}")
                return True
            else:
                print(f"❌ Key Not Approved: {user_key}")
                print("Request approval by contacting support.")
                return False
        else:
            print("❌ Failed to fetch approved keys. Check your internet connection.")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def download_and_run_script():
    """Download and execute the script from the external GitHub repo."""
    try:
        response = requests.get(GITHUB_SCRIPT_URL)
        if response.status_code == 200:
            with open(SCRIPT_FILE, "w") as f:
                f.write(response.text)
            
            print("✅ Script downloaded successfully. Running it now...")
            os.system(f"python {SCRIPT_FILE}")  # Run the script
        else:
            print("❌ Failed to download script. Check the GitHub URL.")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function to check key approval and run the script."""
    if check_key_approval():
        download_and_run_script()
    else:
        print("⛔ Access denied. Please get your key approved.")

# Run the script
main()
