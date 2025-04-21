from pydantic import BaseModel

class InstaSchema(BaseModel):
    url: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://www.instagram.com/example.uz/"
                }
            ]
        }
    }



class InstaStory(BaseModel):
    username: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "example.uz"
                }
            ]
        }
    }


# class ProxyServerFileSCHEMA(BaseModel):
#     file:



class YtSchema(BaseModel):
    url: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://youtu.be/2Rys8Udrlus?si=MBdCS5EV_y57811A"
                }
            ]
        }
    }



class TkSchema(BaseModel):
    url: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://vt.tiktok.com/ZSr9A2KyN/"
                }
            ]
        }
    }