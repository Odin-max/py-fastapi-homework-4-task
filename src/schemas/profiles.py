from datetime import date

from fastapi import UploadFile, Form, File, HTTPException
from pydantic import BaseModel, field_validator, HttpUrl, Field

from validation import (
    validate_name,
    validate_image,
    validate_gender,
    validate_birth_date
)

class ProfileCreateSchema(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    gender: str
    date_of_birth: date
    info: str = Field(..., min_length=1)
    avatar: UploadFile

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str) -> str:
        validate_name(value)
        return value

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: str) -> str:
        validate_name(value)
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender_value(cls, value: str) -> str:
        validate_gender(value)
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_birth_date_value(cls, value: date) -> date:
        validate_birth_date(value)
        return value


class ProfileResponseSchema(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    gender: str
    date_of_birth: date
    info: str
    avatar: str

    model_config = {
        "from_attributes": True
    }