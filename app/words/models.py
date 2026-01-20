from pydantic import BaseModel, Field, field_validator
from typing import List


class WordConcatRequest(BaseModel):
    words: List[str] = Field(
        ...,
        min_items=1,
        description="List of words to concatenate. Each word must have enough characters for its position.",
        examples=[["hello", "world", "test"]]
    )
    
    @field_validator('words')
    @classmethod
    def validate_words_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure words are not empty strings."""
        if not v:
            raise ValueError("At least one word is required")
        for i, word in enumerate(v):
            if not word or not word.strip():
                raise ValueError(f"Word at position {i} cannot be empty")
        return [word.strip() for word in v]


class WordConcatResponse(BaseModel):
    result: str = Field(..., description="Concatenated result from extracting characters")
    words: List[str] = Field(..., description="Original list of words processed")
    characters_extracted: int = Field(..., description="Number of characters successfully extracted")
    characters_skipped: int = Field(..., description="Number of characters skipped due to word length")
    
    class Config:
        json_schema_extra = {
            "example": {
                "result": "hw",
                "words": ["hello", "world"],
                "characters_extracted": 2,
                "characters_skipped": 0
            }
        }

