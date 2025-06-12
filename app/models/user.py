from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, Text
from database.database import Base
from enum import Enum
from sqlalchemy_utils import ChoiceType
import datetime

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
    

    
    
class Download(Base):
    __tablename__ = "downloads"

    id = Column(String, primary_key=True, index=True)
    original_url = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


    def __repr__(self):
        return f"Download(original_url={self.original_url}, created_at={self.created_at})"


class Platform(Base):
    __tablename__ = "platforms"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(Text)
    base_url = Column(Text)
    extra_link = Column(Text)
    avatar = Column(Text)
    hidden = Column(Boolean, default=False)

    def __repr__(self):
        return f"Platform(name={self.name}, link={self.hidden})"