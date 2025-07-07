# FastAPI OpenFGA Project

This project is a FastAPI application that implements a simple API to manage organizations, project managers, roles, and permissions. It utilizes the OpenFGA Python SDK for authorization checks based on a defined OpenFGA authorization model.

## Project Structure

```
fastapi-openfga-project
├── app
│   ├── main.py                  # Entry point of the FastAPI application
│   ├── models                   # Contains data models
│   │   ├── organization.py      # Organization model
│   │   ├── project_manager.py    # Project Manager model
│   │   ├── role.py              # Role model
│   │   └── permission.py         # Permission model
│   ├── routes                   # Contains API routes
│   │   ├── organization_routes.py # CRUD operations for organizations
│   │   ├── project_manager_routes.py # CRUD operations for project managers
│   │   ├── role_routes.py       # CRUD operations for roles
│   │   └── permission_routes.py  # CRUD operations for permissions
│   ├── services                 # Contains service classes
│   │   └── authorization_service.py # Handles authorization checks
│   └── utils                    # Utility functions
│       └── openfga_client.py    # OpenFGA client setup
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fastapi-openfga-project
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the FastAPI application:
   ```
   uvicorn app.main:app --reload
   ```

## Usage

Once the application is running, you can access the API documentation at `http://127.0.0.1:8000/docs`. This will provide you with an interactive interface to test the API endpoints.

## API Endpoints Overview

- **Organizations**
  - `GET /organizations`: Retrieve all organizations
  - `POST /organizations`: Create a new organization
  - `GET /organizations/{id}`: Retrieve a specific organization
  - `PUT /organizations/{id}`: Update a specific organization
  - `DELETE /organizations/{id}`: Delete a specific organization

- **Project Managers**
  - `GET /project-managers`: Retrieve all project managers
  - `POST /project-managers`: Create a new project manager
  - `GET /project-managers/{id}`: Retrieve a specific project manager
  - `PUT /project-managers/{id}`: Update a specific project manager
  - `DELETE /project-managers/{id}`: Delete a specific project manager

- **Roles**
  - `GET /roles`: Retrieve all roles
  - `POST /roles`: Create a new role
  - `GET /roles/{id}`: Retrieve a specific role
  - `PUT /roles/{id}`: Update a specific role
  - `DELETE /roles/{id}`: Delete a specific role

- **Permissions**
  - `GET /permissions`: Retrieve all permissions
  - `POST /permissions`: Create a new permission
  - `GET /permissions/{id}`: Retrieve a specific permission
  - `PUT /permissions/{id}`: Update a specific permission
  - `DELETE /permissions/{id}`: Delete a specific permission

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
