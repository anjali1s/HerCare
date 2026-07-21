from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base



# -------------------------
# Users Table
# -------------------------

class User(Base):

    __tablename__ = "users"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    name = Column(
        String(100),
        nullable=False
    )


    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )


    hashed_password = Column(
        String(255),
        nullable=False
    )


    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


    # One user can have many conversations
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete"
    )




# -------------------------
# Conversations Table
# -------------------------

class Conversation(Base):

    __tablename__ = "conversations"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    title = Column(
        String(255),
        default="New Conversation"
    )


    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )


    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


    # Relationship back to user
    user = relationship(
        "User",
        back_populates="conversations"
    )


    # One conversation has many messages
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete"
    )




# -------------------------
# Messages Table
# -------------------------

class Message(Base):

    __tablename__ = "messages"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False
    )


    role = Column(
        String(20),
        nullable=False
    )
    # values:
    # user
    # assistant


    content = Column(
        Text,
        nullable=False
    )


    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )