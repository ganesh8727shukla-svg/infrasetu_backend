from geoalchemy2.functions import ST_X, ST_Y
from sqlalchemy import select


def coordinates_from_geom(db, geom):
    # Kept as a helper for explicit SQLAlchemy expressions.
    return (
        db.execute(select(ST_X(geom), ST_Y(geom))).one()
    )
