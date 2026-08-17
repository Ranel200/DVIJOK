"""Frontend-oriented schemas for staff tasks."""

from datetime import date, datetime

from pydantic import ConfigDict, Field, model_validator

from app.shared.base_schema import StrictModel
from app.shared.enums import TaskStatus


class TaskModel(StrictModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class TaskEmployee(TaskModel):
    id: int | str
    name: str
    role: str


class TaskCreate(TaskModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    status: TaskStatus = TaskStatus.NEW
    deadline: date | None = None
    employee: TaskEmployee

    @model_validator(mode="after")
    def validate_employee_id(self) -> "TaskCreate":
        if isinstance(self.employee.id, str) and self.employee.id != "all":
            raise ValueError("employee.id должен быть числом или 'all'")
        return self


class TaskUpdate(TaskModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    deadline: date | None = None
    employee: TaskEmployee | None = None


class TaskStatusUpdate(TaskModel):
    status: TaskStatus


class TaskRead(TaskModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    deadline: date | None
    employee: TaskEmployee
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class TaskTodaySummary(TaskModel):
    count: int
    overdue: int


class TaskSummary(TaskModel):
    today: TaskTodaySummary
    planned: int
    done_per_week: int = Field(alias="donePerWeek")


class TaskBulkDelete(TaskModel):
    ids: list[int] = Field(min_length=1, max_length=100)
