from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import engine, Base

from auth import router as auth_router
from chat import router as chat_router
from periods import router as period_router

from dotenv import load_dotenv

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import os


load_dotenv()


# =========================
# DATABASE STARTUP
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting application...")

    Base.metadata.create_all(
        bind=engine
    )

    print("Database initialized")

    yield

    print("Application shutdown")



# =========================
# FASTAPI APP
# =========================

app = FastAPI(

    title="Women's Health AI Assistant",

    description="Secure RAG based healthcare information assistant",

    version="1.0.0",

    lifespan=lifespan

)



# =========================
# CORS
# =========================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:5173",
        "http://localhost:5174"

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)



# =========================
# API ROUTES
# =========================
app.include_router(
    auth_router
)

app.include_router(
    chat_router
)


app.include_router(
    period_router
)



# =========================
# HEALTH CHECK
# =========================

@app.get("/")
def home():

    return {

        "message": "Women's Health AI API running",

        "status": "active"

    }



@app.get("/health")
def health():

    return {

        "api": "working",

        "database": "connected"

    }



# =========================
# REACT FRONTEND
# =========================

frontend_path = os.path.join(

    os.path.dirname(__file__),

    "frontend",

    "dist"

)



assets_path = os.path.join(

    frontend_path,

    "assets"

)



if os.path.exists(assets_path):

    app.mount(

        "/assets",

        StaticFiles(
            directory=assets_path
        ),

        name="assets"

    )




@app.get("/{full_path:path}")
def serve_react(full_path: str):


    file_path = os.path.join(

        frontend_path,

        full_path

    )


    if os.path.isfile(file_path):

        return FileResponse(file_path)



    return FileResponse(

        os.path.join(

            frontend_path,

            "index.html"

        )

    )