from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class WordAddRequest(BaseModel):
    word: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The word to add to the dictionary",
        examples=["python"]
    )
    definition: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The definition of the word",
        examples=["A high-level programming language known for its simplicity and readability"]
    )
    
    @field_validator('word')
    @classmethod
    def validate_word(cls, v: str) -> str:
        """Normalize word by trimming whitespace."""
        word = v.strip()
        if not word:
            raise ValueError("Word cannot be empty or only whitespace")
        return word
    
    @field_validator('definition')
    @classmethod
    def validate_definition(cls, v: str) -> str:
        """Normalize definition by trimming whitespace."""
        definition = v.strip()
        if not definition:
            raise ValueError("Definition cannot be empty or only whitespace")
        return definition


class WordDefinitionResponse(BaseModel):
    word: str = Field(..., description="The word")
    definition: str = Field(..., description="The definition of the word")
    
    class Config:
        json_schema_extra = {
            "example": {
                "word": "python",
                "definition": "A high-level programming language known for its simplicity and readability"
            }
        }


class WordAddResponse(BaseModel):
    message: str = Field(..., description="Success message")
    word: str = Field(..., description="The word that was added")
    definition: str = Field(..., description="The definition that was added")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Word 'python' added successfully",
                "word": "python",
                "definition": "A high-level programming language"
            }
        }


class DictionaryEntryResponse(BaseModel):
    """Full dictionary entry response with metadata"""
    id: int = Field(..., description="Unique identifier of the dictionary entry")
    word: str = Field(..., description="The word")
    definition: str = Field(..., description="The definition of the word")
    created_at: datetime = Field(..., description="Timestamp when the entry was created")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "word": "python",
                "definition": "A high-level programming language",
                "created_at": "2024-01-15T10:30:00"
            }
        }

