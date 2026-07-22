from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from pydantic import BaseModel

from sqlalchemy.orm import Session

from database import get_db

from models import (
    User,
    Conversation,
    Message
)

from auth import get_current_user

from rag_chatbot import ask_question


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)



# =========================
# SCHEMAS
# =========================


class ChatRequest(BaseModel):

    conversation_id: int | None = None

    question: str



class NewConversationRequest(BaseModel):

    title: str = "New Conversation"





# =========================
# CREATE CONVERSATION
# =========================


@router.post("/conversation")
def create_conversation(

    data: NewConversationRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):


    conversation = Conversation(

        title=data.title,

        user_id=current_user.id

    )


    db.add(conversation)

    db.commit()

    db.refresh(conversation)



    return {

        "id": conversation.id,

        "title": conversation.title

    }





# =========================
# GET ALL CONVERSATIONS
# =========================


@router.get("/conversations")
def get_conversations(

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):


    conversations = (

        db.query(Conversation)

        .filter(
            Conversation.user_id == current_user.id
        )

        .order_by(
            Conversation.created_at.desc()
        )

        .all()

    )



    return [

        {

            "id": c.id,

            "title": c.title,

            "created_at": c.created_at

        }

        for c in conversations

    ]







# =========================
# LOAD CHAT HISTORY
# =========================


@router.get(
    "/conversation/{conversation_id}"
)

def get_chat_history(

    conversation_id:int,

    db:Session = Depends(get_db),

    current_user:User = Depends(get_current_user)

):


    conversation = (

        db.query(Conversation)

        .filter(

            Conversation.id == conversation_id,

            Conversation.user_id == current_user.id

        )

        .first()

    )



    if not conversation:

        raise HTTPException(

            status_code=404,

            detail="Conversation not found"

        )




    return [

        {

            "role":m.role,

            "content":m.content,

            "created_at":m.created_at

        }

        for m in conversation.messages

    ]







# =========================
# CHAT WITH AI
# =========================


@router.post("/")
def chat(

    data:ChatRequest,

    db:Session = Depends(get_db),

    current_user:User = Depends(get_current_user)

):



    if not data.question.strip():

        raise HTTPException(

            status_code=400,

            detail="Question cannot be empty"

        )





    # ---------------------
    # Create / Load Chat
    # ---------------------


    if data.conversation_id is None:



        conversation = Conversation(

            title=data.question[:50],

            user_id=current_user.id

        )


        db.add(conversation)

        db.commit()

        db.refresh(conversation)



    else:



        conversation=(

            db.query(Conversation)

            .filter(

                Conversation.id == data.conversation_id,

                Conversation.user_id == current_user.id

            )

            .first()

        )



        if not conversation:


            raise HTTPException(

                status_code=404,

                detail="Conversation not found"

            )







    # ---------------------
    # Save User Message
    # ---------------------


    user_message = Message(

        conversation_id=conversation.id,

        role="user",

        content=data.question

    )


    db.add(user_message)

    db.commit()






    # ---------------------
    # RAG RESPONSE
    # ---------------------


    try:


        answer = ask_question(
            data.question
        )


    except Exception as e:


        answer = (

            "Sorry 🌸 I am unable to answer right now."

        )

        print("RAG ERROR:",e)







    # ---------------------
    # Save AI Message
    # ---------------------


    ai_message = Message(

        conversation_id=conversation.id,

        role="assistant",

        content=answer

    )


    db.add(ai_message)

    db.commit()





    return {


        "conversation_id":

        conversation.id,


        "answer":

        answer


    }