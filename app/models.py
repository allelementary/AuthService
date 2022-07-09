from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text("gen_random_uuid()"))
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    api_key = Column(String, nullable=True)
    api_secret = Column(String, nullable=True)
    chat_id = Column(String, nullable=True)
    scopes = Column(ARRAY(String), nullable=True, server_default="{}")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
