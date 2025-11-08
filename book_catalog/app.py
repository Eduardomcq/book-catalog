from fastapi import FastAPI

from book_catalog.routers import auth, livros, romancistas, usuario

app = FastAPI()

app.include_router(usuario.router)
app.include_router(auth.router)
app.include_router(livros.router)
app.include_router(romancistas.router)
