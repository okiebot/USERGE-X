""" setup gmute """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved

import asyncio

from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    UserAdminInvalid,
)
from pyrogram.types import ChatPermissions

from userge import Config, Message, filters, get_collection, userge

GMUTE_USER_BASE = get_collection("GMUTE_USER")
CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)


@userge.on_cmd(
    "mute",
    about={
        "header": "Globally Mute A User",
        "description": "Adds User to your GMute List",
        "examples": "{tr}gmute [userid | reply] [reason for gmute] (mandatory)",
    },
    allow_channels=False,
    allow_bots=False,
)
async def gmute_user(msg: Message):
    """Mute a user globally"""
    await msg.edit("`MUTING THIS CUCK!`")
    user_id, reason = msg.extract_user_and_text
    if not user_id:
        await msg.edit(
            "`Error`"
            "`Error"
            "Error"
        )
        return
    get_mem = await msg.client.get_user_dict(user_id)
    firstname = get_mem["fname"]
    if not reason:
        await msg.edit(
            f"**⚠️ERROR**\n\n**MUTING** [{firstname}](tg://user?id={user_id}) "
            "`Failed! Must provide reason.`",
            del_in=5,
        )
        return
    user_id = get_mem["id"]
    if user_id == msg.from_user.id:
        await msg.err(r"error")
        return
    if user_id in Config.SUDO_USERS:
        await msg.edit(
            "`That user has access to me, unable to mute user.`\n\n"
            "Ask Lalo for help!!`",
            del_in=5,
        )
        return
    found = await GMUTE_USER_BASE.find_one({"user_id": user_id})
    if found:
        await msg.edit(
            "**⚠️ERROR⚠️**\n\n`User is already muted`\n"
            f"**Reason For Mute:** `{found['reason']}`"
        )
        return
    await asyncio.gather(
        GMUTE_USER_BASE.insert_one(
            {"firstname": firstname, "user_id": user_id, "reason": reason}
        ),
        msg.edit(
            r"♦️USER NOW MUTED"
            f"\n\n**Name:** [{firstname}](tg://user?id={user_id})\n"
            f"**ID:** `{user_id}`\n**Reason:** `{reason}`"
        ),
    )
    chats = await userge.get_common_chats(user_id)
    for chat in chats:
        try:
            await chat.restrict_member(user_id, ChatPermissions())
            await CHANNEL.log(
                r"\\**ANTI SPAM**//"
                f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
                f"**ID:** `{user_id}`\n"
                f"**Chat:** {chat.title}\n"
                f"**Chat ID:** `{chat.id}`\n"
                f"**Reason:** `{reason}`\n\n$MUTE #id{user_id}"
            )
        except (ChatAdminRequired, UserAdminInvalid):
            pass
    if msg.reply_to_message:
        await CHANNEL.fwd_msg(msg.reply_to_message)
        await CHANNEL.log(f"$GMUTE #prid{user_id} ⬆️")
    LOG.info("G-Muted %s", str(user_id))


@userge.on_cmd(
    "unmute",
    about={
        "header": "Globally Unmute an User",
        "description": "Removes an user from your GMute List",
        "examples": "{tr}ungmute [userid | reply]",
    },
    allow_channels=False,
    allow_bots=False,
)
async def ungmute_user(msg: Message):
    """unmute a user globally"""
    await msg.edit("`UN-MUTING USER`")
    user_id, _ = msg.extract_user_and_text
    if not user_id:
        await msg.err("user-id not found")
        return
    get_mem = await msg.client.get_user_dict(user_id)
    firstname = get_mem["fname"]
    user_id = get_mem["id"]
    found = await GMUTE_USER_BASE.find_one({"user_id": user_id})
    if not found:
        await msg.err("User was never muted")
        return
    await asyncio.gather(
        GMUTE_USER_BASE.delete_one(found),
        msg.edit(
            r"♦️**Un-Muted User**♦️"
            f"\n\n**Name:** [{firstname}](tg://user?id={user_id})\n"
            f"**ID:** `{user_id}`"
        ),
    )
    chats = await userge.get_common_chats(user_id)
    for chat in chats:
        try:
            await chat.unban_member(user_id)
            await CHANNEL.log(
                r"\\**#Antispam_Log**//"
                f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
                f"**User ID:** `{user_id}`\n"
                f"**Chat:** {chat.title}\n"
                f"**Chat ID:** `{chat.id}`\n\n$UNGMUTED #id{user_id}"
            )
        except (ChatAdminRequired, UserAdminInvalid):
            pass
    LOG.info("UnGMuted %s", str(user_id))


@userge.on_cmd(
    "gmlist",
    about={
        "header": "Get a List of GMuted Users",
        "description": "Get Up-to-date list of users GMuted by you.",
        "examples": "{tr}gmlist",
    },
    allow_channels=False,
)
async def list_gmuted(msg: Message):
    """views gmuted users"""
    users = ""
    async for c in GMUTE_USER_BASE.find():
        users += "**User** : " + str(c["firstname"])
        users += "\n**User ID** : " + str(c["user_id"])
        users += "\n**Reason for GMuted** : " + str(c["reason"]) + "\n\n"
    await msg.edit_or_send_as_file(
        f"**--Globally Muted Users List--**\n\n{users}"
        if users
        else "`Gmute List is Empty`"
    )


@userge.on_filters(
    filters.group & filters.new_chat_members, group=1, check_restrict_perm=True
)
async def gmute_at_entry(msg: Message):
    """handle gmute"""
    chat_id = msg.chat.id
    for user in msg.new_chat_members:
        user_id = user.id
        first_name = user.first_name
        gmuted = await GMUTE_USER_BASE.find_one({"user_id": user_id})
        if gmuted:
            await asyncio.gather(
                msg.client.restrict_chat_member(chat_id, user_id, ChatPermissions()),
                msg.reply(
                    r"\\**#𝑿_Antispam**//"
                    "\n\nGlobally Muted User Detected in this Chat.\n\n"
                    f"**User:** [{first_name}](tg://user?id={user_id})\n"
                    f"**ID:** `{user_id}`\n**Reason:** `{gmuted['reason']}`\n\n"
                    "**Quick Action:** Muted",
                    del_in=10,
                ),
                CHANNEL.log(
                    r"\\**#Antispam_Log**//"
                    "\n\n**GMuted User $SPOTTED**\n"
                    f"**User:** [{first_name}](tg://user?id={user_id})\n"
                    f"**ID:** `{user_id}`\n**Reason:** {gmuted['reason']}\n**Quick Action:** "
                    f"Muted in {msg.chat.title}"
                ),
            )
    msg.continue_propagation()
