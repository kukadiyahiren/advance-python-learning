from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from db import (create_user, get_all_users, get_user_by_id, 
                update_user, delete_user, create_role, get_all_roles,
                get_role_by_id, update_role, delete_role,
                create_student, get_all_students, get_student_by_id,
                update_student, delete_student)

app = FastAPI(title="User Management API", version="1.0.0")

# Security Configuration removed


# Enable CORS to allow Flask frontend to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models

# Role Models
class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None

class RoleUpdate(BaseModel):
    name: str
    description: Optional[str] = None

# User Models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: Optional[int] = 2  # Default to 'user' role

class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: Optional[datetime] = None
    role: Optional[RoleResponse] = None

    class Config:
        from_attributes = True

class UserDetailResponse(UserResponse):
    password: str

# Student Models
class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    course: str

class StudentUpdate(BaseModel):
    name: str
    email: EmailStr
    course: str

class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    course: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaginatedStudentResponse(BaseModel):
    items: List[StudentResponse]
    total: int
    page: int
    size: int
    pages: int

# API Endpoints

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "User Management API", "version": "1.0.0"}

# ===== TEST API ENDPOINTS =====

@app.get("/api/test/hello")
def test_hello():
    """Simple hello world test endpoint"""
    return {
        "message": "Hello from FastAPI!",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test/echo/{text}")
def test_echo(text: str):
    """Echo back the text you send"""
    return {
        "original": text,
        "reversed": text[::-1],
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "length": len(text)
    }

@app.post("/api/test/calculate")
def test_calculate(num1: float, num2: float, operation: str = "add"):
    """Simple calculator API"""
    operations = {
        "add": num1 + num2,
        "subtract": num1 - num2,
        "multiply": num1 * num2,
        "divide": num1 / num2 if num2 != 0 else "Cannot divide by zero"
    }
    
    if operation not in operations:
        raise HTTPException(status_code=400, detail="Invalid operation. Use: add, subtract, multiply, divide")
    
    return {
        "num1": num1,
        "num2": num2,
        "operation": operation,
        "result": operations[operation]
    }

@app.get("/api/test/status")
def test_status():
    """Check API and database status"""
    try:
        from db import get_db_connection
        conn = get_db_connection()
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "api_status": "running",
        "database_status": db_status,
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "users": "/api/users",
            "test_hello": "/api/test/hello",
            "test_echo": "/api/test/echo/{text}",
            "test_calculate": "/api/test/calculate",
            "test_status": "/api/test/status"
        }
    }

# ===== USER MANAGEMENT ENDPOINTS =====


@app.post("/api/users", response_model=dict, status_code=201)
def create_user_endpoint(user: UserCreate):
    """Create a new user"""
    created_at = datetime.now()
    updated_at = datetime.now()
    user_id = create_user(user.name, user.email, user.password, created_at, updated_at, user.role_id)
    if user_id:
        return {"success": True, "id": user_id, "message": "User created successfully"}
    else:
        raise HTTPException(status_code=400, detail="Name or Email already exists")

class PaginatedUserResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int

@app.get("/api/users", response_model=PaginatedUserResponse)
@app.get("/api/users", response_model=PaginatedUserResponse)
def get_users_endpoint(page: int = 1, size: int = 10):
    """Get all users with pagination"""
    data = get_all_users(page=page, page_size=size)
    
    total = data['total']
    pages = (total + size - 1) // size
    
    return {
        "items": data['users'],
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }

@app.get("/api/users/{user_id}", response_model=UserDetailResponse)
@app.get("/api/users/{user_id}", response_model=UserDetailResponse)
def get_user_endpoint(user_id: int):
    """Get user by ID"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{user_id}", response_model=dict)
@app.put("/api/users/{user_id}", response_model=dict)
def update_user_endpoint(user_id: int, user: UserUpdate):
    """Update user"""
    updated_at = datetime.now()
    success = update_user(user_id, user.name, user.email, user.password, updated_at, user.role_id)
    if success:
        return {"success": True, "message": "User updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Name or Email already exists or user not found")

@app.delete("/api/users/{user_id}", response_model=dict)
@app.delete("/api/users/{user_id}", response_model=dict)
def delete_user_endpoint(user_id: int):
    """Delete user"""
    success = delete_user(user_id)
    if success:
        return {"success": True, "message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

# ===== ROLE MANAGEMENT ENDPOINTS =====

@app.post("/api/roles", response_model=dict, status_code=201)
def create_role_endpoint(role: RoleCreate):
    """Create a new role"""
    role_id = create_role(role.name, role.description)
    if role_id:
        return {"success": True, "id": role_id, "message": "Role created successfully"}
    else:
        raise HTTPException(status_code=400, detail="Role name already exists")

@app.get("/api/roles", response_model=List[RoleResponse])
def get_roles_endpoint():
    """Get all roles"""
    roles = get_all_roles()
    return roles

@app.get("/api/roles/{role_id}", response_model=RoleResponse)
def get_role_endpoint(role_id: int):
    """Get role by ID"""
    role = get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@app.put("/api/roles/{role_id}", response_model=dict)
def update_role_endpoint(role_id: int, role: RoleUpdate):
    """Update role"""
    success = update_role(role_id, role.name, role.description)
    if success:
        return {"success": True, "message": "Role updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Role name already exists or role not found")

@app.delete("/api/roles/{role_id}", response_model=dict)
def delete_role_endpoint(role_id: int):
    """Delete role"""
    success = delete_role(role_id)
    if success:
        return {"success": True, "message": "Role deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Role not found")

# ===== STUDENT MANAGEMENT ENDPOINTS =====

@app.post("/api/students", response_model=dict, status_code=201)
@app.post("/api/students", response_model=dict, status_code=201)
def create_student_endpoint(student: StudentCreate):
    """Create a new student"""
    created_at = datetime.now()
    updated_at = datetime.now()
    student_id = create_student(student.name, student.email, student.course, created_at, updated_at)
    if student_id:
        return {"success": True, "id": student_id, "message": "Student created successfully"}
    else:
        raise HTTPException(status_code=400, detail="Email already exists")

@app.get("/api/students", response_model=PaginatedStudentResponse)
@app.get("/api/students", response_model=PaginatedStudentResponse)
def get_students_endpoint(page: int = 1, size: int = 10):
    """Get all students with pagination"""
    data = get_all_students(page=page, page_size=size)
    
    total = data['total']
    pages = (total + size - 1) // size
    
    return {
        "items": data['students'],
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }

@app.get("/api/students/{student_id}", response_model=StudentResponse)
@app.get("/api/students/{student_id}", response_model=StudentResponse)
def get_student_endpoint(student_id: int):
    """Get student by ID"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/api/students/{student_id}", response_model=dict)
@app.put("/api/students/{student_id}", response_model=dict)
def update_student_endpoint(student_id: int, student: StudentUpdate):
    """Update student"""
    updated_at = datetime.now()
    success = update_student(student_id, student.name, student.email, student.course, updated_at)
    if success:
        return {"success": True, "message": "Student updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Email already exists or student not found")

@app.delete("/api/students/{student_id}", response_model=dict)
@app.delete("/api/students/{student_id}", response_model=dict)
def delete_student_endpoint(student_id: int):
    """Delete student"""
    success = delete_student(student_id)
    if success:
        return {"success": True, "message": "Student deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Student not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
