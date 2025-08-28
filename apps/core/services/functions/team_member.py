from typing import Optional
from datetime import datetime
from apps.core.models import TeamMember

def get_team_member(email: str):
    try:
        member = TeamMember.objects.get(email=email)
        return {
            "first_name": member.first_name,
            "last_name": member.last_name,
            "email": member.email,
            "country": member.country,
            "joined_on": member.joined_on.isoformat() if member.joined_on else None,
        }
    except TeamMember.DoesNotExist:
        return f"No team member found with email '{email}'."

def add_team_member(
    first_name: str,
    last_name: str,
    email: str,
    country: str,
    joined_on: Optional[str] = None
):
    if TeamMember.objects.filter(email=email).exists():
        return f"Team member with email '{email}' already exists."

    joined_date = None
    if joined_on:
        try:
            joined_date = datetime.strptime(joined_on, "%Y-%m-%d").date()
        except ValueError:
            return "Invalid date format for joined_on. Use YYYY-MM-DD."

    member = TeamMember.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        country=country,
        joined_on=joined_date
    )
    return f"Team member '{member.first_name} {member.last_name}' added successfully."

def update_team_member(
    email: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    country: Optional[str] = None,
    joined_on: Optional[str] = None
):
    try:
        member = TeamMember.objects.get(email=email)
    except TeamMember.DoesNotExist:
        return f"No team member found with email '{email}'."

    if first_name is not None:
        member.first_name = first_name
    if last_name is not None:
        member.last_name = last_name
    if country is not None:
        member.country = country
    if joined_on is not None:
        try:
            member.joined_on = datetime.strptime(joined_on, "%Y-%m-%d").date()
        except ValueError:
            return "Invalid date format for joined_on. Use YYYY-MM-DD."

    member.save()
    return f"Team member with email '{email}' updated successfully."

def delete_team_member(email: str):
    try:
        member = TeamMember.objects.get(email=email)
        member.delete()
        return f"Team member with email '{email}' deleted successfully."
    except TeamMember.DoesNotExist:
        return f"No team member found with email '{email}'."

def list_team_members():
    members = TeamMember.objects.all()
    if not members:
        return "No team members registered yet."
    return [{
        "first_name": m.first_name,
        "last_name": m.last_name,
        "email": m.email,
        "country": m.country,
        "joined_on": m.joined_on.isoformat() if m.joined_on else None
    } for m in members]

# Map functions here
FUNCTION_MAP = {
    "get_team_member": get_team_member,
    "add_team_member": add_team_member,
    "update_team_member": update_team_member,
    "delete_team_member": delete_team_member,
    "list_team_members": list_team_members,
}
