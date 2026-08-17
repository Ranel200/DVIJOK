"""Tasks API used by the administrative frontend."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_feature, require_roles
from app.modules.tasks.schemas import (
    TaskBulkDelete,
    TaskCreate,
    TaskEmployee,
    TaskRead,
    TaskStatusUpdate,
    TaskSummary,
    TaskUpdate,
)
from app.modules.tasks.service import TaskService
from app.modules.users.models import User
from app.shared.enums import UserRole

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[
        Depends(require_feature("tasks", UserRole.ADMIN, UserRole.MANAGER, UserRole.MECHANIC))
    ],
)
manage = require_roles(UserRole.ADMIN, UserRole.MANAGER)


def get_task_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(get_current_user),
) -> TaskService:
    return TaskService(db, current_user)


@router.get("/summary", response_model=TaskSummary)
async def task_summary(
    service: TaskService = Depends(get_task_service),
) -> TaskSummary:
    return await service.summary()


@router.get("/employees", response_model=list[TaskEmployee])
async def task_employees(
    service: TaskService = Depends(get_task_service),
) -> list[TaskEmployee]:
    return await service.employees()


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    service: TaskService = Depends(get_task_service),
) -> list[TaskRead]:
    return await service.list()


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(manage)],
)
async def create_task(
    payload: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    return await service.create(payload)


@router.delete(
    "/bulk",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(manage)],
)
async def delete_tasks(
    payload: TaskBulkDelete,
    service: TaskService = Depends(get_task_service),
) -> None:
    await service.delete_many(payload.ids)


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    dependencies=[Depends(manage)],
)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    return await service.update(task_id, payload)


@router.patch("/{task_id}/status", response_model=TaskRead)
async def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    service: TaskService = Depends(get_task_service),
) -> TaskRead:
    return await service.update(task_id, TaskUpdate(status=payload.status))


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(manage)],
)
async def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
) -> None:
    await service.delete(task_id)
