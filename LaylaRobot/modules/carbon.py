from pyrogram import filters

from LaylaRobot import pbot
from LaylaRobot.utils.errors import capture_err
from LaylaRobot.utils.functions import make_carbon


@pbot.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "Reply to a text message to make carbon."
        )
    if not message.reply_to_message.text:
        return await message.reply_text(
            "Reply to a text message to make carbon."
        )
    m = await message.reply_text("Preparing Carbon")
    carbon = await make_carbon(message.reply_to_message.text)
    await m.edit("Uploading")
    await pbot.send_document(message.chat.id, carbon)
    await m.delete()
    carbon.close()

__mod_name__ = "Carbon Text"
__help__ = """
    /carbon <text> [or reply]
Usage: Beautify your code using carbon.now.sh
"""
