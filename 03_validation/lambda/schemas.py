# ユーザー情報用のスキーマ
USER_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "age": {
            "type": "integer",
            "minimum": 0,
            "maximum": 150
        }
    },
    "required": ["name", "email"],
    "additionalProperties": True
}


# レスポンス用のスキーマ
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "statusCode": {
            "type": "integer",
            "maxLength": 3
        },
        "body": {
            "type": "object"
        }
    },
    "required": ["statusCode", "body"],
    "additionalProperties": False
}
