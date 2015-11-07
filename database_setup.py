import sys

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    
    __tablename__ = 'user'
    
    name= Column( String(80), nullable = False)
    id = Column( Integer, primary_key = True)
    picture = Column( String(80))
    email = Column( String(80), nullable = False)

class Vocalband(Base):
    
    __tablename__ = 'vocalband'
    
    name = Column(String(30), nullable = False)
    id = Column(Integer, primary_key =True)
    
    @property
    def serialize(self):
        return {
            'id' :self.id,
            'name' : self.name,
        }
    
    
class Musicsheet(Base):
    
    __tablename__ = 'musicsheet'
    
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    vocalband_id = Column(Integer, ForeignKey('vocalband.id'))
    needs_beatbox = Column(Boolean, nullable = False)
    vocal_part = Column(String(10), nullable = False)
    vocalband = relationship(Vocalband, single_parent=True, cascade="all, delete-orphan")
    
    @property
    def serialize(self):
        return {
            'id' :self.id,
            'name' : self.name,
            'vocalband_id' :self.vocalband_id,
            'needs_beatbox' : self.needs_beatbox,
            'vocal_part': self.vocal_part
        }
    
    
engine = create_engine('sqlite:///vocalbandmusic.db')
Base.metadata.create_all(engine)