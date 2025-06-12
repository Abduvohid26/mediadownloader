from pydantic import BaseModel
from typing import Optional

class PlatformBase(BaseModel):
    name: str
    base_url: str
    extra_link: Optional[str] = None
    hidden: Optional[bool] = False
    avatar: Optional[str] = None 

class PlatformCreate(PlatformBase):
    pass

class PlatformUpdate(PlatformBase):
    pass

class PlatformOut(PlatformBase):
    id: int

    model_config = {
        "from_attributes": True
    }
