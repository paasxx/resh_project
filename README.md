
# Account Management System API - Django Rest FrameWork


API REST Website based to manage accounts, create, delete, update and login. 


## Acknowledgements

- CRUD of a base of Users 
- API REST based website
- JWT token security with 10 minutes expiry time.
- Function Based View design.


## API Reference

#### Return User details, id, username, email, password (hashed)

```http
  GET /api-get-user/
```

| Parameter  | Type      | Description                       |
| :---------- | :--------- | :---------------------------------- |
| `api_key` | `string` | **Required**. Needs to be logged |

#### Return JWT Token for User

```http
  POST /api-login-user/
```

| Parameter  | Type      | Description                       |
| :---------- | :--------- | :---------------------------------- |
| `api_key` | `string` | **Required**. None |

#### Log out the User and delete the token.

```http
  POST/api-logout-user/
```

| Parameter  | Type      | Description                       |
| :---------- | :--------- | :---------------------------------- |
| `api_key` | `string` | **Required**. Needs to be logged. |

#### Update the password.

```http
  PUT /api-update-password-user/
```

| Parameter  | Type      | Description                       |
| :---------- | :--------- | :---------------------------------- |
| `api_key` | `string` | **Required**. Needs to be logged. |

#### Update the Email.

```http
  PUT /api-update-email-user/
```

| Parameter  | Type      | Description                       |
| :---------- | :--------- | :---------------------------------- |
| `api_key` | `string` | **Required**. Needs to be logged. |

#### Delete User Data

```http
  DELETE /api-delete-user/
```

| Parameter  | Type      | Description                       |
| :---------- | :--------- | :---------------------------------- |
| `api_key` | `string` | **Required**. Needs to be logged. |



## Tech Stack

**Front-end:** HTML, CSS, Bootstrap5, Javascript

**Back-end:** Python, Django


## Deployment

Clone the project

```bash
  git clone https://github.com/paasxx/resh_project.git
```

Enter the directory

```bash
  cd resh_project
```
Create a virtual Enviroment 
```bash
  python -m venv
```

Install requirements.txt

```bash
  pip install requirements.txt
```

Run server
```bash
  python manage.py runserver
```

