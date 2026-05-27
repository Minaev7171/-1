import discord
from discord.ext import commands
from discord import ui
from utils.db import db

class ConfigView(ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=60)
        self.guild_id = guild_id

    @ui.button(label="Вкл/Выкл Модерацию", style=discord.ButtonStyle.secondary)
    async def toggle_mod(self, interaction: discord.Interaction, button: ui.Button):
        config = await db.get_guild_config(self.guild_id)
        current = config.get("moderation_enabled", True)
        await db.update_guild_config(self.guild_id, {"moderation_enabled": not current})
        status = "ВЫКЛЮЧЕНА" if current else "ВКЛЮЧЕНА"
        await interaction.response.send_message(f"Модерация теперь {status}.", ephemeral=True)

    @ui.select(cls=ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Выберите канал для логов")
    async def select_log_channel(self, interaction: discord.Interaction, select: ui.ChannelSelect):
        channel = select.values[0]
        await db.update_guild_config(self.guild_id, {"log_channel_id": channel.id})
        await interaction.response.send_message(f"Канал логов установлен на {channel.mention}.", ephemeral=True)

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="настройки", help="Открыть панель настроек сервера")
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        embed = discord.Embed(title="Настройки сервера", description="Используйте кнопки и меню ниже для настройки бота.")
        view = ConfigView(ctx.guild.id)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="сет_мод_роль", help="Установить роль модератора")
    @commands.has_permissions(administrator=True)
    async def set_mod_role(self, ctx, role: discord.Role):
        await db.update_guild_config(ctx.guild.id, {"mod_role_id": role.id})
        await ctx.send(f"Роль модератора установлена на {role.name}")

    @commands.command(name="сет_админ_роль", help="Установить роль администратора")
    @commands.has_permissions(administrator=True)
    async def set_admin_role(self, ctx, role: discord.Role):
        await db.update_guild_config(ctx.guild.id, {"admin_role_id": role.id})
        await ctx.send(f"Роль администратора установлена на {role.name}")

async def setup(bot):
    await bot.add_cog(Config(bot))
