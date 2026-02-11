"""
Database operations using Django ORM.
This module replaces raw MySQL operations with Django's ORM.
"""

# Initialize Django before importing models
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_settings')
django.setup()

from models import Gallery, Category, User, Role, Student
from django.core.paginator import Paginator, EmptyPage

# ... (existing imports)

def get_all_users(page=1, page_size=10):
    """Get all users with role information using Django ORM and Paginator"""
    queryset = User.objects.select_related('role').all().order_by('-created_at')
    paginator = Paginator(queryset, page_size)
    
    try:
        users_page = paginator.page(page)
        users = users_page.object_list
    except EmptyPage:
        users = []
    except Exception:
         users = []

    # Transform the data to include role as nested object
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at,
            'role': {
                'id': user.role.id,
                'name': user.role.name,
                'description': user.role.description
            } if user.role else None
        })
    return {'users': result, 'total': paginator.count}


# Database Configuration (kept for reference, now in django_settings.py)
DB_CONFIG = {
    'user': 'laravel',
    'password': 'password',
    'host': '127.0.0.1',
    'database': 'laravel',
    'raise_on_warnings': False
}


def init_db():
    """
    Initialize database tables.
    With Django ORM and managed=False, tables are expected to exist.
    This function now just ensures categories and roles are seeded.
    """
    # Seed Categories if they don't exist
    categories = ['General', 'Hair Style']
    for cat_name in categories:
        Category.objects.get_or_create(name=cat_name)
    
    # Seed Roles if they don't exist
    roles = [
        ('admin', 'Administrator with full access'),
        ('user', 'Standard user with basic access'),
        ('moderator', 'Moderator with elevated permissions')
    ]
    for role_name, role_desc in roles:
        Role.objects.get_or_create(name=role_name, defaults={'description': role_desc})



# ===== GALLERY FUNCTIONS =====

def save_gallery_item(filename, text, timestamp, category_id=1):
    """Save a gallery item to database using Django ORM"""
    # Convert string timestamp to datetime if needed
    if isinstance(timestamp, str):
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    
    gallery_item = Gallery.objects.create(
        filename=filename,
        text=text,
        timestamp=timestamp,
        category_id=category_id
    )
    return gallery_item.id


def get_gallery_items():
    """Get all gallery items using Django ORM"""
    items = Gallery.objects.all().values(
        'id', 'filename', 'text', 'timestamp', 'category_id'
    )
    # Convert QuerySet to list of dicts for compatibility
    return list(items)


def get_gallery_count():
    """Get count of gallery items using Django ORM"""
    return Gallery.objects.count()


def delete_gallery_item(item_id):
    """Delete a gallery item by ID using Django ORM"""
    try:
        item = Gallery.objects.get(id=item_id)
        filename = item.filename
        item.delete()
        return filename
    except Gallery.DoesNotExist:
        return None


# ===== USER FUNCTIONS =====

def create_user(name, email, password, created_at=None, updated_at=None, role_id=None):
    """Create a new user using Django ORM"""
    # Set default timestamps if not provided
    if created_at is None:
        created_at = timezone.now()
    if updated_at is None:
        updated_at = timezone.now()
    # Default to 'user' role if not specified
    if role_id is None:
        role_id = 2
    
    try:
        user = User.objects.create(
            name=name,
            email=email,
            password=password,
            role_id=role_id,
            created_at=created_at,
            updated_at=updated_at
        )
        return user.id
    except IntegrityError:
        return None


def get_all_users(page=1, page_size=10):
    """Get all users with role information using Django ORM and Paginator"""
    queryset = User.objects.select_related('role').all().order_by('-created_at')
    paginator = Paginator(queryset, page_size)
    
    try:
        users_page = paginator.page(page)
        users = users_page.object_list
    except EmptyPage:
        users = []
    except Exception:
         users = []

    # Transform the data to include role as nested object
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at,
            'role': {
                'id': user.role.id,
                'name': user.role.name,
                'description': user.role.description
            } if user.role else None
        })
    return {'users': result, 'total': paginator.count}


def get_user_by_id(user_id):
    """Get user by ID with role information using Django ORM"""
    try:
        user = User.objects.select_related('role').filter(id=user_id).values(
            'id', 'name', 'email', 'password', 'created_at', 'role_id', 'role__name', 'role__description'
        ).first()
        
        if user:
            return {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'password': user['password'],
                'created_at': user['created_at'],
                'role': {
                    'id': user['role_id'],
                    'name': user['role__name'],
                    'description': user['role__description']
                } if user['role_id'] else None
            }
        return None
    except User.DoesNotExist:
        return None


def update_user(user_id, name, email, password, updated_at=None, role_id=None):
    """Update user information using Django ORM"""
    # Set default timestamp if not provided
    if updated_at is None:
        updated_at = timezone.now()
    
    try:
        update_data = {
            'name': name,
            'email': email,
            'password': password,
            'updated_at': updated_at
        }
        
        # Only update role_id if provided
        if role_id is not None:
            update_data['role_id'] = role_id
        
        updated_count = User.objects.filter(id=user_id).update(**update_data)
        return updated_count > 0
    except IntegrityError:
        return False


def delete_user(user_id):
    """Delete a user by ID using Django ORM"""
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return True
    except User.DoesNotExist:
        return False


# ===== ROLE FUNCTIONS =====

def create_role(name, description=None):
    """Create a new role using Django ORM"""
    try:
        role = Role.objects.create(
            name=name,
            description=description
        )
        return role.id
    except IntegrityError:
        return None


def get_all_roles():
    """Get all roles using Django ORM"""
    roles = Role.objects.all().values('id', 'name', 'description')
    return list(roles)


def get_role_by_id(role_id):
    """Get role by ID using Django ORM"""
    try:
        role = Role.objects.filter(id=role_id).values(
            'id', 'name', 'description'
        ).first()
        return role
    except Role.DoesNotExist:
        return None


def update_role(role_id, name, description=None):
    """Update role information using Django ORM"""
    try:
        updated_count = Role.objects.filter(id=role_id).update(
            name=name,
            description=description
        )
        return updated_count > 0
    except IntegrityError:
        return False


def delete_role(role_id):
    """Delete a role by ID using Django ORM"""
    try:
        role = Role.objects.get(id=role_id)
        role.delete()
        return True
    except Role.DoesNotExist:
        return False


def get_categories():
    """Get all categories using Django ORM"""
    categories = Category.objects.all().values('id', 'name')
    return list(categories)


# ===== STUDENT FUNCTIONS =====

def create_student(name, email, course, created_at=None, updated_at=None):
    """Create a new student using Django ORM"""
    if created_at is None:
        created_at = timezone.now()
    if updated_at is None:
        updated_at = timezone.now()
    
    try:
        student = Student.objects.create(
            name=name,
            email=email,
            course=course,
            created_at=created_at,
            updated_at=updated_at
        )
        return student.id
    except IntegrityError:
        return None


def get_all_students(page=1, page_size=10):
    """Get all students using Django ORM and Paginator"""
    queryset = Student.objects.all().order_by('-created_at')
    paginator = Paginator(queryset, page_size)
    
    try:
        students_page = paginator.page(page)
        students = students_page.object_list
    except EmptyPage:
        students = []
    except Exception:
        students = []

    result = []
    for student in students:
        result.append({
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'course': student.course,
            'created_at': student.created_at
        })
    return {'students': result, 'total': paginator.count}


def get_student_by_id(student_id):
    """Get student by ID using Django ORM"""
    try:
        student = Student.objects.get(id=student_id)
        return {
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'course': student.course,
            'created_at': student.created_at
        }
    except Student.DoesNotExist:
        return None


def update_student(student_id, name, email, course, updated_at=None):
    """Update student information using Django ORM"""
    if updated_at is None:
        updated_at = timezone.now()
    
    try:
        updated_count = Student.objects.filter(id=student_id).update(
            name=name,
            email=email,
            course=course,
            updated_at=updated_at
        )
        return updated_count > 0
    except IntegrityError:
        return False


def delete_student(student_id):
    """Delete a student by ID using Django ORM"""
    try:
        student = Student.objects.get(id=student_id)
        student.delete()
        return True
    except Student.DoesNotExist:
        return False


def get_student_count():
    """Get total count of students using Django ORM"""
    return Student.objects.count()


def get_user_count():
    """Get total count of users using Django ORM"""
    return User.objects.count()
