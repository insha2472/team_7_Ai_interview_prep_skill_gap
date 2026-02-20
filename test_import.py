print("Testing imports...")
try:
    print("Importing FastAPI...")
    from fastapi import FastAPI
    print("Importing models...")
    import models
    print("Importing db...")
    from db import engine, Base, get_db
    print("Importing routers...")
    from routes.auth_routes import router as auth_router
    print("All core imports done!")
    
    app = FastAPI()
    app.include_router(auth_router)
    print("App created and router included!")
    
except Exception as e:
    print(f"Error during import: {e}")
