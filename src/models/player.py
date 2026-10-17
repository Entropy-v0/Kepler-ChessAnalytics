from datetime import date
from typing import Any, Optional
from pydantic import BaseModel, model_validator


class FidePlayer(BaseModel):
    fideid: str
    name: str
    country: Optional[str] = None
    sex: Optional[str] = None
    title: Optional[str] = None
    w_title: Optional[str] = None
    o_title: Optional[str] = None
    rating: Optional[int] = None
    games: Optional[int] = None
    rapid_rating: Optional[int] = None
    rapid_games: Optional[int] = None
    blitz_rating: Optional[int] = None
    blitz_games: Optional[int] = None
    birthday: Optional[int] = None
    flag: Optional[str] = None
    snapshot_date: date

    @model_validator(mode="before")
    @classmethod
    def clean_empty_strings(cls, data: Any) -> Any:
        """
        Convierte strings vacíos a None para evitar errores
        al intentar parsear campos numéricos y asegura que fideid sea str.
        """
        if isinstance(data, dict):
            cleaned = {k: (None if v == "" or v is None else v) for k, v in data.items()}
            if cleaned.get("fideid") is not None:
                cleaned["fideid"] = str(cleaned["fideid"]).strip()
            return cleaned
        return data
