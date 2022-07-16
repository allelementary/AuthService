from sqlalchemy import Column, String, ARRAY
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text("gen_random_uuid()"))
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    scopes = Column(ARRAY(String), nullable=True, server_default="{}")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    def __repr__(self):
        return f"{self.__tablename__}{self.id}"
