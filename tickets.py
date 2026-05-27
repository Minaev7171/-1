import discord
from discord.ext import commands
from discord import ui
import datetime
from utils.db import db

class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Открыть тикет", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        config = await db.get_guild_config(interaction.guild.id)
        category_id = config.get("ticket_category_id")
        category = interaction.guild.get_channel(category_id) if category_id else None
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await interaction.guild.create_text_channel(
            f"тикет-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )
        
        await db.create_ticket(interaction.guild.id, channel.id, interaction.user.id)
        
        embed = discord.Embed(title="Тикет открыт", description=f"Здравствуйте, {interaction.user.mention}! Чем мы можем вам помочь?")
        view = CloseTicketView()
        await channel.send(embed=embed, view=view)
        
        await interaction.response.send_message(f"Тикет создан: {channel.mention}", ephemeral=True)

class CloseTicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Закрыть тикет", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await db.close_ticket(interaction.channel.id)
        await interaction.response.send_message("Тикет будет закрыт через 5 секунд...")
        await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=5))
        await interaction.channel.delete()

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="панель_тикетов", help="Отправить панель для создания тикетов")
    @commands.has_permissions(administrator=True)
    async def ticket_panel(self, ctx):
        embed = discord.Embed(title="Поддержка", description="Нажмите на кнопку ниже, чтобы создать тикет.")
        view = TicketView()
        await ctx.send(embed=embed, view=view)

    @commands.command(name="настройка_тикетов", help="Создать категорию для тикетов")
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx):
        category = discord.utils.get(ctx.guild.categories, name="Tickets")
        if not category:
            category = await ctx.guild.create_category("Tickets")
            await ctx.send(f"Категория тикетов создана: {category.name}")
        else:
            await ctx.send(f"Категория тикетов уже существует: {category.name}")
        await db.update_guild_config(ctx.guild.id, {"ticket_category_id": category.id})

async def setup(bot):
    await bot.add_cog(Tickets(bot))
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
