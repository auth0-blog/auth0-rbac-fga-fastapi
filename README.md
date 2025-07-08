# FastAPI OpenFGA RBAC Demo

This project demonstrates how to implement **Role-Based Access Control (RBAC)** using OpenFGA with FastAPI. It follows OpenFGA's best practices for coarse-grained access control, starting simple and building up complexity gradually.

## RBAC Model Overview

This demo implements a simple organizational RBAC pattern with:

- **Organizations**: Groups that contain users with specific roles
- **Users**: Individual actors with roles in organizations  
- **Resources**: Assets owned by organizations
- **Roles**: `admin` and `member` with different permission levels

## OpenFGA Model

```
type user

type organization
  relations
    define admin: [user]
    define member: [user]
    
    define can_add_member: admin
    define can_delete_member: admin
    define can_view_member: admin or member
    define can_add_resource: admin or member

type resource
  relations
    define organization: [organization]
    
    define can_delete_resource: admin from organization
    define can_view_resource: admin from organization or member from organization
```

## Key RBAC Concepts Demonstrated

### 1. **Direct Role Assignment**
- Users are directly assigned `admin` or `member` roles in organizations
- Simple, easy to understand and implement

### 2. **Permission Inheritance**
- Resource permissions inherit from organization roles
- Uses OpenFGA's `from` keyword to map organization roles to resource permissions
- `admin from organization` means "users who are admins of the organization that owns this resource"

### 3. **Coarse-Grained Access Control**
- Follows OpenFGA best practices by starting simple
- Two clear roles with distinct permission sets
- Easy to reason about and audit

## Permission Matrix

| Role | Add Members | Delete Members | View Members | Add Resources | Delete Resources | View Resources |
|------|-------------|----------------|--------------|---------------|------------------|----------------|
| **admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **member** | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |

## Project Structure

```
fastapi-openfga-project/
├── app/
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration settings
│   ├── models/
│   │   ├── organization.py      # Organization and member models
│   │   └── resource.py          # Resource models
│   ├── routes/
│   │   ├── organization_routes.py # Organization management endpoints
│   │   └── resource_routes.py   # Resource management endpoints
│   ├── services/
│   │   └── authorization_service.py # OpenFGA integration
│   ├── utils/
│   │   └── openfga_client.py    # OpenFGA client wrapper
│   └── openfga/
│       └── model.fga.yaml       # OpenFGA model definition
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Start OpenFGA Server**
   ```bash
   # Using Docker
   docker run --rm -p 8080:8080 openfga/openfga run
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenFGA server details
   ```

4. **Run the Application**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API**
   - API Documentation: http://127.0.0.1:8000/docs
   - RBAC Info: http://127.0.0.1:8000/rbac-info

## API Endpoints

### Organizations
- `GET /organizations` - List accessible organizations
- `POST /organizations` - Create organization (creator becomes admin)
- `GET /organizations/{id}` - Get organization details
- `PUT /organizations/{id}` - Update organization (admin only)
- `DELETE /organizations/{id}` - Delete organization (admin only)
- `POST /organizations/{id}/members` - Add member (admin only)
- `DELETE /organizations/{id}/members/{user_id}` - Remove member (admin only)

### Resources
- `GET /resources` - List accessible resources
- `POST /resources` - Create resource (admin or member)
- `GET /resources/{id}` - Get resource details
- `PUT /resources/{id}` - Update resource (admin only)
- `DELETE /resources/{id}` - Delete resource (admin only)
- `GET /resources/{id}/permissions` - Check user permissions on resource

## Example Usage Flow

1. **Create an Organization**
   ```bash
   curl -X POST "http://localhost:8000/organizations?user_id=alice" \
        -H "Content-Type: application/json" \
        -d '{"name": "Acme Corp", "description": "Example organization"}'
   ```

2. **Add a Member**
   ```bash
   curl -X POST "http://localhost:8000/organizations/{org_id}/members?user_id=alice" \
        -H "Content-Type: application/json" \
        -d '{"user_id": "bob", "role": "member", "organization_id": "{org_id}"}'
   ```

3. **Create a Resource**
   ```bash
   curl -X POST "http://localhost:8000/resources?user_id=bob" \
        -H "Content-Type: application/json" \
        -d '{"name": "Database Server", "resource_type": "database", "organization_id": "{org_id}"}'
   ```

4. **Check Permissions**
   ```bash
   curl "http://localhost:8000/resources/{resource_id}/permissions?user_id=bob"
   ```

## OpenFGA Best Practices Demonstrated

### 1. **Start with Coarse-Grained Access Control**
- Two simple roles instead of complex permission matrices
- Clear separation of responsibilities
- Easy to understand and implement

### 2. **Use Direct Relationships**
- Direct user-to-organization role assignments
- No complex role hierarchies initially
- Straightforward permission checks

### 3. **Leverage Permission Inheritance**
- Resources inherit permissions from their owning organization
- Reduces tuple complexity
- Maintains clear ownership model

### 4. **Model Real-World Concepts**
- Organizations as natural grouping mechanisms
- Resources as owned assets
- Roles that map to business responsibilities

## Benefits of This Approach

- **Simplicity**: Easy to understand and implement
- **Scalability**: Can be extended with more roles and permissions
- **Performance**: Efficient permission checks through inheritance
- **Auditability**: Clear permission trails through organization ownership
- **Maintainability**: Simple model reduces complexity

## Next Steps for Extension

This basic RBAC model can be extended by:

1. Adding more roles (e.g., `viewer`, `manager`)
2. Implementing resource-specific permissions
3. Adding hierarchical organizations
4. Implementing time-based access controls
5. Adding attribute-based access control (ABAC) elements

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
