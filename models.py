from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Date,
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


    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )


    period_cycle = relationship(
        "PeriodCycle",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


    period_history = relationship(
        "PeriodHistory",
        back_populates="user",
        cascade="all, delete-orphan"
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


    user = relationship(
        "User",
        back_populates="conversations"
    )


    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
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





# -------------------------
# Current Period Cycle
# -------------------------

class PeriodCycle(Base):

    __tablename__ = "period_cycles"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True
    )


    last_period = Column(
        Date
    )


    cycle_length = Column(
        Integer,
        default=28
    )


    period_length = Column(
        Integer,
        default=5
    )


    user = relationship(
        "User",
        back_populates="period_cycle"
    )





# -------------------------
# Period History
# -------------------------

class PeriodHistory(Base):

    __tablename__ = "period_history"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )


    start_date = Column(
        Date,
        nullable=False
    )


    end_date = Column(
        Date,
        nullable=False
    )


    cycle_length = Column(
        Integer,
        default=28
    )


    period_length = Column(
        Integer,
        default=5
    )


    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


    user = relationship(
        "User",
        back_populates="period_history"
    )