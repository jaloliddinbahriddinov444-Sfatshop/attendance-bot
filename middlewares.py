"""Aiogram middleware'lari."""
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, User

import texts
from database import get_employee_by_telegram_id

logger = logging.getLogger(__name__)


class BlockDeactivatedMiddleware(BaseMiddleware):
    """Ro'yxatda bor, lekin faolsizlantirilgan (is_active=0) xodimlarni bloklaydi.

    Faqat MA'LUM (bazada bor) va is_active=0 bo'lgan foydalanuvchilar bloklanadi.
    Ro'yxatdan o'tmagan begona odamlar (employee=None) bloklanmaydi — ular
    /start orqali tegishli javobni olishadi (begona → rad, INITIAL_ADMIN → ro'yxat).
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user is not None:
            emp = get_employee_by_telegram_id(user.id)
            if emp is not None and not emp["is_active"]:
                logger.info("Bloklangan (deaktiv) foydalanuvchi: tg=%s", user.id)
                if isinstance(event, Message):
                    await event.answer(texts.ACCOUNT_DEACTIVATED)
                elif isinstance(event, CallbackQuery):
                    await event.answer(texts.ACCOUNT_DEACTIVATED, show_alert=True)
                return  # handlerni chaqirmaymiz — to'liq bloklangan
        return await handler(event, data)
