"""HTTP-роутер модуля schedule. Доступ: ADMIN и MANAGER."""

import datetime as dt

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_feature
from app.core.exceptions import ForbiddenError
from app.modules.schedule.admin_schemas import (
    StaffDetail,
    StaffMonthRow,
    StaffScheduleSettings,
    StaffWrite,
)
from app.modules.schedule.admin_service import ScheduleAdminService
from app.modules.schedule.repository import ScheduleRepository
from app.modules.schedule.schemas import (
    AvailabilitySuggestions,
    BlockCreate,
    BlockRead,
    CalendarView,
    SlotCreate,
    SlotRead,
    SlotUpdate,
    WeekView,
    WorkingHoursRead,
    WorkingHoursReplace,
)
from app.modules.schedule.service import ScheduleService
from app.modules.users.models import User
from app.shared.enums import UserRole

router = APIRouter(
    prefix="/schedule",
    tags=["schedule"],
    dependencies=[Depends(get_current_user)],
)

_current = require_feature(
    "schedule", UserRole.ADMIN, UserRole.MANAGER, UserRole.MECHANIC
)


async def _manage(user: User = Depends(_current)) -> User:
    if not user.is_owner and user.staff_role_key != "senior_admin":
        raise ForbiddenError("Управлять сотрудниками и графиком может только старший администратор")
    return user


def get_schedule_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(_current),
) -> ScheduleService:
    return ScheduleService(
        ScheduleRepository(db, current_user.organization_id),
        current_user=current_user,
    )


def get_schedule_admin_service(
    db: AsyncSession = Depends(get_db, scope="function"),
    current_user: User = Depends(_current),
) -> ScheduleAdminService:
    return ScheduleAdminService(db, current_user)


@router.get("/employees", response_model=list[StaffMonthRow])
async def staff_month(
    year: int = Query(default_factory=lambda: dt.date.today().year, ge=2000, le=2100),
    month: int = Query(default_factory=lambda: dt.date.today().month - 1, ge=0, le=11),
    service: ScheduleAdminService = Depends(get_schedule_admin_service),
) -> list[StaffMonthRow]:
    return await service.month(year, month)


@router.get(
    "/employees/{user_id}",
    response_model=StaffDetail,
    dependencies=[Depends(_manage)],
)
async def staff_detail(
    user_id: int,
    service: ScheduleAdminService = Depends(get_schedule_admin_service),
) -> StaffDetail:
    return await service.detail(user_id)


@router.post(
    "/employees",
    response_model=StaffDetail,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_manage)],
)
async def create_staff(
    payload: StaffWrite,
    service: ScheduleAdminService = Depends(get_schedule_admin_service),
) -> StaffDetail:
    return await service.create(payload)


@router.put(
    "/employees/{user_id}",
    response_model=StaffDetail,
    dependencies=[Depends(_manage)],
)
async def update_staff(
    user_id: int,
    payload: StaffWrite,
    service: ScheduleAdminService = Depends(get_schedule_admin_service),
) -> StaffDetail:
    return await service.update(user_id, payload)


@router.delete(
    "/employees/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(_manage)],
)
async def delete_staff(
    user_id: int,
    service: ScheduleAdminService = Depends(get_schedule_admin_service),
) -> None:
    await service.delete(user_id)


@router.put(
    "/settings",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(_manage)],
)
async def save_staff_schedule_settings(
    payload: StaffScheduleSettings,
    service: ScheduleAdminService = Depends(get_schedule_admin_service),
) -> None:
    await service.save_settings(payload)


@router.get("/week", response_model=WeekView)
async def week_view(
    day: dt.date = Query(..., description="Любая дата нужной недели (Пн–Вс)"),
    mechanic_id: int | None = Query(default=None),
    service: ScheduleService = Depends(get_schedule_service),
) -> WeekView:
    start, end, slots, blocks = await service.week(day, mechanic_id)
    return WeekView(week_start=start, week_end=end, slots=slots, blocks=blocks)


@router.get("/calendar", response_model=CalendarView)
async def calendar_view(
    week_start: dt.date = Query(..., alias="weekStart"),
    service: ScheduleService = Depends(get_schedule_service),
) -> CalendarView:
    return await service.calendar(week_start)


@router.get("/availability", response_model=AvailabilitySuggestions)
async def availability(
    date_from: dt.date = Query(...),
    date_to: dt.date = Query(...),
    mechanic_id: int | None = Query(default=None),
    service_id: int | None = Query(default=None),
    duration_minutes: int | None = Query(default=None, ge=1, le=1440),
    service: ScheduleService = Depends(get_schedule_service),
) -> AvailabilitySuggestions:
    """Только предлагает свободные интервалы; ничего не резервирует."""
    return await service.suggestions(
        date_from=date_from,
        date_to=date_to,
        mechanic_id=mechanic_id,
        service_id=service_id,
        duration_minutes=duration_minutes,
    )


@router.get(
    "/mechanics/{mechanic_id}/working-hours",
    response_model=WorkingHoursRead,
)
async def get_working_hours(
    mechanic_id: int,
    service: ScheduleService = Depends(get_schedule_service),
) -> WorkingHoursRead:
    return await service.working_hours(mechanic_id)


@router.put(
    "/mechanics/{mechanic_id}/working-hours",
    response_model=WorkingHoursRead,
    dependencies=[Depends(_manage)],
)
async def replace_working_hours(
    mechanic_id: int,
    payload: WorkingHoursReplace,
    service: ScheduleService = Depends(get_schedule_service),
) -> WorkingHoursRead:
    return await service.replace_working_hours(mechanic_id, payload.intervals)


@router.post(
    "/slots",
    response_model=SlotRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_manage)],
)
async def create_slot(
    payload: SlotCreate, service: ScheduleService = Depends(get_schedule_service)
) -> SlotRead:
    return SlotRead.model_validate(await service.create_slot(payload))


@router.patch(
    "/slots/{slot_id}",
    response_model=SlotRead,
    dependencies=[Depends(_manage)],
)
async def update_slot(
    slot_id: int, payload: SlotUpdate, service: ScheduleService = Depends(get_schedule_service)
) -> SlotRead:
    return SlotRead.model_validate(await service.update_slot(slot_id, payload))


@router.delete(
    "/slots/{slot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(_manage)],
)
async def delete_slot(
    slot_id: int, service: ScheduleService = Depends(get_schedule_service)
) -> None:
    await service.delete_slot(slot_id)


@router.post(
    "/blocks",
    response_model=BlockRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_manage)],
)
async def create_block(
    payload: BlockCreate, service: ScheduleService = Depends(get_schedule_service)
) -> BlockRead:
    return BlockRead.model_validate(await service.create_block(payload))


@router.delete(
    "/blocks/{block_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(_manage)],
)
async def delete_block(
    block_id: int, service: ScheduleService = Depends(get_schedule_service)
) -> None:
    await service.delete_block(block_id)
