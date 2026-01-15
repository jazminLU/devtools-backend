from pydantic import BaseModel, Field
from datetime import datetime


class WordAddRequest(BaseModel):
    word: str = Field(..., description="The word to add to the dictionary")
    definition: str = Field(..., description="The definition of the word")


class WordDefinitionResponse(BaseModel):
    word: str
    definition: str


class DictionaryEntryResponse(BaseModel):
    """Full dictionary entry response with metadata"""
    id: int
    word: str
    definition: str
    created_at: datetime
    
    class Config:
        from_attributes = True

