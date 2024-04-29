import json


class Configuration:

    def __init__(self) -> None:
        self.config_path = "./config.json"
        self.config = None

        self.load_config()
    
    def load_config(self):
        with open(self.config_path, "r") as f:
            self.config = json.load(f)
        return self.config
    
    def __getitem__(self,a):
        return self.config[a]
    