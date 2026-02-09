"""
API Package
Combines all API routers into a single router.
"""
from fastapi import APIRouter
from app.api import auth, users, groups, participants, expenses, balances, mintsense

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(groups.router)
api_router.include_router(participants.router)
api_router.include_router(expenses.router)
api_router.include_router(balances.router)
api_router.include_router(mintsense.router)