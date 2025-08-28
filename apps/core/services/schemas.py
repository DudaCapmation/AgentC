from pydantic import BaseModel
from typing import Optional

class ListClientsParams(BaseModel):
    pass

class ListTeamMembersParams(BaseModel):
    pass

class GetTeamMemberParams(BaseModel):
    email: str

class AddTeamMemberParams(BaseModel):
    first_name: str
    last_name: str
    email: str
    country: str
    joined_on: Optional[str] = None  # YYYY-MM-DD

class UpdateTeamMemberParams(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    joined_on: Optional[str] = None

class DeleteTeamMemberParams(BaseModel):
    email: str

class GetClientParams(BaseModel):
    email: str

class AddClientParams(BaseModel):
    name: str
    description: str
    email: str

class UpdateClientParams(BaseModel):
    email: str
    name: Optional[str] = None
    description: Optional[str] = None

class DeleteClientParams(BaseModel):
    email: str

class SendEmailParams(BaseModel):
    to_email: str
    subject: str
    body: str

def get_schemas():
    return [
        {
            "type": "function",
            "name": "list_clients",
            "description": "Returns a list of all clients.",
            "parameters": ListClientsParams.model_json_schema()
        },
        {
            "type": "function",
            "name": "list_team_members",
            "description": "Returns a list of all team members.",
            "parameters": ListTeamMembersParams.model_json_schema()
        },
        {
            "type": "function",
            "name": "get_team_member",
            "description": "Get details of a team member by email.",
            "parameters": GetTeamMemberParams.model_json_schema()
        },
        {
            "type": "function",
            "name": "add_team_member",
            "description": "Add a new team member.",
            "parameters": AddTeamMemberParams.model_json_schema()
        },
        {
            "type": "function",
            "name": "update_team_member",
            "description": "Update an existing team member.",
            "parameters": UpdateTeamMemberParams.model_json_schema()
        },
        {
            "type": "function",
            "name": "delete_team_member",
            "description": "Delete a team member by email.",
            "parameters": DeleteTeamMemberParams.model_json_schema()
        },
        {
            "type": "function",
            "name": "get_client",
            "description": "Get details of a client by email.",
            "parameters": GetClientParams.model_json_schema()
        },
        {
            "type": "function",
            "name": "add_client",
            "description": "Add a new client.",
            "parameters": AddClientParams.model_json_schema()
        },
        {
            "type": "function",
            "name": "update_client",
            "description": "Update an existing client.",
            "parameters": UpdateClientParams.model_json_schema()
        },
        {
            "type": "function",
            "name": "delete_client",
            "description": "Delete a client by email.",
            "parameters": DeleteClientParams.model_json_schema()
        },
        {
            "type": "function",
            "name": "send_email",
            "description": "Simulate sending an email.",
            "parameters": SendEmailParams.model_json_schema()
        },
    ]