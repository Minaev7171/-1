import discord
from discord.ext import commands
from utils.db import db

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild):
        config = await db.get_guild_config(guild.id)
        channel_id = config.get("log_channel_id")
        if channel_id:
            return guild.get_channel(channel_id)
        return None

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        channel = await self.get_log_channel(message.guild)
        if channel:
            embed = discord.Embed(title="Сообщение удалено", color=discord.Color.red())
            embed.add_field(name="Автор", value=message.author)
            embed.add_field(name="Канал", value=message.channel.mention)
            embed.add_field(name="Содержание", value=message.content or "Нет содержания", inline=False)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        channel = await self.get_log_channel(before.guild)
        if channel:
            embed = discord.Embed(title="Сообщение изменено", color=discord.Color.blue())
            embed.add_field(name="Автор", value=before.author)
            embed.add_field(name="Канал", value=before.channel.mention)
            embed.add_field(name="До", value=before.content, inline=False)
            embed.add_field(name="После", value=after.content, inline=False)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = await self.get_log_channel(member.guild)
        if channel:
            await channel.send(f"📥 {member.mention} зашел на сервер.")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = await self.get_log_channel(member.guild)
        if channel:
            await channel.send(f"📤 {member.name} покинул сервер.")

async def setup(bot):
    await bot.add_cog(Logs(bot))
