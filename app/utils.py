import base64

def encodeParam(param:dict) -> str:
    return base64.b64encode(str(param).encode()).decode()
    