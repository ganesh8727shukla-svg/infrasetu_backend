from sqlalchemy.orm import Session

from app.models import AIDetection
from app.services.ids import new_id


def analyze_image(
    db: Session,
    *,
    asset_id: str,
    image_url: str,
    complaint_id: str | None = None,
) -> AIDetection:
    """
    Development adapter.

    The source report requires an AI endpoint but does not specify the actual
    model, input tensor, class list, or inference service. Therefore this is
    intentionally deterministic and replaceable.
    """
    detection = AIDetection(
        id=new_id("DET"),
        asset_id=asset_id,
        complaint_id=complaint_id,
        image_url=image_url,
        detection_type="Pothole",
        confidence=94.0,
        severity="critical",
    )
    db.add(detection)
    return detection
