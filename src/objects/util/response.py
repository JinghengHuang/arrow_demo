import json

class Response():
    def __init__(self, code, msg, result):
        self.code = code
        self.msg = msg
        self.result = result
        
    def to_json_str(self) -> str:
        return json.dumps(self)