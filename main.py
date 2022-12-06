# This example requires the 'message_content' privileged intent to function.
import os

import discord
from string import Template
from discord.ext import commands
from dotenv import load_dotenv

import datetime

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

message_content_1 = Template(
    """
First Message
"""
)

message_content_2 = Template(
    """
Second Message after buttons
"""
)


# This is the list of role IDs that will be added as buttons.
role_ids = [
    (<ROLE_ID>, "🏄"),  # Role name
]


class RoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role, emoji, style=discord.ButtonStyle.primary):
        """A button for one role. `custom_id` is needed for persistent views."""
        super().__init__(
            label=role.name, style=style, custom_id=str(role.id), emoji=emoji
        )

    async def callback(self, interaction: discord.Interaction):
        """
        This function will be called any time a user clicks on this button.
        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            The interaction object that was created when a user clicks on a button.
        """
        # Get the user who clicked the button.
        user = interaction.user
        # Get the role this button is for (stored in the custom ID).
        role = interaction.guild.get_role(int(self.custom_id))

        if role is None:
            # If the specified role does not exist, return nothing.
            # Error handling could be done here.
            return

        # Add the role and send a response to the user ephemerally (hidden to other users).
        if role not in user.roles:
            # Give the user the role if they don't already have it.
            await user.add_roles(role)
            await interaction.response.send_message(
                f"🎉 You have been given the role {role.mention}!",
                ephemeral=True,
            )
            print(f"{user} joined {role}")
        else:
            # Otherwise, take the role away from the user.
            await user.remove_roles(role)
            await interaction.response.send_message(
                f"❌ The {role.mention} role has been taken from you!",
                ephemeral=True,
            )
            print(f"{user} left {role}")


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            activity=discord.Game(name="💙 in 💻"),
        )
        self.color_to_style = {
            0: discord.ButtonStyle.danger,  # red
            1: discord.ButtonStyle.blurple,  # purple
            2: discord.ButtonStyle.success,  # green
            3: discord.ButtonStyle.secondary,  # gray
        }

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        # We recreate the view as we did in the /post command.
        view = discord.ui.View(timeout=None)
        # Make sure to set the guild ID here to whatever server you want the buttons in!
        guild = self.get_guild(<SERVER_GUILD>)
        count = 0
        for role_id, emoji in role_ids:
            role = guild.get_role(role_id)
            view.add_item(
                RoleButton(
                    role,
                    discord.PartialEmoji(name=emoji),
                    self.color_to_style[count % 4],
                )
            )
            count += 1

        # Add the view to the bot so that it will watch for button interactions.
        self.add_view(view)
        channel = self.get_channel(<CHANNEL_ID>)

        # 1st message
        try:
            message_1 = await channel.fetch_message(<MESSAGE_ID>)
            await message_1.edit(
                content=message_content_1.substitute(rules=rules), view=view
            )
        except discord.errors.NotFound:
            await channel.send(
                content=message_content_1.substitute(rules=rules), view=view
            )
        # 2nd message
        try:
            message_2 = await channel.fetch_message(<MESSAGE_ID>)
            await message_2.edit(
                content=message_content_2.substitute(intro_circle=intro_circle)
            )
        except discord.errors.NotFound:
            await channel.send(
                content=message_content_2.substitute(intro_circle=intro_circle)
            )


bot = Bot()


bot.run(DISCORD_TOKEN)
