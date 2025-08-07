# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
#
# from routes.auth import auth
# from routes.users import user_router
# from routes.nationality import nationality_router
#
# app = FastAPI(
#     title="Reception Kiosk API",
#     version="1.0.0",
#     description="API for managing walk-in guest data and admin login"
# )
#
# # Enable CORS (for frontend communication)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Replace "*" with actual frontend domain in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Register routers
# app.include_router(auth, prefix="/auth")
# app.include_router(user_router, prefix="/users")
# app.include_router(nationality_router,  prefix="/nationalities")


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import auth
from routes.users import user_router
from routes.nationality import nationality_router
from routes.client_menu import client_menu_router

# Initialize FastAPI app
app = FastAPI(
    title="Reception Kiosk API",
    version="1.0.0",
    description="API for managing walk-in guest data and admin login"
)

# Initialize rate limiter


# Enable CORS (restrict origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth, prefix="/auth")
app.include_router(user_router, prefix="/users")
app.include_router(nationality_router, prefix="/nationalities")
app.include_router(client_menu_router)
