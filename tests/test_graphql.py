import pytest
from django.test import TestCase
from apps.users.models import User, PlanChoices
from apps.deployedapps.models import DeployedApp
from config.schema import schema


@pytest.mark.asyncio
class GraphQLQueryTest(TestCase):
    """Test GraphQL queries"""

    async def asyncSetUp(self):
        """Set up test data"""
        self.hobby_user = await User.objects.acreate(
            username="hobbyuser", plan=PlanChoices.HOBBY
        )
        self.pro_user = await User.objects.acreate(
            username="prouser", plan=PlanChoices.PRO
        )
        self.app1 = await DeployedApp.objects.acreate(
            owner=self.hobby_user, active=True
        )
        self.app2 = await DeployedApp.objects.acreate(owner=self.pro_user, active=False)

    async def test_users_query(self):
        """Test querying all users"""
        await self.asyncSetUp()

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

        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)
        self.assertGreaterEqual(len(result.data["users"]), 2)

        usernames = [user["username"] for user in result.data["users"]]
        self.assertIn("hobbyuser", usernames)
        self.assertIn("prouser", usernames)

        # Ensure raw ID format (u_...)
        for u in result.data["users"]:
            self.assertTrue(u["id"].startswith("u_"), f"Expected raw ID, got {u['id']}")

    async def test_apps_query(self):
        """Test querying all apps"""
        await self.asyncSetUp()

        query = """
        query {
            apps {
                id
                active
            }
        }
        """

        result = await schema.execute(query)

        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)
        self.assertGreaterEqual(len(result.data["apps"]), 2)

    async def test_node_query_user(self):
        """Test querying a user by node ID"""
        await self.asyncSetUp()

        # Use raw ID directly (u_xxx format)
        node_id = self.hobby_user.id

        query = f"""
        query {{
            node(id: "{node_id}") {{
                ... on User {{
                    id
                    username
                    plan
                }}
            }}
        }}
        """

        result = await schema.execute(query)

        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)
        self.assertEqual(result.data["node"]["username"], "hobbyuser")
        self.assertEqual(result.data["node"]["plan"], "HOBBY")

    async def test_node_query_app(self):
        """Test querying an app by node ID"""
        await self.asyncSetUp()

        # Use raw ID directly (app_xxx format)
        node_id = self.app1.id

        query = f"""
        query {{
            node(id: "{node_id}") {{
                ... on App {{
                    id
                    active
                }}
            }}
        }}
        """

        result = await schema.execute(query)

        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)
        self.assertTrue(result.data["node"]["active"])

    async def test_user_apps_relationship(self):
        """Test querying user with their apps"""
        await self.asyncSetUp()

        query = """
        query {
            users {
                username
                apps {
                    id
                    active
                }
            }
        }
        """

        result = await schema.execute(query)

        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)

        # Find hobby user in results
        hobby_user_data = next(
            u for u in result.data["users"] if u["username"] == "hobbyuser"
        )
        self.assertEqual(len(hobby_user_data["apps"]), 1)


@pytest.mark.asyncio
class GraphQLMutationTest(TestCase):
    """Test GraphQL mutations"""

    async def asyncSetUp(self):
        """Set up test data"""
        self.user = await User.objects.acreate(
            username="testuser", plan=PlanChoices.HOBBY
        )

    async def test_upgrade_account(self):
        """Test upgrading an account to Pro"""
        await self.asyncSetUp()

        mutation = f"""
        mutation {{
            upgradeAccount(userId: "{self.user.id}") {{
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

        self.assertIsNone(result.errors)
        self.assertTrue(result.data["upgradeAccount"]["success"])
        self.assertEqual(result.data["upgradeAccount"]["user"]["plan"], "PRO")

        # Verify in database
        user = await User.objects.aget(id=self.user.id)
        self.assertEqual(user.plan, PlanChoices.PRO)

    async def test_upgrade_already_pro_account(self):
        """Test upgrading an account that is already Pro"""
        await self.asyncSetUp()

        # First upgrade
        self.user.plan = PlanChoices.PRO
        await self.user.asave()

        mutation = f"""
        mutation {{
            upgradeAccount(userId: "{self.user.id}") {{
                success
                message
            }}
        }}
        """

        result = await schema.execute(mutation)

        self.assertIsNone(result.errors)
        self.assertFalse(result.data["upgradeAccount"]["success"])
        self.assertIn("already on Pro", result.data["upgradeAccount"]["message"])

    async def test_downgrade_account(self):
        """Test downgrading an account to Hobby"""
        await self.asyncSetUp()

        # Start with Pro
        self.user.plan = PlanChoices.PRO
        await self.user.asave()

        mutation = f"""
        mutation {{
            downgradeAccount(userId: "{self.user.id}") {{
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

        self.assertIsNone(result.errors)
        self.assertTrue(result.data["downgradeAccount"]["success"])
        self.assertEqual(result.data["downgradeAccount"]["user"]["plan"], "HOBBY")

        # Verify in database
        user = await User.objects.aget(id=self.user.id)
        self.assertEqual(user.plan, PlanChoices.HOBBY)

    async def test_downgrade_already_hobby_account(self):
        """Test downgrading an account that is already Hobby"""
        await self.asyncSetUp()

        mutation = f"""
        mutation {{
            downgradeAccount(userId: "{self.user.id}") {{
                success
                message
            }}
        }}
        """

        result = await schema.execute(mutation)

        self.assertIsNone(result.errors)
        self.assertFalse(result.data["downgradeAccount"]["success"])
        self.assertIn("already on Hobby", result.data["downgradeAccount"]["message"])

    async def test_upgrade_nonexistent_user(self):
        """Test upgrading a user that doesn't exist"""
        mutation = """
        mutation {
            upgradeAccount(userId: "u_doesnotexist123") {
                success
                message
            }
        }
        """

        result = await schema.execute(mutation)

        self.assertIsNone(result.errors)
        self.assertFalse(result.data["upgradeAccount"]["success"])
        self.assertIn("not found", result.data["upgradeAccount"]["message"])
