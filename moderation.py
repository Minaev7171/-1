import discord
from discord.ext import commands
from discord import app_commands
import datetime
from utils.db import db

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        config = await db.get_guild_config(ctx.guild.id)
        return config.get("moderation_enabled", True)

    @commands.command(name="кик", help="Исключить участника с сервера")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await db.increment_stat(ctx.guild.id, "kick")
        await ctx.send(f"Участник {member.mention} был исключен. Причина: {reason}")

    @commands.command(name="бан", help="Забанить участника на сервере")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await db.increment_stat(ctx.guild.id, "ban")
        await ctx.send(f"Участник {member.mention} был забанен. Причина: {reason}")

    @commands.command(name="мут", help="Выдать тайм-аут участнику (в минутах)")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason=None):
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        await db.increment_stat(ctx.guild.id, "timeout")
        await ctx.send(f"Участник {member.mention} отправлен в тайм-аут на {minutes} минут. Причина: {reason}")

    @commands.command(name="варн", help="Выдать предупреждение участнику")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        await db.add_warn(ctx.guild.id, member.id, ctx.author.id, reason)
        await db.increment_stat(ctx.guild.id, "warn")
        await ctx.send(f"Участнику {member.mention} выдано предупреждение. Причина: {reason}")

    @commands.command(name="варны", help="Посмотреть предупреждения участника")
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx, member: discord.Member):
        warns = await db.get_warns(ctx.guild.id, member.id)
        if not warns:
            return await ctx.send(f"У {member.mention} нет предупреждений.")
        
        embed = discord.Embed(title=f"Предупреждения для {member}", color=discord.Color.orange())
        for i, warn in enumerate(warns, 1):
            moderator = self.bot.get_user(warn['moderator_id']) or f"ID: {warn['moderator_id']}"
            embed.add_field(name=f"Предупреждение {i}", value=f"Причина: {warn['reason']}\nМодератор: {moderator}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="очистить", help="Удалить указанное количество сообщений")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Удалено {amount} сообщений.", delete_after=5)

    @commands.command(name="настройка_мод", help="Автоматическая настройка ролей и каналов модерации")
    @commands.has_permissions(administrator=True)
    async def setup_mod(self, ctx):
        mod_role = discord.utils.get(ctx.guild.roles, name="Moderator")
        if not mod_role:
            mod_role = await ctx.guild.create_role(name="Moderator", color=discord.Color.blue())
            await ctx.send("Создана роль 'Moderator'.")
        
        log_channel = discord.utils.get(ctx.guild.channels, name="mod-logs")
        if not log_channel:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                mod_role: discord.PermissionOverwrite(read_messages=True)
            }
            log_channel = await ctx.guild.create_text_channel("mod-logs", overwrites=overwrites)
            await ctx.send("Создан канал 'mod-logs'.")
            await db.update_guild_config(ctx.guild.id, {"log_channel_id": log_channel.id})

async def setup(bot):
    await bot.add_cog(Moderation(bot))
