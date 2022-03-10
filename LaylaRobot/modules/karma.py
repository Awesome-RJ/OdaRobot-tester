# Ported From WilliamButcher Bot.
# Credits Goes to WilliamButcherBot

import asyncio
import re

from pyrogram import filters

from LaylaRobot.utils.errors import capture_err
from LaylaRobot.utils.permissions import adminsOnly
from LaylaRobot.utils.dbfunc import (
    alpha_to_int,
    get_karma,
    get_karmas,
    int_to_alpha,
    is_karma_on,
    karma_off,
    karma_on,
    update_karma,
)
from LaylaRobot.utils.filter_groups import karma_negative_group, karma_positive_group
from LaylaRobot import pbot as app

__mod_name__ = "Karma"
__help__ = """
[UPVOTE] - Use upvote keywords like "+", "+1", "thanks" etc to upvote a message.
[DOWNVOTE] - Use downvote keywords like "-", "-1", etc to downvote a message.
Reply to a message with /karma to check a user's karma
Send /karma without replying to any message to chek karma list of top 10 users
Special Credits to WilliamButcherBot
"""


regex_upvote = (
    r"^(\+|\+\+|\+1|thx|tnx|ty|thank you|thanx|thanks|pro|cool|good|👍|\+\+ .+)$"
)
regex_downvote = r"^(-|--|-1|👎|-- .+)$"


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_upvote)
    & ~filters.via_bot
    & ~filters.bot
    & ~filters.edited,
    group=karma_positive_group,
)
async def upvote(_, message):

    if await is_karma_on(message.chat.id):
        return
    try:
        if message.reply_to_message.from_user.id == message.from_user.id:
            return
    except:
        return
    chat_id = message.chat.id
    try:
        user_id = message.reply_to_message.from_user.id
    except:
        return
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
    if current_karma:
        current_karma = current_karma["karma"]
        karma = current_karma + 1
    else:
        karma = 1
    new_karma = {"karma": karma}
    await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    await message.reply_text(
        f"Incremented Karma of {user_mention} By 1 \nTotal Points: {karma}"
    )


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_downvote, re.IGNORECASE)
    & ~filters.via_bot
    & ~filters.bot
    & ~filters.edited,
    group=karma_negative_group,
)
@capture_err
async def downvote(_, message):

    if not await is_karma_on(message.chat.id):
        return
    try:
        if message.reply_to_message.from_user.id == message.from_user.id:
            return
    except:
        return
    chat_id = message.chat.id
    try:
        user_id = message.reply_to_message.from_user.id
    except:
        return
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
    if current_karma:
        current_karma = current_karma["karma"]
        karma = current_karma - 1
    else:
        karma = 1
    new_karma = {"karma": karma}
    await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    await message.reply_text(
        f"Decremented Karma Of {user_mention} By 1 \nTotal Points: {karma}"
    )


@app.on_message(filters.command("karma") & filters.group)
@capture_err
async def command_karma(_, message):
    chat_id = message.chat.id
    if not message.reply_to_message:
        m = await message.reply_text("Analyzing Karma...Will Take 10 Seconds")
        karma = await get_karmas(chat_id)
        if not karma:
            await m.edit("No karma in Database for this chat.")
            return
        msg = f"**Karma list of {message.chat.title}:- **\n"
        limit = 0
        karma_dicc = {}
        for i in karma:
            user_id = await alpha_to_int(i)
            user_karma = karma[i]["karma"]
            karma_dicc[str(user_id)] = user_karma
            karma_arranged = dict(
                sorted(karma_dicc.items(), key=lambda item: item[1], reverse=True)
            )
        if not karma_dicc:
            await m.edit("No karma in DB for this chat.")
            return
        for user_idd, karma_count in karma_arranged.items():
            if limit > 9:
                break
            try:
                user = await app.get_users(int(user_idd))
                await asyncio.sleep(0.8)
            except Exception:
                continue
            first_name = user.first_name
            if not first_name:
                continue
            username = user.username
            msg += f"**{karma_count}**  {first_name[:12] + '...' if len(first_name) > 12 else first_name}  `{'@' + username if username else user_idd}`\n"

            limit += 1
        await m.edit(msg)
    else:
        user_id = message.reply_to_message.from_user.id
        karma = await get_karma(chat_id, await int_to_alpha(user_id))
        karma = karma["karma"] if karma else 0
        await message.reply_text(f"**Total Points**: __{karma}__")


@app.on_message(filters.command("karmastat") & ~filters.private)
@adminsOnly("can_change_info")
async def captcha_state(_, message):
    usage = "**Usage:**\n/karmastat [On|Off]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "on":
        await karma_on(chat_id)
        await message.reply_text("Karma will be enabled here")
    elif state == "off":
        await karma_off(chat_id)
        await message.reply_text("Karma will be disabled here")
    else:
        await message.reply_text(usage)
