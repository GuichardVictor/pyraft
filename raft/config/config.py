import json
import jsonschema

class Config:

    config_schema = {
        "cluster": [
            {
                "ip": {"type": "string"},
                "port": {"type": "number"}
            }
        ]
    }

    def __init__(self):
        self.cluster = None

    def _validate_schema(self, jsondata):
        try:
            jsonschema.validate(jsondata, Config.config_schema)
        except jsonschema.exceptions.ValidationError as err:
            raise err

    def _update(self, data):
        self._validate_schema(data)
        self.cluster = list(map(lambda x: (x["ip"], x["port"]), data['cluster']))

    def parse_config_from_file(self, inputfile):
        data = None
        with open(inputfile) as f:
            data = json.load(f)
        
        self._update(data)

    def parse_config(self, data):
        self._update(data)