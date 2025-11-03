import strawberry
from strawberry import relay
from strawberry.types import Info
from typing import Optional, List, Union
from enum import Enum
from apps.users.models import User as UserModel, PlanChoices
from apps.deployedapps.models import DeployedApp as DeployedAppModel
from config.dataloaders import apps_by_owner_loader


@strawberry.enum
class Plan(Enum):
    HOBBY = "HOBBY"
    PRO = "PRO"


@strawberry.type
class User(relay.Node):
    id: strawberry.ID  # Use strawberry.ID for Relay compatibility
    username: str
    plan: Plan

    @classmethod
    def resolve_id(cls, root, info: Optional[Info] = None) -> str:
        """Return raw database ID in format u_[a-Z0-9]+"""
        if hasattr(root, "id"):
            return root.id
        return root

    @classmethod
    async def resolve_nodes(
        cls, *, info: Info, node_ids: List[str], required: bool = False
    ) -> List[Optional["User"]]:
        # node_ids are already raw IDs like u_xxx
        users = [user async for user in UserModel.objects.filter(id__in=node_ids)]
        users_dict = {u.id: cls.from_model(u) for u in users}
        return [users_dict.get(nid) for nid in node_ids]

    @strawberry.field
    async def apps(self) -> List["App"]:
        # Use raw ID directly
        user_id = self.id
        apps = await apps_by_owner_loader.load(user_id)
        return [App.from_model(app) for app in apps]

    @classmethod
    def from_model(cls, model: UserModel) -> "User":
        return cls(
            id=strawberry.ID(model.id),
            username=model.username,
            plan=getattr(Plan, model.plan),
        )


@strawberry.type
class App(relay.Node):
    id: strawberry.ID  # Use strawberry.ID for Relay compatibility
    active: bool

    @classmethod
    def resolve_id(cls, root, info: Optional[Info] = None) -> str:
        """Return raw database ID in format app_[a-Z0-9]+"""
        if hasattr(root, "id"):
            return root.id
        return root

    @classmethod
    async def resolve_nodes(
        cls, *, info: Info, node_ids: List[str], required: bool = False
    ) -> List[Optional["App"]]:
        # node_ids are already raw IDs like app_xxx
        apps = [app async for app in DeployedAppModel.objects.filter(id__in=node_ids)]
        apps_dict = {a.id: cls.from_model(a) for a in apps}
        return [apps_dict.get(nid) for nid in node_ids]

    @strawberry.field
    async def owner(self) -> User:
        # Use raw ID directly
        app_id = self.id
        app = [
            app
            async for app in DeployedAppModel.objects.select_related("owner").filter(
                id=app_id
            )
        ][0]
        return User.from_model(app.owner)

    @classmethod
    def from_model(cls, model: DeployedAppModel) -> "App":
        return cls(id=strawberry.ID(model.id), active=model.active)


@strawberry.type
class MutationPayload:
    user: Optional[User] = None
    success: bool = False
    message: str = ""


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def upgrade_account(self, user_id: str) -> MutationPayload:
        try:
            user = await UserModel.objects.aget(id=user_id)
            if user.plan == PlanChoices.PRO:
                return MutationPayload(
                    user=User.from_model(user),
                    success=False,
                    message="User is already on Pro plan",
                )
            user.plan = PlanChoices.PRO
            await user.asave()
            return MutationPayload(
                user=User.from_model(user),
                success=True,
                message="Account upgraded to Pro successfully",
            )
        except UserModel.DoesNotExist:
            return MutationPayload(
                success=False, message=f"User with id {user_id} not found"
            )

    @strawberry.mutation
    async def downgrade_account(self, user_id: str) -> MutationPayload:
        try:
            user = await UserModel.objects.aget(id=user_id)
            if user.plan == PlanChoices.HOBBY:
                return MutationPayload(
                    user=User.from_model(user),
                    success=False,
                    message="User is already on Hobby plan",
                )
            user.plan = PlanChoices.HOBBY
            await user.asave()
            return MutationPayload(
                user=User.from_model(user),
                success=True,
                message="Account downgraded to Hobby successfully",
            )
        except UserModel.DoesNotExist:
            return MutationPayload(
                success=False, message=f"User with id {user_id} not found"
            )


@strawberry.type
class Query:
    # Custom node resolver that accepts raw IDs
    @strawberry.field
    async def node(self, id: str) -> Optional[Union[User, App]]:
        """
        Resolve a node by raw ID (u_xxx or app_xxx).
        This implements the Relay Node interface without base64 encoding.
        """
        if id.startswith("u_"):
            try:
                user = await UserModel.objects.aget(id=id)
                return User.from_model(user)
            except UserModel.DoesNotExist:
                return None
        elif id.startswith("app_"):
            try:
                app = await DeployedAppModel.objects.aget(id=id)
                return App.from_model(app)
            except DeployedAppModel.DoesNotExist:
                return None
        return None

    @strawberry.field
    async def users(self) -> List[User]:
        return [User.from_model(u) async for u in UserModel.objects.all()]

    @strawberry.field
    async def apps(self) -> List[App]:
        return [App.from_model(a) async for a in DeployedAppModel.objects.all()]


schema = strawberry.Schema(query=Query, mutation=Mutation)
