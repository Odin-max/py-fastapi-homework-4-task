from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Path, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from database import get_db, UserModel, UserProfileModel
from schemas.profiles import ProfileCreateSchema, ProfileResponseSchema
from validation import validate_image
from datetime import date

from config.dependencies import get_s3_storage_client, S3StorageInterface
from config.dependencies import get_current_user


router = APIRouter()


@router.post(
    "/users/{user_id}/profile/",
    response_model=ProfileResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_profile(
    user_id: int = Path(..., description="User ID"),
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    gender: Annotated[str, Form()],
    date_of_birth: Annotated[str, Form()],
    info: Annotated[str, Form()],
    avatar: UploadFile = Form(...),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    s3_client: S3StorageInterface = Depends(get_s3_storage_client),
):
    if current_user.id != user_id and not current_user.has_group("admin"):
        raise HTTPException(status_code=403, detail="You don't have permission to edit this profile.")

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or not active.")

    if user.profile:
        raise HTTPException(status_code=400, detail="User already has a profile.")

    try:
        validate_image(avatar)
        filename = f"{user_id}_avatar.{avatar.filename.split('.')[-1]}"
        avatar_url = await s3_client.upload_file(file=avatar, object_name=f"avatars/{filename}")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to upload avatar. Please try again later.")

    profile = UserProfileModel(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        date_of_birth=date.fromisoformat(date_of_birth),
        info=info,
        avatar=avatar_url,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return ProfileResponseSchema.model_validate(profile)

