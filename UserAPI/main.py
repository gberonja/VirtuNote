from fastapi import FastAPI
from routes.users import router as users_router


# App initialization
app = FastAPI()

# Include the users router
app.include_router(users_router, prefix="/users", tags=["Users"])
