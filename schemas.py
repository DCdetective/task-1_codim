from pydantic import BaseModel , EmailStr , ConfigDict

class UserCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr
    age: int
    date: str
    time: str
    
class UserResponse(UserCreate):
    id: int
    
    model_config = ConfigDict(from_attributes= True)