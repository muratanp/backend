
def jsonrpc_success(result, id=1):
    return {
        "jsonrpc": "2.0",
        "result": result,
        "id": id
    }

def jsonrpc_error(message: str, code: int = -32603, id=1):
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": code,
            "message": message
        },
        "id": id
    }

# Standard JSON-RPC errors
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INTERNAL_ERROR = -32603
