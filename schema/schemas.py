from bson import ObjectId

def individual_serial(message) -> dict:
    return {
        "_id": str(message["_id"]),
        "from_id": message["from_id"],
        "to_id": message["to_id"],
        "body": message["body"],
        "attachment": message.get("attachment", None),  # Usar None como valor predeterminado
        "seen": message.get("seen", False),  # Usar False como valor predeterminado
        "created_at": message["created_at"],
        "updated_at": message["updated_at"],
        "__v": message.get("__v", 0)
    }

def list_serial(messages) -> list:
    return [individual_serial(message) for message in messages]
