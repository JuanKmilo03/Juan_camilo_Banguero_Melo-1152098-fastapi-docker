from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "usuario")
DB_PASSWORD = os.getenv("DB_PASS", "password123")
DB_NAME = os.getenv("DB_NAME", "notasdb")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# --- Modelo SQL ---
class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "¡Bienvenido a la API de notas!"}

@app.get("/notes")
def get_notes(db: Session = Depends(get_db)):
    try:
        notes = db.query(Note).all()
        return {"notes": [{"id": n.id, "title": n.title, "content": n.content} for n in notes]}
    except Exception:
        raise HTTPException(status_code=500, detail="Error al acceder a la base de datos")

@app.post("/notes")
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    try:
        new_note = Note(title=note.title, content=note.content)
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        return {"message": "Nota creada correctamente", "note": {"id": new_note.id, "title": new_note.title, "content": new_note.content}}
    except Exception:
        raise HTTPException(status_code=500, detail="Error al guardar la nota")

