import json

def read_json(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)
    
def write_json(data, file_name, indent=4):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=indent)