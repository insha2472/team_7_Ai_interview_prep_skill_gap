from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from db import engine
from models import Base

# Import all routers
from routes.auth_routes import router as auth_router
from routes.resume_routes import router as resume_router
from routes.analysis_routes import router as analysis_router
from routes.roadmap_routes import router as roadmap_router
from routes.test_routes import router as test_router
from routes.dashboard_routes import router as dashboard_router
from routes.voice_routes import router as voice_router
from routes.progress_routes import router as progress_router
from routes.gamification_routes import router as gamification_router

# --------------- App Initialisation ---------------
app = FastAPI(
    title="AI Interview Preparation Platform",
    description="Analyse skill gaps, generate roadmaps, and practise with mock tests.",
    version="1.0.0",
)

# --------------- CORS ---------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------- Include Routers ---------------
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(analysis_router)
app.include_router(roadmap_router)
app.include_router(test_router)
app.include_router(dashboard_router)
app.include_router(voice_router)
app.include_router(progress_router)
app.include_router(gamification_router)

# --------------- Create Tables ---------------
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def run_migrations():
    from fix_db import fix_schema
    print("Running startup migrations...")
    fix_schema()
    print("Startup migrations completed.")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Interview Preparation Platform!"}


@app.get("/demo", tags=["Root"])
def voice_demo():
    """Redirect to the voice chat demo page."""
    return RedirectResponse(url="/static/voice_demo.html")


# --------------- Static Files ---------------
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)