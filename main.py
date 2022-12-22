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
Hey all 👋

I am a Bot, and I'm so glad to be part of this server!

I can help automate pretty much anything
I am created with code so the possibilities are endless

My current name is ${bot} but don't worry we change it

I was created by ${abe} so tag him and message him with all your questions and comments

I have not yet been deployed yet so I only work when <@834216780586287146> has me running on his laptop, but no woories cause I'm real easy to deploy

To demonstrate I created this grey button which assigns the ${podcast} role 
"""
)

message_content_2 = Template(
    """
We can have an additional message after the button

I'll end off with a link button to my source code on GitHub
"""
)


# This is the list of role IDs that will be added as buttons.
role_ids = [
    (1039995112207429805, "💙"),  # Podcast
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

class SourceCodeButton(discord.ui.View):
    def __init__(self):
        super().__init__()

        url = "https://github.com/abe-101/empathy-in-tech-discord-bot/blob/main/main.py"
        self.add_item(discord.ui.Button(label='GitHub', url=url))

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=commands.when_mentioned_or("?"),
            intents=intents,
            activity=discord.Game(name="💙 in 💻"),
        )
        self.color_to_style = {
            0: discord.ButtonStyle.secondary,  # gray
            1: discord.ButtonStyle.danger,  # red
            2: discord.ButtonStyle.blurple,  # purple
            3: discord.ButtonStyle.success,  # green
        }

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        # We recreate the view as we did in the /post command.
        view = discord.ui.View(timeout=None)
        # Make sure to set the guild ID here to whatever server you want the buttons in!
        guild = self.get_guild(826646363553923072)
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
        channel = self.get_channel(829853488925114408)

        # 1st message
        message_1_data = {
            "abe": guild.get_member(834216780586287146).mention,
            "bot": guild.get_member(1049717857111507055).mention,
            "podcast": guild.get_role(1039995112207429805).mention,
                }
        try:
            message_1 = await channel.fetch_message(1049737305503567882)
            await message_1.edit(
                content=message_content_1.substitute(message_1_data), view=view
            )
        except discord.errors.NotFound:
            await channel.send(
                content=message_content_1.substitute(message_1_data), view=view
            )
        # 2nd message
        message_2_data = {}
        try:
            message_2 = await channel.fetch_message(1049737308305358878)
            await message_2.edit(
                content=message_content_2.substitute(message_2_data), view=SourceCodeButton()
            )
        except discord.errors.NotFound:
            await channel.send(
                content=message_content_2.substitute(message_2_data), view=SourceCodeButton()
            )

    async def setup_hook(self) -> None:
        # Load cogs
        for file in os.listdir(f"./cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await bot.load_extension(f"cogs.{extension}")
                    print(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to load extension {extension}\n{exception}")


bot = Bot()


bot.run(DISCORD_TOKEN)
