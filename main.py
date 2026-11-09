from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI()

# --- MODELOS (como los DTOs en Kotlin) ---
class AuthRequest(BaseModel):
    correo: str
    contrasena: str
    nombre: Optional[str] = None

class AuthResponse(BaseModel):
    token: str
    usuarioId: str

class Rutina(BaseModel):
    id: Optional[str] = None
    nombre: str
    grupoMuscular: str
    series: int
    repeticiones: int
    activa: bool
    fechaCreacion: Optional[str] = None

# --- BASE DE DATOS EN MEMORIA (Simulada) ---
users_db = {}
rutinas_db = {}

# --- ENDPOINTS DE AUTENTICACIÓN ---
@app.post("/register", response_model=AuthResponse)
def register(req: AuthRequest):
    if req.correo in users_db:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    user_id = str(uuid.uuid4())
    # Guardamos al usuario simulando una base de datos
    users_db[req.correo] = {"id": user_id, "pass": req.contrasena, "nombre": req.nombre}
    
    # Generamos un token falso pero funcional
    return AuthResponse(token=f"fake-jwt-{user_id}", usuarioId=user_id)

@app.post("/login", response_model=AuthResponse)
def login(req: AuthRequest):
    user = users_db.get(req.correo)
    if not user or user["pass"] != req.contrasena:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    return AuthResponse(token=f"fake-jwt-{user['id']}", usuarioId=user["id"])

# --- ENDPOINTS CRUD DE RUTINAS ---
@app.get("/rutinas", response_model=List[Rutina])
def get_rutinas():
    return list(rutinas_db.values())

@app.post("/rutinas", response_model=Rutina)
def create_rutina(rutina: Rutina):
    rutina.id = str(uuid.uuid4())
    if not rutina.fechaCreacion:
        rutina.fechaCreacion = datetime.now().strftime("%Y-%m-%d")
    rutinas_db[rutina.id] = rutina
    return rutina

@app.put("/rutinas/{id}", response_model=Rutina)
def update_rutina(id: str, rutina: Rutina):
    if id not in rutinas_db:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")
    rutina.id = id
    rutinas_db[id] = rutina
    return rutina

@app.delete("/rutinas/{id}")
def delete_rutina(id: str):
    if id in rutinas_db:
        del rutinas_db[id]
    return {"status": "ok"}