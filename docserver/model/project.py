from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class RepositoryVersion(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    status = Column(String)
    project = Column(Integer, ForeignKey("projects.id"))


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    git_uri = Column(String)
    minimum_version = Column(String)
    versions = relationship('RepositoryVersion')

