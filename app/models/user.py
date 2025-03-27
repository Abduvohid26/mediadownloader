from sqlalchemy import Column, Integer, String, BigInteger, Boolean
from database.database import Base
from enum import Enum
from sqlalchemy_utils import ChoiceType

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)





class ProxyServers(Base):
    __tablename__ = "proxy_servers"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    proxy = Column(String(100), index=True)
    username = Column(String(100), index=True)
    password = Column(String(100), index=True)
    instagram = Column(Boolean, default=True)
    tiktok = Column(Boolean, default=True)
    youtube = Column(Boolean, default=True)
    


    def __repr__(self):
        return f"ProxyServers(proxy={self.proxy}, instagram={self.instagram}, tiktok={self.tiktok}, youtube={self.youtube}, username={self.username}, password={self.password})"
    

    
    
