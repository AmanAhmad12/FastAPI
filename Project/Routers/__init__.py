from .Todo_Routers import todo_router
from .User_Routers import user_router

__all__ = ["todo_router","user_router"]
# docker exec -it postgres-db psql -U postgres -d tododb