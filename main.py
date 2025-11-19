from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from fastapi.staticfiles import StaticFiles
from database import Base, engine, SessionLocal
from models import User
from schemas import UserCreate, UserResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/save", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/save", response_class=HTMLResponse)
def create_user(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    db: Session = Depends(get_db)
):

    # Check phone unique
    if db.query(User).filter(User.phone == phone).first():
        return templates.TemplateResponse("form.html", {
            "request": request,
            "error": "Phone number already exists!"
        })

    # Check email unique
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("form.html", {
            "request": request,
            "error": "Email already exists!"
        })

    # Save user
    new_user = User(
        name=name,
        phone=phone,
        email=email,
        age=age,
        date=date,
        time=time
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return templates.TemplateResponse("form.html", {
        "request": request,
        "success": f"User {name} saved successfully!"
    })
