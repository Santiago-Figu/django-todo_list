# django-todo_list
Implementa una API REST utilizando Django Rest Framework (DRF) para gestionar una lista de tareas (ToDo).


# Crear el directorio del proyecto (opcional)
mkdir django-todo_list
cd django-todo_list

# Crear el entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
 venv\Scripts\activate   # Windows

# Instalar Django y dependencias iniciales
pip install 
django 
django-rest-framework
python-dotenv
psycopg2-binary
pycryptodome
pyjwt 
cryptography

# Run
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000

# Admin
jose_admin | jose@algo.com | meoi1234
admin_test | admin_test@outlook.com | meoi1234