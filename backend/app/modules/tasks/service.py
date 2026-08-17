"""Business logic and tenant isolation for staff tasks."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.modules.tasks.models import Task
from app.modules.tasks.schemas import (
    TaskCreate,
    TaskEmployee,
    TaskRead,
    TaskSummary,
    TaskTodaySummary,
    TaskUpdate,
)
from app.modules.users.models import User
from app.shared.enums import TaskStatus, UserRole

_ROLE_LABELS = {
    UserRole.ADMIN: "Администратор",
    UserRole.MANAGER: "Менеджер",
    UserRole.MECHANIC: "Мастер",
}


class TaskService:
    def __init__(self, session, current_user: User) -> None:
        self.session = session
        self.current_user = current_user
        self.organization_id = current_user.organization_id

    @staticmethod
    def _employee(user: User | None) -> TaskEmployee:
        if user is None:
            return TaskEmployee(id="all", name="Все сотрудники", role="")
        return TaskEmployee(
            id=user.id,
            name=user.full_name,
            role=_ROLE_LABELS[user.role],
        )

    def _read(self, task: Task) -> TaskRead:
        return TaskRead(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            deadline=task.deadline,
            employee=self._employee(task.assignee),
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    def _scope(self):
        conditions = [Task.organization_id == self.organization_id]
        if not self.current_user.is_owner:
            conditions.append(Task.assignee_id == self.current_user.id)
        return conditions

    async def employees(self) -> list[TaskEmployee]:
        users = list(
            (
                await self.session.execute(
                    select(User)
                    .where(
                        User.organization_id == self.organization_id,
                        User.is_active.is_(True),
                    )
                    .order_by(User.full_name)
                )
            )
            .scalars()
            .all()
        )
        return [self._employee(user) for user in users]

    async def list(self) -> list[TaskRead]:
        rows = list(
            (
                await self.session.execute(
                    select(Task)
                    .options(selectinload(Task.assignee))
                    .where(*self._scope())
                    .order_by(Task.id.desc())
                )
            )
            .scalars()
            .all()
        )
        return [self._read(task) for task in rows]

    async def _get(self, task_id: int) -> Task:
        task = (
            await self.session.execute(
                select(Task)
                .options(selectinload(Task.assignee))
                .where(Task.id == task_id, *self._scope())
            )
        ).scalar_one_or_none()
        if task is None:
            raise NotFoundError("Задача не найдена")
        return task

    async def _assignee_id(self, employee: TaskEmployee) -> int | None:
        if employee.id == "all":
            return None
        user = (
            await self.session.execute(
                select(User).where(
                    User.id == int(employee.id),
                    User.organization_id == self.organization_id,
                    User.is_active.is_(True),
                )
            )
        ).scalar_one_or_none()
        if user is None:
            raise NotFoundError("Сотрудник не найден")
        return user.id

    async def create(self, data: TaskCreate) -> TaskRead:
        task = Task(
            organization_id=self.organization_id,
            title=data.title.strip(),
            description=data.description.strip(),
            status=data.status,
            deadline=data.deadline,
            assignee_id=await self._assignee_id(data.employee),
            created_by_id=self.current_user.id,
            completed_at=dt.datetime.now(dt.UTC) if data.status == TaskStatus.DONE else None,
        )
        self.session.add(task)
        await self.session.flush()
        return self._read(await self._get(task.id))

    async def update(self, task_id: int, data: TaskUpdate) -> TaskRead:
        task = await self._get(task_id)
        payload = data.model_dump(exclude_unset=True)
        employee = payload.pop("employee", None)
        if employee is not None:
            task.assignee_id = await self._assignee_id(TaskEmployee.model_validate(employee))
        old_status = task.status
        for field, value in payload.items():
            setattr(task, field, value)
        if task.status == TaskStatus.DONE and old_status != TaskStatus.DONE:
            task.completed_at = dt.datetime.now(dt.UTC)
        elif task.status != TaskStatus.DONE:
            task.completed_at = None
        await self.session.flush()
        return self._read(await self._get(task.id))

    async def summary(self) -> TaskSummary:
        today = dt.date.today()
        week_ago = dt.datetime.now(dt.UTC) - dt.timedelta(days=7)
        active = Task.status != TaskStatus.DONE
        today_count = int(
            (
                await self.session.execute(
                    select(func.count(Task.id)).where(
                        *self._scope(), active, Task.deadline == today
                    )
                )
            ).scalar_one()
        )
        overdue = int(
            (
                await self.session.execute(
                    select(func.count(Task.id)).where(*self._scope(), active, Task.deadline < today)
                )
            ).scalar_one()
        )
        planned = int(
            (
                await self.session.execute(
                    select(func.count(Task.id)).where(*self._scope(), active)
                )
            ).scalar_one()
        )
        done_per_week = int(
            (
                await self.session.execute(
                    select(func.count(Task.id)).where(
                        *self._scope(),
                        Task.status == TaskStatus.DONE,
                        Task.completed_at >= week_ago,
                    )
                )
            ).scalar_one()
        )
        return TaskSummary(
            today=TaskTodaySummary(count=today_count, overdue=overdue),
            planned=planned,
            done_per_week=done_per_week,
        )

    async def delete(self, task_id: int) -> None:
        await self.session.delete(await self._get(task_id))

    async def delete_many(self, ids: list[int]) -> None:
        for task_id in list(dict.fromkeys(ids)):
            await self.delete(task_id)
