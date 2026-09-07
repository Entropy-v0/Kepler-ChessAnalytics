from typing import Optional, Any
from pydantic import BaseModel, model_validator

class FidePlayer(BaseModel):
    fideid: int
    name: str
    country: Optional[str] = None
    sex: Optional[str] = None
    title: Optional[str] = None
    w_title: Optional[str] = None
    o_title: Optional[str] = None
    rating: Optional[int] = None
    rapid_rating: Optional[int] = None
    blitz_rating: Optional[int] = None
    birthday: Optional[int] = None
    flag: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def clean_empty_strings(cls, data: Any) -> Any:
        """
        Convierte strings vacíos a None para evitar errores 
        al intentar parsear campos numéricos (como 'rating' o 'birthday').
        """
        if isinstance(data, dict):
            return {k: (None if v == "" or v is None else v) for k, v in data.items()}
        return data
