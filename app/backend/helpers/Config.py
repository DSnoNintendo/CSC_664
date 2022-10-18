import io
import os
import json


class Config:
    def __init__(self, path):
        self.path = path
        self.file = self._open_or_create_file(path)

        self.params = self._config_to_dict(self.file)

    def set_config(self, k, v):
        self.params[k] = v
        self.save_file()

    def exists(self):
        if os.path.exists(self.path):
            return True
        return False

    def get_config(self, k):
        try:
            return self.params[k]
        except KeyError:
            return None

    def save_file(self):
        self.file.truncate(0)
        self.file.write(json.dumps(self.params))
        self._flush()

    def has_required_configs(self, configs):
        for c in configs:
            if not self.get_config(c):
                return False
        return True

    def _flush(self):
        self.file.close()
        self.file = self._open_or_create_file(self.path)
        self.params = self._config_to_dict(self.file)

    def _open_or_create_file(self, path):
        if self.exists():
            f = open(f"{path}", "r")
        else:
            f = open(f"{path}", "w+")
        return f

    def _config_to_dict(self, s):
        """
        :param s: config file plain text
        :return dict: config file as dictionary if file is populated; empty dict if not
        """
        try:
            return json.load(s)
        except json.decoder.JSONDecodeError:
            return dict()