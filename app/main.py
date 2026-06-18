from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.auth_dependency import get_current_user
from app.auth import LoginRequest, CreateUserRequest
from app.database import engine, get_db
from app.models import Base, User
from app.security import create_access_token
from fastapi import Header


app = FastAPI()
Base.metadata.create_all(bind=engine)
@app.get("/")
def root():
    return {
        "status": "running",
        "server": "DroneServer"
    }

@app.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if user.password != request.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
            "email": user.email,
            "role": user.role
        }
    )

    return {
        "success": True,
        "token": token,
        "role": user.role,
        "email": user.email
    }

@app.post("/users/create")
def create_user(
    request: CreateUserRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    user = User(
        email=request.email,
        password=request.password,
        role=request.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "id": user.id
    }
@app.get("/users")
def get_users(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403,detail="Admin only")
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "success": True
    }