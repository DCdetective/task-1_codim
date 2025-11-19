from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from fastapi.staticfiles import StaticFiles
from database import Base, engine, SessionLocal
from models import User
from schemas import UserCreate, UserResponse
from fastapi.responses import RedirectResponse

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

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
    
    
@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin/login", response_class=HTMLResponse)
def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie(key="admin_auth", value="true")
        return response

    return templates.TemplateResponse("admin_login.html", {
        "request": request,
        "error": "Invalid username or password"
    })
    
    
    
    
def is_admin_authenticated(request: Request):
    return request.cookies.get("admin_auth") == "true"




@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):

    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    users = db.query(User).all()

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "users": users
    })
    
    


# ------------------------------------
# ADMIN LOGOUT
# ------------------------------------
@app.get("/admin/logout")
def admin_logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_auth")
    return response