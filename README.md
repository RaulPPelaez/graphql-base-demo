# GraphQL Base API - Backend Challenge

A Django-based GraphQL API that allows users to manage apps with a subscription plan system (Hobby/Pro).

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
You can also use the Makefile:

```bash
make setup
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

## Testing

### Run All Tests

```bash
pytest -v
```
