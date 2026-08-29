from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import Notification, User
from app.schemas.notification import NotificationOut, NotificationUpdate

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut])
def notifications(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = db.scalars(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
    ).all()
    return [
        NotificationOut(
            id=x.id, title=x.title, body=x.body,
            createdAt=x.created_at, read=x.read,
        ) for x in rows
    ]


@router.put("/{notification_id}", response_model=NotificationOut)
def mark_read(
    notification_id: str,
    payload: NotificationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = db.get(Notification, notification_id)
    if not row or row.user_id != user.id:
        raise HTTPException(404, "Notification not found")
    row.read = payload.read
    db.commit()
    db.refresh(row)
    return NotificationOut(
        id=row.id, title=row.title, body=row.body,
        createdAt=row.created_at, read=row.read,
    )
