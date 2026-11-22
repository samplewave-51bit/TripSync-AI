"""
TripSync AI - Attraction & Destination Repository
"""

from typing import Any, List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.app.crud.base import CRUDBase
from backend.app.models.destination import Attraction, Destination


class CRUDAttraction(CRUDBase[Attraction, Any, Any]):
    """Repository handling attraction catalog queries and filtering."""

    def get_by_place_id(self, db: Session, place_id: int) -> Optional[Attraction]:
        return db.query(Attraction).filter(Attraction.place_id == place_id).first()

    def search_attractions(
        self,
        db: Session,
        *,
        query: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        zone: Optional[str] = None,
        type_: Optional[str] = None,
        max_fee: Optional[float] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Attraction]:
        q = db.query(Attraction)

        if query:
            search_pattern = f"%{query}%"
            q = q.filter(
                or_(
                    Attraction.name.ilike(search_pattern),
                    Attraction.city.ilike(search_pattern),
                    Attraction.type.ilike(search_pattern),
                )
            )

        if state:
            q = q.filter(Attraction.state.ilike(state))

        if city:
            q = q.filter(Attraction.city.ilike(city))

        if zone:
            q = q.filter(Attraction.zone.ilike(zone))

        if type_:
            q = q.filter(Attraction.type.ilike(type_))

        if max_fee is not None:
            q = q.filter(Attraction.entrance_fee_inr <= max_fee)

        return q.order_by(Attraction.rating.desc()).offset(skip).limit(limit).all()


attraction = CRUDAttraction(Attraction)
destination = CRUDBase[Destination, Any, Any](Destination)
