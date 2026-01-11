import json
import os
from app.path_utils import get_app_root

class ProfileManager:
    def __init__(self, profiles_dir=None):
        if profiles_dir is None:
            self.profiles_dir = os.path.join(get_app_root(), "profiles")
        else:
            self.profiles_dir = profiles_dir

        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)

    def save_profile(self, name, data):
        path = os.path.join(self.profiles_dir, f"{name}.json")
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_profile(self, name):
        path = os.path.join(self.profiles_dir, f"{name}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return None

    def list_profiles(self):
        if not os.path.exists(self.profiles_dir):
            return []
        return [f.replace(".json", "") for f in os.listdir(self.profiles_dir) if f.endswith(".json")]

    def delete_profile(self, name):
        path = os.path.join(self.profiles_dir, f"{name}.json")
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
