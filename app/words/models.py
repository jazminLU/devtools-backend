from pydantic import BaseModel, Field
from typing import List


class WordConcatRequest(BaseModel):
    words: List[str] = Field(..., min_items=1, description="List of words to concatenate")


class WordConcatResponse(BaseModel):
    result: str
    words: List[str]

