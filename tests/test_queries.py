import pytest
from apps.users.models import User, PlanChoices
from apps.deployedapps.models import DeployedApp
from config.schema import schema


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_node_query_with_raw_user_id():
    """Test querying a user by raw ID using node interface"""
    # Create test user
    user = await User.objects.acreate(
        username="test_user_raw_id", plan=PlanChoices.HOBBY
    )

    query = f"""
    query {{
        node(id: "{user.id}") {{
            ... on User {{
                id
                username
                plan
            }}
        }}
    }}
    """
    result = await schema.execute(query)

    assert result.errors is None
    assert result.data is not None
    assert result.data["node"]["id"] == user.id
    assert result.data["node"]["username"] == "test_user_raw_id"
    assert result.data["node"]["plan"] == "HOBBY"
    # Verify ID format
    assert user.id.startswith("u_")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_node_query_with_raw_app_id():
    """Test querying an app by raw ID using node interface"""
    # Create test user and app
    user = await User.objects.acreate(
        username="test_user_for_app", plan=PlanChoices.PRO
    )
    app = await DeployedApp.objects.acreate(owner=user, active=True)

    query = f"""
    query {{
        node(id: "{app.id}") {{
            ... on App {{
                id
                active
            }}
        }}
    }}
    """
    result = await schema.execute(query)

    assert result.errors is None
    assert result.data is not None
    assert result.data["node"]["id"] == app.id
    assert result.data["node"]["active"] is True
    # Verify ID format
    assert app.id.startswith("app_")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_upgrade_account_with_raw_id():
    """Test upgrading an account using raw user ID"""
    user = await User.objects.acreate(
        username="test_upgrade_user", plan=PlanChoices.HOBBY
    )

    mutation = f"""
    mutation {{
        upgradeAccount(userId: "{user.id}") {{
            success
            message
            user {{
                username
                plan
            }}
        }}
    }}
    """
    result = await schema.execute(mutation)

    assert result.errors is None
    assert result.data is not None
    assert result.data["upgradeAccount"]["success"] is True
    assert result.data["upgradeAccount"]["user"]["plan"] == "PRO"

    # Verify in database
    user_refreshed = await User.objects.aget(id=user.id)
    assert user_refreshed.plan == PlanChoices.PRO


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_downgrade_account_with_raw_id():
    """Test downgrading an account using raw user ID"""
    user = await User.objects.acreate(
        username="test_downgrade_user", plan=PlanChoices.PRO
    )

    mutation = f"""
    mutation {{
        downgradeAccount(userId: "{user.id}") {{
            success
            message
            user {{
                username
                plan
            }}
        }}
    }}
    """
    result = await schema.execute(mutation)

    assert result.errors is None
    assert result.data is not None
    assert result.data["downgradeAccount"]["success"] is True
    assert result.data["downgradeAccount"]["user"]["plan"] == "HOBBY"

    # Verify in database
    user_refreshed = await User.objects.aget(id=user.id)
    assert user_refreshed.plan == PlanChoices.HOBBY


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_query_all_users_returns_raw_ids():
    """Test that querying all users returns raw IDs"""
    user1 = await User.objects.acreate(username="user1", plan=PlanChoices.HOBBY)
    user2 = await User.objects.acreate(username="user2", plan=PlanChoices.PRO)

    query = """
    query {
        users {
            id
            username
            plan
        }
    }
    """
    result = await schema.execute(query)

    assert result.errors is None
    assert result.data is not None
    assert len(result.data["users"]) >= 2

    # Verify all IDs
    for user in result.data["users"]:
        assert user["id"].startswith("u_"), f"Expected raw ID format, got {user['id']}"
        assert len(user["id"]) > 2  # Should be more than just "u_"
