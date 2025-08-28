from typing import Optional
from apps.core.models import Client

def get_client(email: str):
    try:
        client = Client.objects.get(email=email)
        return {
            "name": client.name,
            "description": client.description,
            "email": client.email,
        }
    except Client.DoesNotExist:
        return f"No client found with email '{email}'."

def add_client(name: str, description: str, email: str):
    if Client.objects.filter(email=email).exists():
        return f"Client with email '{email}' already exists."

    client = Client.objects.create(name=name, description=description, email=email)
    return f"Client '{client.name}' added successfully."

def update_client(
    email: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
):
    try:
        client = Client.objects.get(email=email)
    except Client.DoesNotExist:
        return f"No client found with email '{email}'."

    if name is not None:
        client.name = name
    if description is not None:
        client.description = description
    if email is not None:
        client.email = email

    client.save()
    return f"Client with email '{email}' updated successfully."

def delete_client(email: str):
    try:
        client = Client.objects.get(email=email)
        client.delete()
        return f"Client with email '{email}' deleted successfully."
    except Client.DoesNotExist:
        return f"No client found with email '{email}'."

def list_clients():
    clients = Client.objects.all()
    if not clients:
        return "There are currently no clients registered."
    return [{
        "name": c.name,
        "description": c.description,
        "email": c.email,
    } for c in clients]

# Map functions here
FUNCTION_MAP = {
    "get_client": get_client,
    "add_client": add_client,
    "update_client": update_client,
    "delete_client": delete_client,
    "list_clients": list_clients,
}