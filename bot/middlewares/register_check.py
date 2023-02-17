from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from data.users import User


class RegisterCheck(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        session_maker: sessionmaker = data['session_maker']
        async with session_maker() as session:
            async with session.begin():
                result = await session.execute(select(User).where(User.telegram_user_id))
                user = result.one_or_none()

                if not user:
                    user = User(
                        user_id=event.from_user.id,
                        username=event.from_user.username
                    )
                    await session.merge(user)
                    if isinstance(event, Message):
                        await event.answer('Вы умпешно зарегистированны в боте')
                    else:
                        await event.message.answeer('Вы умпешно зарегистированны в боте')

        return await handler(event, data)
