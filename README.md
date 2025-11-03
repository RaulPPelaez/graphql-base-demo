# GraphQL Base API - Backend Challenge

A Django-based GraphQL API that allows users to manage apps with a subscription plan system (Hobby/Pro).

## Features

- **GraphQL API** with Relay Node interface
- **Custom ID formats**: Users (`u_[a-Z0-9]+`) and Apps (`app_[a-Z0-9]+`)
- **DataLoaders** for efficient database queries (prevents N+1 problems)
- **Async support** throughout the business logic
- **Plan system**: Hobby and Pro plans with upgrade/downgrade mutations
- **ASGI** configuration for async operations

## Tech Stack

- Python ≥ 3.11
- Django 5.x
- Strawberry GraphQL (async)
- SQLite (default, configurable to PostgreSQL/MySQL)
- ASGI with Uvicorn
- pytest for testing

## Models

### User
- `id`: Custom format `u_[a-Z0-9]+`
- `username`: String (unique)
- `plan`: Enum (HOBBY or PRO)

### DeployedApp
- `id`: Custom format `app_[a-Z0-9]+`
- `owner`: ForeignKey to User
- `active`: Boolean

## Setup

### Install Dependencies

```bash
# Create a virtual environment with conda
conda env create
conda activate graphql-base-api
```

### Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Test Fixtures

```bash
python manage.py create_fixtures
```

This will create:
- 3 hobby users with 2 apps each
- 3 pro users with 3-5 apps each

### Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

### Run the Server

For instance, using Django's development server:

```bash
python manage.py runserver
```
## GraphQL Endpoint

Access the GraphQL interface at: http://localhost:8000/graphql

## Example Queries

### Get User by ID

```graphql
query getUser {
  node(id: "u_abcdefghijklmnop") {
    ... on User {
      id
      username
      plan
      apps {
        id
        active
      }
    }
  }
}
```

### Get App by ID

```graphql
query getApp {
  node(id: "app_abcdefghijklmnop") {
    ... on App {
      id
      active
      owner {
        id
        username
        plan
      }
    }
  }
}
```

### List All Users

```graphql
query getAllUsers {
  users {
    id
    username
    plan
    apps {
      id
      active
    }
  }
}
```

### List All Apps

```graphql
query getAllApps {
  apps {
    id
    active
    owner {
      id
      username
      plan
    }
  }
}
```

### Upgrade Account

```graphql
mutation upgradeUser {
  upgradeAccount(userId: "u_abcdefghijklmnop") {
    success
    message
    user {
      id
      username
      plan
    }
  }
}
```

### Downgrade Account

```graphql
mutation downgradeUser {
  downgradeAccount(userId: "u_abcdefghijklmnop") {
    success
    message
    user {
      id
      username
      plan
    }
  }
}
```

## Notes

### Getting Real IDs

After running `create_fixtures`, you can get real user and app IDs by:

1. Using the GraphQL interface to query all users/apps
2. Using Django admin at http://localhost:8000/admin
3. Using Django shell:

```bash
python manage.py shell
```

```python
from apps.users.models import User
from apps.deployedapps.models import DeployedApp

# Get all users
users = User.objects.all()
for user in users:
    print(f"{user.username}: {user.id}")

# Get all apps
apps = DeployedApp.objects.all()
for app in apps:
    print(f"{app.id} (Owner: {app.owner.username})")
```

### IDs

The GraphQL API returns IDs in their raw database format:
- User IDs: `u_[a-Z0-9]+` (e.g., `u_ky3kpR0Cv6GThnHxK`)
- App IDs: `app_[a-Z0-9]+` (e.g., `app_ttWn49RYCefdU0ick`)

These IDs can be used directly in the `node` query and mutations.

## Testing

### Run All Tests

```bash
# Run all tests with pytest
pytest -v

# Or using pytest
pytest
```
