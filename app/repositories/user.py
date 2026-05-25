from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_google_sub(self, google_sub: str) -> User | None:
        result = await self.session.execute(select(User).where(User.google_sub == google_sub))
        return result.scalar_one_or_none()

    async def upsert_from_google(
        self, google_sub: str, email: str, name: str, picture_url: str | None
    ) -> User:
        user = await self.get_by_google_sub(google_sub)
        if user:
            user.email = email
            user.name = name
            user.picture_url = picture_url
            user.last_login_at = datetime.utcnow()
            await self.session.commit()
            return user
        user = User(
            google_sub=google_sub,
            email=email,
            name=name,
            picture_url=picture_url,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
