from fastapi import APIRouter, HTTPException, status
from models.message import Message
from config.database import collection_name
from schema.schemas import list_serial, individual_serial
from bson import ObjectId
from typing import List
from datetime import datetime
import json
from json import JSONDecodeError

router = APIRouter()

# POST /message/add
@router.post("/message/add", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_message(message: Message):
    new_message = message.dict()
    new_message["created_at"] = datetime.now().isoformat()
    new_message["updated_at"] = datetime.now().isoformat()
    result = collection_name.insert_one(new_message)
    created_message = collection_name.find_one({"_id": result.inserted_id})
    return individual_serial(created_message)

# GET /getMessages
@router.get("/getMessages", response_model=List[dict])
async def get_messages():
    messages = list_serial(collection_name.find())
    return messages

# GET /fetchMessages/{authUserId}/{userId}
@router.get("/fetchMessages/{authUserId}/{userId}", response_model=List[dict])
async def fetch_messages(authUserId: int, userId: int):
    messages = list_serial(collection_name.find({
        "$or": [
            {"from_id": authUserId, "to_id": userId},
            {"from_id": userId, "to_id": authUserId}
        ]
    }))
    return messages

# GET /getSharedPhotos/{userId}
@router.get("/getSharedPhotos/{userId}", response_model=List[str])
async def get_shared_photos(userId: int):
    try:
        # Consulta a MongoDB para obtener los mensajes enviados o recibidos por el usuario
        messages = collection_name.find({
            "$or": [
                {"from_id": userId},
                {"to_id": userId}
            ]
        })
        
        photos = []
        for message in messages:
            attachment = message.get("attachment")
            if attachment:
                try:
                    parsed_attachment = json.loads(attachment)
                    if parsed_attachment.get("new_name"):
                        photos.append(parsed_attachment["new_name"])
                except JSONDecodeError:
                    # Ignorar si el attachment no es un JSON válido
                    pass
        
        return photos
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# GET /getLastMessage/{authUserId}/{userId}
@router.get("/getLastMessage/{authUserId}/{userId}", response_model=dict)
async def get_last_message(authUserId: int, userId: int):
    messages = list(collection_name.find({
        "$or": [
            {"from_id": authUserId, "to_id": userId},
            {"from_id": userId, "to_id": authUserId}
        ]
    }).sort("created_at", -1).limit(1))
    if messages:
        return individual_serial(messages[0])
    else:
        raise HTTPException(status_code=404, detail="Message not found")

# GET /countUnseenMessages/{authUserId}/{contactUserId}
@router.get("/countUnseenMessages/{authUserId}/{contactUserId}", response_model=dict)
async def count_unseen_messages(authUserId: int, contactUserId: int):
    unseen_messages_count = collection_name.count_documents({
        "from_id": contactUserId,
        "to_id": authUserId,
        "seen": False
    })
    return {"unseenMessagesCount": unseen_messages_count}

# PUT /messages/{authUserId}/{userId}/seen
@router.put("/messages/{authUserId}/{userId}/seen", response_model=dict)
async def make_seen(authUserId: int, userId: int):
    result = collection_name.update_many({
        "from_id": userId,
        "to_id": authUserId,
        "seen": False
    }, {
        "$set": {"seen": True}
    })
    if result.modified_count:
        return {"status": 1}
    else:
        raise HTTPException(status_code=500, detail="Error marking messages as seen")
    

@router.delete("/deleteMessage/{messageId}")
async def delete_message(messageId: str):
    try:
        # Verifica si el messageId es un ObjectId válido
        if not ObjectId.is_valid(messageId):
            raise HTTPException(status_code=400, detail="Invalid message ID format")

        # Intenta encontrar y eliminar el mensaje
        result = collection_name.find_one_and_delete({"_id": ObjectId(messageId)})
        
        if result:
            return {"message": "Mensaje eliminado exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar el mensaje")
