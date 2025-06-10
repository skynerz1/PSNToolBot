import discord
import os
from discord.ext import commands
from discord import app_commands  # استخدم app_commands بدل SlashCommandGroup و Option
from api.common import APIError
from api.psn import PSN, PSNRequest

valid_regions = [
    "ar-AE", "ar-BH", "ar-KW", "ar-LB", "ar-OM", "ar-QA", "ar-SA", "ch-HK", "ch-TW", "cs-CZ",
    # ... باقي المناطق
]

# تقسيم المناطق إلى مجموعات من 5 وليس 10
valid_regionsShow = [valid_regions[i:i + 5] for i in range(0, len(valid_regions), 5)]
valid_regionsShow = "\n".join([", ".join(sublist) for sublist in valid_regionsShow])

invalid_region = discord.Embed(
    title="Error",
    description=f"Invalid region, make sure you have the last two letters in uppercase. Here are all valid regions:\n```{valid_regionsShow}```",
    color=discord.Color.red()
)

token_desc = "pdccws_p cookie"
id_desc = "ID from psprices product_id command"
region_desc = "For example 'en-US', check 'playstation.com'"

class PSNCog(commands.Cog):
    def __init__(self, secret: str, bot: commands.Bot) -> None:
        self.bot = bot
        self.api = PSN(secret)

    psn_group = app_commands.Group(name="psn", description="PSN commands")

    @psn_group.command(name="check_avatar", description="Checks an avatar for you.")
    @app_commands.describe(
        pdccws_p=token_desc,
        product_id=id_desc,
        region=region_desc
    )
    async def check_avatar(
        self,
        interaction: discord.Interaction,
        pdccws_p: str,
        product_id: str,
        region: str,
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        if region not in valid_regions:
            await interaction.followup.send(embed=invalid_region, ephemeral=True)
            return

        request = PSNRequest(
            pdccws_p=pdccws_p,
            region=region,
            product_id=product_id
        )

        try:
            avatar_url = await self.api.check_avatar(request)
        except APIError as e:
            embed_error = discord.Embed(
                title="Error",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed_error, ephemeral=True)
            return

        embed_success = discord.Embed(
            title="Success",
            description="Found your avatar.",
            color=discord.Color.blue()
        )
        embed_success.set_image(url=avatar_url)
        await interaction.followup.send(embed=embed_success, ephemeral=True)

    @psn_group.command(name="add_avatar", description="Adds the avatar you input into your cart.")
    @app_commands.describe(
        pdccws_p=token_desc,
        product_id=id_desc,
        region=region_desc
    )
    async def add_avatar(
        self,
        interaction: discord.Interaction,
        pdccws_p: str,
        product_id: str,
        region: str,
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        if region not in valid_regions:
            await interaction.followup.send(embed=invalid_region, ephemeral=True)
            return

        request = PSNRequest(
            pdccws_p=pdccws_p,
            region=region,
            product_id=product_id
        )

        try:
            await self.api.add_to_cart(request)
        except APIError as e:
            embed_error = discord.Embed(
                title="Error",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed_error, ephemeral=True)
            return

        embed_success = discord.Embed(
            title="Success",
            description=f"{product_id} added to cart.",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed_success, ephemeral=True)

    @psn_group.command(name="remove_avatar", description="Removes the avatar you input from your cart.")
    @app_commands.describe(
        pdccws_p=token_desc,
        product_id=id_desc,
        region=region_desc
    )
    async def remove_avatar(
        self,
        interaction: discord.Interaction,
        pdccws_p: str,
        product_id: str,
        region: str,
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        if region not in valid_regions:
            await interaction.followup.send(embed=invalid_region, ephemeral=True)
            return

        request = PSNRequest(
            pdccws_p=pdccws_p,
            region=region,
            product_id=product_id
        )

        try:
            await self.api.remove_from_cart(request)
        except APIError as e:
            embed_error = discord.Embed(
                title="Error",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed_error, ephemeral=True)
            return

        embed_success = discord.Embed(
            title="Success",
            description=f"{product_id} removed from cart.",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed_success, ephemeral=True)

    @psn_group.command(name="account_id", description="Gets the account ID from a PSN username.")
    async def account_id(
        self,
        interaction: discord.Interaction,
        username: str
    ) -> None:
        await interaction.response.defer()

        try:
            accid = await self.api.obtain_account_id(username)
        except APIError as e:
            embed_error = discord.Embed(
                title="Error",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed_error)
            return

        embed_success = discord.Embed(
            title=username,
            description=f"**{accid}**",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed_success)

async def setup(bot: commands.Bot) -> None:
    bot.add_cog(PSNCog(os.getenv("NPSSO"), bot))
