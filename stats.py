import discord
from discord.ext import commands
from utils.db import db

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="статистика", help="Посмотреть статистику действий модерации")
    async def stats(self, ctx):
        stats_data = await db.get_stats(ctx.guild.id)
        if not stats_data or "actions" not in stats_data:
            return await ctx.send("Статистика для этого сервера пока не записана.")

        embed = discord.Embed(title=f"Статистика модерации для {ctx.guild.name}", color=discord.Color.green())
        actions = stats_data["actions"]
        
        # Перевод названий действий
        translation = {
            "kick": "Кики",
            "ban": "Баны",
            "timeout": "Тайм-ауты",
            "warn": "Предупреждения"
        }
        
        for action, count in actions.items():
            name = translation.get(action, action.capitalize())
            embed.add_field(name=name, value=count, inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))
