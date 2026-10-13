#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations as _annotations

import pytest

from pyrogram import raw, types


@pytest.mark.asyncio
async def test_description_is_parsed_from_text_with_entities() -> None:
    # Layer 230 changed `botVerification.description` from `string` to `TextWithEntities`.
    #  The high-level field stays a `str` (a `Str`, so existing callers keep working) while
    #  the entities remain reachable through its `.html`/`.markdown` renderings.
    verification = raw.types.BotVerification(
        bot_id=7,
        icon=123,
        description=raw.types.TextWithEntities(
            text="Verified by Acme",
            entities=[raw.types.MessageEntityBold(offset=12, length=4)],
        ),
    )
    users = {
        7: raw.types.User(id=7, first_name="Bot 7", bot=True, usernames=[], restriction_reason=[]),
    }

    parsed = await types.BotVerification._parse(None, verification, users)

    assert isinstance(parsed.description, str)
    assert parsed.description == "Verified by Acme"
    assert parsed.description.html == "Verified by <b>Acme</b>"
    assert parsed.custom_emoji_id == "123"
    assert parsed.bot.id == 7
