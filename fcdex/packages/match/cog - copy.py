import logging
import random
import sys
from typing import TYPE_CHECKING, Dict
from dataclasses import dataclass, field

import discord
from discord import app_commands
from discord.ext import commands

import asyncio
import io

from ballsdex.core.models import (
    Ball,
    BallInstance,
    Player
)
from ballsdex.core.models import balls as countryballs
from ballsdex.settings import settings

from ballsdex.core.utils.transformers import (
    BallInstanceTransform,
    BallEnabledTransform
)

from ballsdex.packages.match.xe_battle_lib import (
    BattleBall,
    BattleInstance,
    gen_battle,
)

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger("ballsdex.packages.match")

battles = []

@dataclass
class GuildBattle:
    interaction: discord.Interaction

    author: discord.Member
    opponent: discord.Member

    author_ready: bool = False
    opponent_ready: bool = False

    battle: BattleInstance = field(default_factory=BattleInstance)


def gen_deck(balls) -> str:
    """Generates a text representation of the player's deck."""
    if not balls:
        return "Empty"
    deck = "\n".join(
        [
            f"- {ball.emoji} {ball.name} (DEF: {ball.defense} | ATK: {ball.attack})"
            for ball in balls
        ]
    )
    if len(deck) > 1024:
        return deck[0:951] + '\n<truncated due to discord limits, the rest of your balls are still here>'
    return deck

def update_embed(
    author_balls, opponent_balls, author, opponent, author_ready, opponent_ready
) -> discord.Embed:
    """Creates an embed for the battle setup phase."""
    embed = discord.Embed(
        title=f"{settings.plural_collectible_name.title()} Match Overview",
        description=(
            f"Add or remove {settings.plural_collectible_name} you want to propose to the other player using the "
            "'/match add' and '/match remove' commands. Once you've finished, "
            "click the tick button to start the match."
        ),
        color=discord.Colour.blurple(),
    )

    author_emoji = ":white_check_mark:" if author_ready else ""
    opponent_emoji = ":white_check_mark:" if opponent_ready else ""

    embed.add_field(
        name=f"{author_emoji} {author}'s lineup:",
        value=gen_deck(author_balls),
        inline=True,
    )
    embed.add_field(
        name=f"{opponent_emoji} {opponent}'s lineup:",
        value=gen_deck(opponent_balls),
        inline=True,
    )
    return embed


def create_disabled_buttons() -> discord.ui.View:
    """Creates a view with disabled start and cancel buttons."""
    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            style=discord.ButtonStyle.success, emoji="✔", label="Ready", disabled=True
        )
    )
    view.add_item(
        discord.ui.Button(
            style=discord.ButtonStyle.danger, emoji="✖", label="Cancel", disabled=True
        )
    )


def fetch_battle(user: discord.User | discord.Member):
    """
    Fetches a battle based on the user provided.

    Parameters
    ----------
    user: discord.User | discord.Member
        The user you want to fetch the battle from.
    """
    found_battle = None

    for battle in battles:
        if user not in (battle.author, battle.opponent):
            continue

        found_battle = battle
        break

    return found_battle


class Match(commands.GroupCog):
    """
    Head to head match with your clubballs!
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot

    async def start_battle(self, interaction: discord.Interaction):
        guild_battle = fetch_battle(interaction.user)

        if guild_battle is None:
            await interaction.response.send_message(
                "You aren't a part of this match.", ephemeral=True
            )
            return
        
        # Set the player's readiness status

        if interaction.user == guild_battle.author:
            guild_battle.author_ready = True
        elif interaction.user == guild_battle.opponent:
            guild_battle.opponent_ready = True
        # If both players are ready, start the battle

        if guild_battle.author_ready and guild_battle.opponent_ready:
            if not (guild_battle.battle.p1_balls and guild_battle.battle.p2_balls):
                await interaction.response.send_message(
                    f"Both players must add {settings.plural_collectible_name}!"
                )
                return
            new_view = create_disabled_buttons()
            battle_log = "\n".join(gen_battle(guild_battle.battle))

            embed = discord.Embed(
                title=f"{settings.plural_collectible_name.title()} Match Overview",
                description=f"Match between {guild_battle.author.mention} and {guild_battle.opponent.mention}",
                color=discord.Color.green(),
            )
            embed.add_field(
                name=f"{guild_battle.author}'s lineup:",
                value=gen_deck(guild_battle.battle.p1_balls),
                inline=True,
            )
            embed.add_field(
                name=f"{guild_battle.opponent}'s lineup:",
                value=gen_deck(guild_battle.battle.p2_balls),
                inline=True,
            )
            embed.add_field(
                name="Winner:",
                value=f"{guild_battle.battle.winner} - Round: {guild_battle.battle.turns}",
                inline=False,
            )
            embed.set_footer(text="Match log is attached.")

            await interaction.response.defer()
            await interaction.message.edit(
                content=f"{guild_battle.author.mention} vs {guild_battle.opponent.mention}",
                embed=embed,
                view=new_view,
                attachments=[
                    discord.File(io.StringIO(battle_log), filename="match-log.txt")
                ],
            )
            battles.pop(battles.index(guild_battle))
        else:
            # One player is ready, waiting for the other player

            await interaction.response.send_message(
                f"Done! Waiting for the other player to press 'Ready'.", ephemeral=True
            )

            author_emoji = (
                ":white_check_mark:" if interaction.user == guild_battle.author else ""
            )
            opponent_emoji = (
                ":white_check_mark:"
                if interaction.user == guild_battle.opponent
                else ""
            )

            embed = discord.Embed(
                title=f"{settings.plural_collectible_name.title()} Match Overview",
                description=(
                    f"Add or remove {settings.plural_collectible_name} you want to propose to the other player using the "
                    "'/match add' and '/match remove' commands. Once you've finished, "
                    "click the tick button to start the match."
                ),
                color=discord.Colour.blurple(),
            )

            embed.add_field(
                name=f"{author_emoji} {guild_battle.author.name}'s lineup:",
                value=gen_deck(guild_battle.battle.p1_balls),
                inline=True,
            )
            embed.add_field(
                name=f"{opponent_emoji} {guild_battle.opponent.name}'s lineup:",
                value=gen_deck(guild_battle.battle.p2_balls),
                inline=True,
            )

            await guild_battle.interaction.edit_original_response(embed=embed)

    async def cancel_battle(self, interaction: discord.Interaction):
        guild_battle = fetch_battle(interaction.user)

        if guild_battle is None:
            await interaction.response.send_message(
                "You aren't a part of this match!", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"{settings.plural_collectible_name.title()} Match Overview",
            description="The match has been cancelled.",
            color=discord.Color.red(),
        )
        embed.add_field(
            name=f":no_entry_sign: {guild_battle.author}'s lineup:",
            value=gen_deck(guild_battle.battle.p1_balls),
            inline=True,
        )
        embed.add_field(
            name=f":no_entry_sign: {guild_battle.opponent}'s lineup:",
            value=gen_deck(guild_battle.battle.p2_balls),
            inline=True,
        )

        try:
            await interaction.response.defer()
        except discord.errors.InteractionResponded:
            pass

        await interaction.message.edit(embed=embed, view=create_disabled_buttons())
        battles.pop(battles.index(guild_battle))

    @app_commands.command()
    async def challenge(self, interaction: discord.Interaction, opponent: discord.Member):
        """
        Starts a match with a chosen player.

        Parameters
        ----------
        opponent: discord.Member
            The user you want to challenge to a match.
        """
        if opponent.bot:
            await interaction.response.send_message(
                "You can't play a match against bots.", ephemeral=True,
            )
            return
        
        if opponent.id == interaction.user.id:
            await interaction.response.send_message(
                "You can't play a match against yourself.", ephemeral=True,
            )
            return

        if fetch_battle(opponent) is not None:
            await interaction.response.send_message(
                "That player is already in a match.", ephemeral=True,
            )
            return

        if fetch_battle(interaction.user) is not None:
            await interaction.response.send_message(
                "You are already in a match.", ephemeral=True,
            )
            return
        
        battles.append(GuildBattle(interaction, interaction.user, opponent))

        embed = update_embed([], [], interaction.user.name, opponent.name, False, False)

        start_button = discord.ui.Button(
            style=discord.ButtonStyle.success, emoji="✔", label="Ready"
        )
        cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.danger, emoji="✖", label="Cancel"
        )

        # Set callbacks

        start_button.callback = self.start_battle
        cancel_button.callback = self.cancel_battle

        view = discord.ui.View(timeout=None)

        view.add_item(start_button)
        view.add_item(cancel_button)

        await interaction.response.send_message(
            f"Hey, {opponent.mention}, {interaction.user.name} is challenging you to a match!",
            embed=embed,
            view=view,
        )

    async def add_balls(self, interaction: discord.Interaction, countryballs):
        guild_battle = fetch_battle(interaction.user)

        if guild_battle is None:
            await interaction.response.send_message(
                "You aren't a part of a match!", ephemeral=True
            )
            return
        
        if interaction.guild_id != guild_battle.interaction.guild_id:
            await interaction.response.send_message(
                "You must be in the same server as your match to use commands.", ephemeral=True
            )
            return

        # Check if the user is already ready

        if (interaction.user == guild_battle.author and guild_battle.author_ready) or (
            interaction.user == guild_battle.opponent and guild_battle.opponent_ready
        ):
            await interaction.response.send_message(
                f"You cannot change your {settings.plural_collectible_name} as you are already ready.", ephemeral=True
            )
            return
        # Determine if the user is the author or opponent and get the appropriate ball list

        user_balls = (
            guild_battle.battle.p1_balls
            if interaction.user == guild_battle.author
            else guild_battle.battle.p2_balls
        )
        # Create the BattleBall instance

        for countryball in countryballs:
            ball = BattleBall(
                countryball.countryball.country,
                interaction.user.name,
                countryball.health,
                countryball.attack,
                self.bot.get_emoji(countryball.countryball.emoji_id),
            )

            # Check if ball has already been added

            if len(user_balls) > 1:
                yield True
                continue
            
            user_balls.append(ball)
            yield False

        # Update the battle embed for both players

        await guild_battle.interaction.edit_original_response(
            embed=update_embed(
                guild_battle.battle.p1_balls,
                guild_battle.battle.p2_balls,
                guild_battle.author.name,
                guild_battle.opponent.name,
                guild_battle.author_ready,
                guild_battle.opponent_ready,
            )
        )

    async def remove_balls(self, interaction: discord.Interaction, countryballs):
        guild_battle = fetch_battle(interaction.user)

        if guild_battle is None:
            await interaction.response.send_message(
                "You aren't a part of a match!", ephemeral=True
            )
            return
        
        if interaction.guild_id != guild_battle.interaction.guild_id:
            await interaction.response.send_message(
                "You must be in the same server as your match to use commands.", ephemeral=True
            )
            return

        # Check if the user is already ready

        if (interaction.user == guild_battle.author and guild_battle.author_ready) or (
            interaction.user == guild_battle.opponent and guild_battle.opponent_ready
        ):
            await interaction.response.send_message(
                "You cannot change your clubball as you are already ready.", ephemeral=True
            )
            return
        # Determine if the user is the author or opponent and get the appropriate ball list

        user_balls = (
            guild_battle.battle.p1_balls
            if interaction.user == guild_battle.author
            else guild_battle.battle.p2_balls
        )
        # Create the BattleBall instance

        for countryball in countryballs:
            ball = BattleBall(
                countryball.countryball.country,
                interaction.user.name,
                countryball.health,
                countryball.attack,
                self.bot.get_emoji(countryball.countryball.emoji_id),
            )

            # Check if ball has already been added

            if ball not in user_balls:
                yield True
                continue
            
            user_balls.remove(ball)
            yield False

        # Update the battle embed for both players

        await guild_battle.interaction.edit_original_response(
            embed=update_embed(
                guild_battle.battle.p1_balls,
                guild_battle.battle.p2_balls,
                guild_battle.author.name,
                guild_battle.opponent.name,
                guild_battle.author_ready,
                guild_battle.opponent_ready,
            )
        )

    @app_commands.command()
    async def add(
        self, interaction: discord.Interaction, countryball: BallInstanceTransform
    ):
        """
        Adds a clubball to the match lineup.

        Parameters
        ----------
        countryball: Ball
            The clubball you want to add.
        """
        async for dupe in self.add_balls(interaction, [countryball]):
            if dupe:
                await interaction.response.send_message(
                    "You cannot add more than one clubball!", ephemeral=True
                )
                return

        # Construct the message
        attack = "{:+}".format(countryball.attack_bonus)
        health = "{:+}".format(countryball.health_bonus)

        await interaction.response.send_message(
            f"Added `#{countryball.id} {countryball.countryball.country} ({attack}%/{health}%)`!",
            ephemeral=True,
        )

    @app_commands.command()
    async def remove(
        self, interaction: discord.Interaction, countryball: BallInstanceTransform
    ):
        """
        Removes a clubball from the match lineup.

        Parameters
        ----------
        countryball: Ball
            The clubball you want to remove.
        """
        async for not_in_battle in self.remove_balls(interaction, [countryball]):
            if not_in_battle:
                await interaction.response.send_message(
                    f"You cannot remove a {settings.collectible_name} that is not in your lineup!", ephemeral=True
                )
                return

        attack = "{:+}".format(countryball.attack_bonus)
        health = "{:+}".format(countryball.health_bonus)

        await interaction.response.send_message(
            f"Removed `#{countryball.id} {countryball.countryball.country} ({attack}%/{health}%)`!",
            ephemeral=True,
        )
