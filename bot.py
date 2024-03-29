import os
import discord
import traceback
from typing import List, Union
from discord.ext import commands, tasks
from pack import MessageHistory


class DiscordRelocate(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self._bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot {self._bot.user} is ready")
        await self.update_status()

    @tasks.loop(hours=1)
    async def update_status(self):
        await self._bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"{len(self._bot.guilds)} servers",
            )
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def servers(self, ctx: commands.Context):
        """List shared servers between me (as admin) and bot"""

        user = ctx.author
        shared_servers = user.mutual_guilds

        admin_shared_servers: List[discord.Guild] = []

        # check access
        for server in shared_servers:
            try:
                if self._validate_user(server, user.id):
                    admin_shared_servers.append(server)

            except Exception:
                traceback.print_exc()

        # check shared admin servers
        if len(admin_shared_servers) == 0:
            await ctx.reply(
                "Sorry, cannot find shared servers where you are administrator on!"
            )

        else:
            for idx in range(0, len(admin_shared_servers), 25):
                embed = discord.Embed(title="Shared admin servers")
                for server in admin_shared_servers[idx : (idx + 25)]:
                    name = server.name
                    if server.id == ctx.guild.id:
                        name = f"{name} (Current)"

                    embed.add_field(name=name, value=f"id = {server.id}", inline=False)

                await ctx.reply(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def channels(self, ctx: commands.Context, server_id: int):
        """List text channels on a server by server id"""

        user = ctx.author

        try:
            # validate server and access
            server = self._bot.get_guild(server_id)
            if server is None:
                raise Exception()

            if not self._validate_user(server, user.id):
                raise Exception()

            channels = server.text_channels

            # check text channels
            if len(channels) == 0:
                await ctx.reply("No text channels found on server!")

            else:
                for idx in range(0, len(channels), 25):
                    embed = discord.Embed(
                        title="Channels",
                        description=f"Channels on the server\n{server.name} (id = {server.id})",
                    )
                    for channel in channels[idx : (idx + 25)]:
                        embed.add_field(
                            name=channel.name,
                            value=f"id = {channel.id} ({channel.category if channel.category is None else channel.category.name})",
                            inline=False,
                        )

                    await ctx.reply(embed=embed)

        except Exception:
            traceback.print_exc()
            await ctx.reply("Invalid server id!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def pack(
        self, ctx: commands.Context, channel_id: Union[int, discord.TextChannel]
    ):
        """Pack everything in a channel (by channel id) and download as zip file"""

        if isinstance(channel_id, discord.TextChannel):
            channel_id = channel_id.id

        user = ctx.author
        history = MessageHistory(self._bot, channel_id, ctx)

        try:
            # valid channel
            if not self._validate_channel(channel_id):
                raise Exception()

            if not self._validate_user(
                self._bot.get_channel(channel_id).guild, user.id
            ):
                raise Exception()

            # build mesasge
            await history.build()

            zipfile = history.zip()

            if os.path.isfile(zipfile):
                await ctx.reply(
                    content="Here's the history zip file", file=discord.File(zipfile)
                )
            else:
                await ctx.reply("Failed to pack history into zip!")

        except Exception:
            traceback.print_exc()
            await ctx.reply("Invalid channel id!")

        finally:
            history.cleanup()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def relocate(
        self,
        ctx: commands.Context,
        from_id: Union[int, discord.TextChannel],
        to_id: Union[int, discord.TextChannel],
    ):
        """Relocate messages from one channel to another channel (by channel id)"""

        if isinstance(from_id, discord.TextChannel):
            from_id = from_id.id

        if isinstance(to_id, discord.TextChannel):
            to_id = to_id.id

        user = ctx.author
        history = MessageHistory(self._bot, from_id, ctx)

        try:
            # valid channels
            if not self._validate_channel(from_id):
                raise Exception()

            if not self._validate_user(self._bot.get_channel(from_id).guild, user.id):
                raise Exception()

            if not self._validate_channel(to_id):
                raise Exception()

            if not self._validate_user(self._bot.get_channel(to_id).guild, user.id):
                raise Exception()

            # build mesasge
            await history.build()

            # transfer messages
            await history.send(to_id)

            await ctx.reply("Relocated messages successfully!")

        except Exception:
            traceback.print_exc()
            await ctx.reply("Invalid channel id!")

        finally:
            history.cleanup()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(
        self,
        ctx: commands.Context,
        channel_id: Union[int, discord.TextChannel, None] = None,
    ):
        """Clear everything in channel by id (be cautious!)"""

        if isinstance(channel_id, discord.TextChannel):
            channel_id = channel_id.id

        try:
            if channel_id is None:
                channel = ctx.channel

            else:
                channel = self._bot.get_channel(channel_id)

            if channel is None:
                raise Exception()

            async for msg in channel.history(limit=None):
                await msg.delete()

        except Exception:
            traceback.print_exc()
            await ctx.reply("Invalid channel id!")

    def _validate_channel(self, channel_id: int) -> bool:
        channel = self._bot.get_channel(channel_id)
        if channel is None:
            return False

        if not isinstance(channel, discord.TextChannel):
            return False

        return True

    def _validate_user(self, server: discord.Guild, user_id: int) -> bool:
        member = server.get_member(user_id)
        if member is None:
            return False

        if not member.guild_permissions.administrator:
            return False

        return True
