from typing import List
from fastapi import APIRouter, HTTPException
from ..models import Group, User
from ..data import GROUPS


router = APIRouter()


@router.get("/", response_model=List[Group])
def list_groups():
    return GROUPS


@router.get("/{group_id}", response_model=Group)
def get_group(group_id: int):
    for group in GROUPS:
        if group.id == group_id:
            return group
    raise HTTPException(status_code=404, detail="Group not found")


@router.post("/", response_model=Group)
def create_group(name: str):
    new_id = max((g.id for g in GROUPS), default=0) + 1
    group = Group(
        id=new_id,
        name=name,
        members=[]
    )
    GROUPS.append(group)
    return group


@router.post("/{group_id}/join")
def join_group(group_id: int, user: User):
    for group in GROUPS:
        if group.id == group_id:
            if user not in group.members:
                group.members.append(user)
            return {"message": "Successfully joined group"}
    raise HTTPException(status_code=404, detail="Group not found")


@router.post("/{group_id}/leave")
def leave_group(group_id: int, user: User):
    for group in GROUPS:
        if group.id == group_id:
            if user in group.members:
                group.members.remove(user)
            return {"message": "Successfully left group"}
    raise HTTPException(status_code=404, detail="Group not found")
