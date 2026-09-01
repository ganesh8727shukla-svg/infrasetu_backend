from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy.orm import Session
from ultralytics import YOLO

from app.models import AIDetection
from app.services.ids import new_id



MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "NILSMS_best.pt"
)

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"YOLO model not found at: {MODEL_PATH}"
    )

model = YOLO(str(MODEL_PATH))



CLASS_NAMES = {
    0: "Longitudinal",
    1: "Transverse",
    2: "Alligator",
    3: "Pothole",
}



def get_severity(
    confidence: float,
    detection_type: str,
) -> str:

    if detection_type == "Pothole":
        if confidence >= 0.70:
            return "critical"
        elif confidence >= 0.40:
            return "high"
        elif confidence >= 0.20:
            return "medium"

        return "low"

    if confidence >= 0.70:
        return "high"
    elif confidence >= 0.40:
        return "medium"

    return "low"



def resolve_image_source(image_url: str) -> str:
  

    parsed = urlparse(image_url)
    filename = Path(parsed.path).name

    project_root = Path(__file__).resolve().parents[2]

    possible_paths = [
        project_root / "storage" / "uploads" / filename,
        project_root / "test.jpg",
        project_root / filename,
    ]

    for path in possible_paths:
        if path.exists() and path.is_file():
            return str(path)

    local_path = Path(image_url)

    if local_path.exists() and local_path.is_file():
        return str(local_path)

    return image_url


def analyze_image(
    db: Session,
    *,
    asset_id: str,
    image_url: str,
    complaint_id: str | None = None,
) -> list[AIDetection]:

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"YOLO model not found at: {MODEL_PATH}"
        )

    image_source = resolve_image_source(image_url)

    if (
        not image_source.startswith("http://")
        and not image_source.startswith("https://")
    ):
        if not Path(image_source).exists():
            raise FileNotFoundError(
                f"Image not found: {image_source}"
            )

    results = model.predict(
        source=image_source,
        imgsz=640,
        conf=0.10,
        device="cpu",
        verbose=False,
        stream=False,
    )

    # YOLO normally returns a list
    if results is None:
        raise ValueError(
            "YOLO returned no prediction result."
        )

    if len(results) == 0:
        raise ValueError(
            "YOLO returned no prediction result."
        )

    result = results[0]

    if result.boxes is None or len(result.boxes) == 0:
        return []

    detections: list[AIDetection] = []

    for box in result.boxes:

        class_id = int(box.cls[0].item())

        confidence = float(
            box.conf[0].item()
        )

        detection_type = CLASS_NAMES.get(
            class_id,
            f"Class {class_id}",
        )

        severity = get_severity(
            confidence,
            detection_type,
        )

        detection = AIDetection(
            id=new_id("DET"),
            asset_id=asset_id,
            complaint_id=complaint_id,
            image_url=image_url,
            detection_type=detection_type,
            confidence=confidence * 100,
            severity=severity,
        )

        db.add(detection)

        detections.append(detection)

    detections.sort(
        key=lambda x: x.confidence,
        reverse=True,
    )

    return detections