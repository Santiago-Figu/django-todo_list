
# django-todo_list
Implementa una API REST simple en Django utilizando Django Rest Framework (DRF) para gestionar una lista de tareas (ToDo).
## Environment Variables

Para levantar este proyecto necesitas agregar las siguientes variables a tu **.env** file:

#### PostgreSQL
`DB_NAME=tu_database_name`

`DB_USER=tu_postgres_user`

`DB_PASSWORD=tu_admin_password`

`DB_HOST=tu_localhost`

`DB_PORT=5432`

`SCHEMA=tu_schema`

#### Django - Configuración
`DJANGO_SECRET_KEY = django-insecure-ied=9!iq1!*pv2%+x$tr)b+#ktzr7ii+jimd_(m_gw5o$s_w#9`

`ADMIN_PASSWORD=tu_password_admin`

#### Tokens y cifrado

> [!NOTE]
> Nota en los archivos jwt_utils.py y aes_cipher.py cuentas con funciones para generar tu FERNET_KEY y probar las funciones de cifrado

`SECRET_KEY=tu_secret_key`

`FERNET_KEY=CZnGcdN2AXxJiXtO2oifCVtbgnO9nUJQpP7yKiaV5t0=`
## Run Locally

Descarga el proyecto

```bash
    git clone https://github.com/Santiago-Figu/django-todo_list.git
    cd django-todo_list
```

> [!NOTE]
> Recuerda trabajar en la rama devel

```bash
    git checkout devel
```


Crear el entorno virtual (recomendado)

```bash
    python -m venv venv
```

Activa el entorno virtual (recomendado)

```bash
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate   # Windows
```

> [!NOTE]
> Recuerda actualizar tu pip install (recomendado)

```bash
    python.exe -m pip install --upgradepip
```

Instalar Django y dependencias iniciales

```bash
    pip install 

    django
    django-rest-framework 
    python-dotenv 
    psycopg2-binary
    pycryptodome
    pyjwt
    cryptography
    python-jose[cryptography]
    colorlog
```
> [!NOTE]
> Si lo prefieres puedes usar el archivo requirements.txt

Ejecuta las migraciones iniciales de Django

```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver 0.0.0.0:8000
```

> [!NOTE]
> Es importante crear un usuario en base de datos con las siguientes caracteristicas establecidas en el modelo **User** de la app **users**: 'name', 'lastname', 'username', 'password', 'email', 'cellphone', 'team'

```bash
    jose_admin | jose@algo.com | meoi1234
    admin_test | admin_test@outlook.com | meoi1234
```

Ejecuta el servidor

```bash
    python manage.py runserver 0.0.0.0:8080
```
## API Reference

#### Get all users

```http
  GET /api/users/
```

| Header    | Auth Type     | Description                |
| :-------- | :-------      | :------------------------- |
| `api_key` | `Bearer Token`| **Required**. Your API key |

#### Get user

```http
  GET /api/users/id/
```

| Header    | Auth Type     | Description                |
| :-------- | :-------      | :------------------------- |
| `api_key` | `Bearer Token`| **Required**. Your API key |

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `int`    | **Required**. Id of item to fetch |

#### Register user

```http
  POST /api/users/register/
```
| Header    | Auth Type     | Description                |
| :-------- | :-------      | :------------------------- |
| `api_key` | `Bearer Token`| **Required**. Your API key |

| Body data      | Type     | Description                             |
| :--------      | :------- | :--------------------------------       |
| `name`         | `string` | **Required**. username for registration |
| `lastname`     | `string` | **Required**. lastname for registration |
| `username`     | `string` | **Required**. username for registration |
| `email`        | `string` | **Required**. email for registration    |
| `password`     | `string` | **Required**. password for registration |
| `cellphone`    | `string` | **Required**. cellphone for registration|
| `team`         | `string` | **Required**. team to which the user belongs|

#### Update user

```http
  PUT /api/users/id/
```
| Header    | Auth Type     | Description                |
| :-------- | :-------      | :------------------------- |
| `api_key` | `Bearer Token`| **Required**. Your API key |

| Parameter | Type     | Description                         |
| :-------- | :------- | :--------------------------------   |
| `id`      | `int`    | **Required**. Id of item to update  |

| Body data      | Type     | Description                        |
| :--------      | :------- | :--------------------------------  |
| `name`         | `string` | new value for update               |
| `lastname`     | `string` | new value for update               |
| `username`     | `string` | new value for update               |
| `email`        | `string` | new value for update               |
| `cellphone`    | `string` | new value for update               |
| `team`         | `string` | new value for update               |

#### Change password

```http
  PUT /api/users/change-password/
```
| Header    | Auth Type     | Description                |
| :-------- | :-------      | :------------------------- |
| `api_key` | `Bearer Token`| **Required**. Your API key |


| Body data      | Type     | Description                        |
| :--------      | :------- | :--------------------------------  |
| `old_password` | `string` | old value                          |
| `new_password` | `string` | new value for update               |


#### Get tasks users

```http
  GET /api/tasks/
```

| Header    | Auth Type     | Description                |
| :-------- | :-------      | :------------------------- |
| `api_key` | `Bearer Token`| **Required**. Your API key |

#### Tasks register

```http
  POST /api/task/create/
```
| Header    | Auth Type     | Description                |
| :-------- | :-------      | :------------------------- |
| `api_key` | `Bearer Token`| **Required**. Your API key |

| Body data      | Type     | Description                        |
| :--------      | :------- | :--------------------------------  |
| `title`        | `string` | task title                         |
| `description`  | `string` | task description                   |
| `completed`    | `boolean`| boolean to indicate whether the task has been completed|
| `assigned_user`| `string` | user to whom the task is assigned  |

#### Get token

```http
  POST /api/login/
```

| Body data      | Type     | Description                        |
| :--------      | :------- | :--------------------------------  |
| `username`     | `string` | username of the registered user    |
| `password`     | `string` | password of the registered user    |

## Acknowledgements

 - [Awesome Readme Templates](https://awesomeopensource.com/project/elangosundar/awesome-README-templates)
 - [Awesome README](https://github.com/matiassingers/awesome-readme)
 - [How to write a Good readme](https://bulldogjob.com/news/449-how-to-write-a-good-readme-for-your-github-project)

- **Autor:** [Santiago Figueroa](https://github.com/Santiago-Figu)
- **Correo de contacto:** Sfigu@outlook.com
## Support

Para recibir soporte, contactar por email sfigu@outlook.com.


## Authors

- **Autor:** [Santiago Figueroa](https://github.com/Santiago-Figu)


## Feedback

If you have any feedback, please reach out to us at sfigu@outlook.com

