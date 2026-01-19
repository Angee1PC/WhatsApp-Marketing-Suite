import uuid
import hashlib
import os
import json

class SecurityManager:
    def __init__(self):
        self.license_file = "license.key"

    def get_device_id(self):
        # Generate a unique ID based on MAC address
        mac_num = uuid.getnode()
        mac_str = ':'.join(("%012X" % mac_num)[i:i+2] for i in range(0, 12, 2))
        # Hash it to make it look cleaner
        return hashlib.md5(mac_str.encode()).hexdigest()[:8].upper()

    def generate_valid_key(self, device_id):
        # SIMPLE ALGORITHM FOR DEMO:
        # The key is "PRO-" + reversed device ID + a secret salt
        # You would keep this logic SECRET on your side (maybe a separate script generator)
        secret = "AUTO-WA-2026"
        raw = f"{device_id}-{secret}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12].upper()

    def validate_key(self, input_key):
        device_id = self.get_device_id()
        expected_key = self.generate_valid_key(device_id)
        return input_key.strip() == expected_key

    def save_license(self, key):
        with open(self.license_file, "w") as f:
            f.write(key)

    def load_license(self):
        if os.path.exists(self.license_file):
            with open(self.license_file, "r") as f:
                return f.read().strip()
        return None

if __name__ == "__main__":
    # Test script to generate keys for yourself
    sec = SecurityManager()
    dev_id = sec.get_device_id()
    print(f"Device ID: {dev_id}")
    print(f"Valid Key (GIVE THIS TO USER): {sec.generate_valid_key(dev_id)}")
