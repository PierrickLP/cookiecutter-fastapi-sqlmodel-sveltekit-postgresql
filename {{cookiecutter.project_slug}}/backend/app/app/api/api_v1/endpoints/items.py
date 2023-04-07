from typing import Any, cast

from fastapi import APIRouter, HTTPException

from app import crud, models
from app.api import deps

router = APIRouter()


@router.get("/", response_model=list[models.ItemReadWithOwner])
async def read_items(
    db: deps.AsyncGetDbDep,
    *,
    current_user: deps.CurrentActiveUserDep,
    offset: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve items.
    """
    if crud.user.is_superuser(current_user):
        items = await crud.item.get_multi(db, offset=offset, limit=limit)
    else:
        items = await crud.item.get_multi_by_owner(
            db=db, owner_id=current_user.id, offset=offset, limit=limit
        )
    return items


@router.post("/", response_model=models.ItemReadWithOwner)
async def create_item(
    db: deps.AsyncGetDbDep,
    *,
    item_in: models.ItemCreate,
    current_user: deps.CurrentActiveUserDep,
) -> Any:
    """
    Create new item.
    """
    item = await crud.item.create_with_owner(
        db, obj_in=item_in, owner_id=cast(int, current_user.id)
    )
    return item


@router.get("/{id}", response_model=models.ItemReadWithOwner)
async def read_item(
    db: deps.AsyncGetDbDep,
    *,
    id: int,
    current_user: deps.CurrentActiveUserDep,
) -> Any:
    """
    Get item by ID.
    """
    item = await crud.item.get(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.patch("/{id}", response_model=models.ItemReadWithOwner)
async def update_item(
    db: deps.AsyncGetDbDep,
    *,
    id: int,
    item_in: models.ItemUpdate,
    current_user: deps.CurrentActiveUserDep,
) -> Any:
    """
    Update an item.
    """
    item = await read_item(db, id=id, current_user=current_user)
    item = await crud.item.update(db, db_obj=item, obj_in=item_in)
    return item


@router.delete("/{id}", response_model=models.ItemReadWithOwner)
async def delete_item(
    db: deps.AsyncGetDbDep,
    *,
    id: int,
    current_user: deps.CurrentActiveUserDep,
) -> Any:
    """
    Delete an item.
    """
    item = await read_item(db, id=id, current_user=current_user)
    item = await crud.item.remove(db, db_obj=item)
    return item
