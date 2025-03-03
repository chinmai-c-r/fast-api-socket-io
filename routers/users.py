from fastapi import APIRouter, FastAPI
import httpx
import logging

router = APIRouter()

class Person :
    def __init__(self,name:str, age:int):
        self.name = name
        self.age = age


@router.get("/users/", tags=["users"])
async def read_users():
    url = "https://jsonplaceholder.typicode.com/users"


    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status() 
            return {"data": response.json(), "error": None}

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"data": None, "error": str(e)}  


@router.get("/user", tags=["users"])
def get_user():
    return Person("Chinmai", 25)