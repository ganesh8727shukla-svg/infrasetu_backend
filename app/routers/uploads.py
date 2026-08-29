from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import require_roles
from app.db.session import get_db
from app.models import Upload, User
from app.schemas.upload import UploadOut
from app.services.ids import new_id

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("", response_model=UploadOut, status_code=201)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("citizen", "contractor")),
):
    content_type = (file.content_type or "").lower()
    if content_type not in settings.allowed_upload_type_list:
        raise HTTPException(415, "Unsupported file type")

    data = await file.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(413, "File is too large")

    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix.lower() or ".bin"
    filename = f"{uuid4().hex}{suffix}"
    path = Path(settings.upload_dir) / filename
    path.write_bytes(data)

    url = f"{settings.public_base_url}/media/{filename}"
    row = Upload(
        id=new_id("UPL"),
        url=url,
        mime=content_type,
        size=len(data),
        uploaded_by=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return UploadOut(id=row.id, url=row.url, mime=row.mime, size=row.size)
