from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import engine, Base

from auth import router as auth_router
from chat import router as chat_router

from dotenv import load_dotenv


load_dotenv()



# -------------------------
# Database Startup
# -------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting application...")

    # Create SQLite tables
    Base.metadata.create_all(
        bind=engine
    )

    print("Database initialized")

    yield

    print("Application shutdown")





# -------------------------
# FastAPI App
# -------------------------

app = FastAPI(

    title="Women's Health AI Assistant",

    description=(
        "Secure RAG based healthcare "
        "information assistant"
    ),

    version="1.0.0",

    lifespan=lifespan

)





# -------------------------
# React CORS
# -------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:5174",

       

    ],

    allow_credentials=True,

    allow_methods=[

        "*"

    ],

    allow_headers=[

        "*"

    ],

)





# -------------------------
# API Routes
# -------------------------

app.include_router(

    auth_router,

    prefix="/auth",

    tags=["Authentication"]

)



app.include_router(

    chat_router,

    prefix="/chat",

    tags=["Chat"]

)





# -------------------------
# Health Routes
# -------------------------

@app.get("/")
def home():

    return {

        "message":
        "Women's Health AI API running",

        "status":
        "active"

    }





@app.get("/health")
def health_check():

    return {

        "api":
        "working",

        "database":
        "connected"

    }