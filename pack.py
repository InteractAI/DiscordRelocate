import os
import math
import json
import shutil
import datetime
import requests
from typing import List
from dataclasses import dataclass
import discord
from discord.ext import commands


PROGRESS_BAR_LEN = 20


@dataclass
class MessagePack:
    author_name: str
    author_id: int
    message_id: int
    content: str
    pinned: bool
    embeds: List[discord.Embed]
    reactions: List[discord.Reaction]
    time: datetime.datetime
    attachments: List[str]  # paths to local caches


class MessageHistory:
    def __init__(
        self,
        bot: discord.Bot,
        channel_id: int,
        progress_report_ctx: commands.Context = None,
    ):
        self._bot = bot
        self._channel_id = channel_id
        self._channel: discord.TextChannel = self._bot.get_channel(channel_id)
        assert isinstance(self._channel, discord.TextChannel)

        self._history: List[MessagePack] = []
        self._cache_path = f"tmp-{channel_id}"

        self._progress_ctx = progress_report_ctx  # report progress here

    async def build(self):
        """Build message history"""

        if not os.path.exists(self._cache_path):
            os.mkdir(self._cache_path)

        messages = await self._channel.history(limit=None, oldest_first=True).flatten()

        total = len(messages)
        current = 0
        report_freq = max(1, total // PROGRESS_BAR_LEN)

        if self._progress_ctx is not None:
            bar = self._build_progress_bar(current, total)
            progress = await self._progress_ctx.reply(
                f"**History Compiling Progress**\n{bar}"
            )

        session = requests.Session()

        for message in messages:
            author_name = message.author.display_name
            author_id = message.author.id
            message_id = message.id
            content = message.content
            pinned = message.pinned
            embeds = message.embeds
            reactions = message.reactions
            time = message.created_at

            attachments = []
            for attach in message.attachments:
                file_cache_path = os.path.join(
                    self._cache_path, f"{message_id}-{attach.filename}"
                )
                try:
                    res = session.get(attach.url, allow_redirects=True)
                    with open(file_cache_path, "wb") as outFile:
                        outFile.write(res.content)

                    attachments.append(file_cache_path)

                except Exception:
                    print(f"Skipping file at {attach.url}")

            pack = MessagePack(
                author_name,
                author_id,
                message_id,
                content,
                pinned,
                embeds,
                reactions,
                time,
                attachments,
            )
            self._history.append(pack)

            current += 1
            if current % report_freq == 0 and self._progress_ctx is not None:
                bar = self._build_progress_bar(current, total)
                progress = await progress.edit(
                    content=f"**History Compiling Progress**\n{bar}"
                )

        if self._progress_ctx is not None:
            await progress.delete()

    async def send(self, channel_id: int):
        """Send to another channel"""

        channel = self._bot.get_channel(channel_id)
        assert channel is not None

        total = len(self._history)
        current = 0
        report_freq = max(1, total // PROGRESS_BAR_LEN)

        if self._progress_ctx is not None:
            bar = self._build_progress_bar(current, total)
            progress = await self._progress_ctx.reply(
                f"**History Transfer Progress**\n{bar}"
            )

        lastauthor = 0
        lasttime = datetime.datetime(2000, 1, 1)

        for pack in self._history:
            author = self._bot.get_user(pack.author_id)

            files = []
            for path in pack.attachments:
                filename = path.replace(f"{pack.message_id}-", "")
                files.append(discord.File(path, filename))

            if lastauthor != pack.author_id or (pack.time - lasttime).days > 0:
                embed = discord.Embed(
                    description=f"Sent on {pack.time.strftime('%m/%d/%Y, %H:%M:%S (UTC)')}"
                )
                embed.set_author(name=author.display_name, icon_url=author.avatar.url)
                await channel.send(silent=True, embed=embed)

            lastauthor = pack.author_id
            lasttime = pack.time

            msg = await channel.send(
                silent=True,
                files=files,
                embeds=pack.embeds,
                content=pack.content,
            )

            for reaction in pack.reactions:
                await msg.add_reaction(reaction)

            if pack.pinned:
                await msg.pin()

            current += 1
            if current % report_freq == 0 and self._progress_ctx is not None:
                bar = self._build_progress_bar(current, total)
                progress = await progress.edit(
                    content=f"**History Transfer Progress**\n{bar}"
                )

        if self._progress_ctx is not None:
            await progress.delete()

    def zip(self) -> str:
        """Create zipfile and return zipfile path"""

        if not os.path.exists(self._cache_path):
            raise ""

        # compile history into json file
        history = []
        for pack in self._history:
            history.append(
                {
                    "author_name": pack.author_name,
                    "author_id": pack.author_id,
                    "message_id": pack.message_id,
                    "message_content": pack.content,
                    "is_pinned": pack.pinned,
                    "created_time": pack.time.strftime("%m/%d/%Y, %H:%M:%S (UTC)"),
                    "attached_files": pack.attachments,
                }
            )

        with open(os.path.join(self._cache_path, "index.json"), "w") as outFile:
            outFile.write(json.dumps(history, indent=4))

        # create zip file
        shutil.make_archive(self._cache_path, "zip", self._cache_path)

        return f"{self._cache_path}.zip"

    def cleanup(self):
        """Clean up local caches"""

        if os.path.exists(self._cache_path):
            shutil.rmtree(self._cache_path)

        if os.path.isfile(f"{self._cache_path}.zip"):
            os.remove(f"{self._cache_path}.zip")

    def _build_progress_bar(self, curr: int, total: int):
        num_bars = min(PROGRESS_BAR_LEN, total)
        bar = int(math.floor(curr / total * num_bars))

        return f"[{'=' * bar}{'>' * (num_bars-bar)}] {curr}/{total}"
