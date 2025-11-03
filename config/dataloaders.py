from strawberry.dataloader import DataLoader
from apps.users.models import User
from apps.deployedapps.models import DeployedApp


async def load_users(keys):
    users = {user.id: user async for user in User.objects.filter(id__in=keys)}
    return [users.get(key) for key in keys]


async def load_apps_by_owner(keys):
    apps_by_owner = {}
    async for app in DeployedApp.objects.filter(owner_id__in=keys):
        owner_id = app.owner_id  # type: ignore
        apps_by_owner.setdefault(owner_id, []).append(app)
    return [apps_by_owner.get(key, []) for key in keys]


user_loader = DataLoader(load_fn=load_users)
apps_by_owner_loader = DataLoader(load_fn=load_apps_by_owner)
