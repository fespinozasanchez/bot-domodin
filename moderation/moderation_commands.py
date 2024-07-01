import discord
from discord.ext import commands
import asyncio

# IDs de los usuarios autorizados para ejecutar comandos de moderación
AUTHORIZED_USERS = {278404222339252225, 276807542229958656,
                    429798122768564225, 458802974681071628}


class ModerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.muted_members = {}  # Dictionary to keep track of muted members and their roles

    async def cog_check(self, ctx):
        return ctx.author.id in AUTHORIZED_USERS

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a member from the server."""
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned for {reason}.')

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member from the server."""
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked for {reason}.')

    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int = 0, *, reason=None):
        """Mute a member in the server for a specific duration in minutes."""
        if member.id in self.muted_members:
            await ctx.send(f'{member.mention} is already muted.')
            return

        # Save the member's current roles
        self.muted_members[member.id] = [
            role for role in member.roles if role != ctx.guild.default_role]

        # Attempt to remove all roles from the member
        try:
            await member.remove_roles(*self.muted_members[member.id], reason=reason)
            await ctx.send(f'{member.mention} has been muted for {duration} minutes. Reason: {reason}')
        except discord.Forbidden:
            await ctx.send(f"Failed to mute {member.mention}. The bot doesn't have enough permissions.")
            return

        if duration > 0:
            await asyncio.sleep(duration * 60)
            await self.unmute_member(ctx, member)

    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmute a member in the server."""
        await self.unmute_member(ctx, member)

    async def unmute_member(self, ctx, member):
        if member.id not in self.muted_members:
            await ctx.send(f'{member.mention} is not currently muted.')
            return

        # Restore the member's roles
        try:
            await member.add_roles(*self.muted_members[member.id])
            del self.muted_members[member.id]
            await ctx.send(f'{member.mention} has been unmuted.')
        except discord.Forbidden:
            await ctx.send(f"Failed to unmute {member.mention}. The bot doesn't have enough permissions.")


async def setup(bot):
    await bot.add_cog(ModerationCommands(bot))
