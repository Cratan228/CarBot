import json
import discord
import requests
import random
from discord import Member
from discord import Reaction, Embed
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import has_permissions, MissingPermissions
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, create_button
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component
from discord_slash import cog_ext, SlashContext
from discord_slash.context import ComponentContext
from discord_slash.http import CustomRoute
from bs4 import BeautifulSoup
import asyncio
import os
import io

alphabet_emoji = {
    "regional_indicator_a": u"\U0001F1E6",
    "regional_indicator_b": u"\U0001F1E7",
    "regional_indicator_c": u"\U0001F1E8",
    "regional_indicator_d": u"\U0001F1E9",
    "regional_indicator_e": u"\U0001F1EA",
    "regional_indicator_f": u"\U0001F1EB",
    "regional_indicator_g": u"\U0001F1EC",
    "regional_indicator_h": u"\U0001F1ED",
    "regional_indicator_i": u"\U0001F1EE",
    "regional_indicator_j": u"\U0001F1EF",
    "regional_indicator_k": u"\U0001F1F0",
    "regional_indicator_l": u"\U0001F1F1",
    "regional_indicator_m": u"\U0001F1F2",
    "regional_indicator_n": u"\U0001F1F3",
    "regional_indicator_o": u"\U0001F1F4",
    "regional_indicator_p": u"\U0001F1F5",
    "regional_indicator_q": u"\U0001F1F6",
    "regional_indicator_r": u"\U0001F1F7",
    "regional_indicator_s": u"\U0001F1F8"
}


class Gallery(commands.Cog):
    """Commands used to search for a car"""
    path = os.path.dirname(os.path.realpath(__file__)) + "/"

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="gallery",
        description="Searches for the specified car on autoevolution and provides a photo gallery",
        options=[
            create_option(
                name="car_name",
                description="Car Name",
                option_type=3,
                required=True
            )
        ],
    )
    async def search(self, ctx: SlashContext, car_name: str):
        await ctx.defer()
        trans_table = {ord("é"): ord("e"), ord("è"): ord("e"), ord("ê"): ord("e"), ord("ë"): ord("e"),
                       ord("à"): ord("a"), ord("á"): ord("a")
            , ord("â"): ord("a"), ord("ä"): ord("a"), ord("ò"): ord("o"), ord("ó"): ord("o"), ord("ô"): ord("o"),
                       ord("ö"): ord("o"), ord("õ"): ord("o")
            , ord("ã"): ord("a"), ord("ñ"): ord("n"), ord("í"): ord("i"), ord("ï"): ord("i"), ord("ü"): ord("u"),
                       ord("ú"): ord("u")}

        tm_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

        search_name = car_name.split(" ")
        ns = ""
        for i in search_name:
            ns += i + "+"
        ns = ns[:-1]
        car_link = "https://www.autoevolution.com/search.php?t=cars&s=" + ns
        soup = BeautifulSoup(requests.get(car_link, headers=tm_headers).content, features="lxml")

        try:
            # Car Link Search
            links = soup.findAll("div", {"class": "srcar clearfix"})
            link_list = {}
            name_list = []
            counter = 0
            for l in links:
                counter += 1
                if counter < 20:
                    link = l.find("a")["href"]
                    name = l.find("a").text
                    name_list.append(name)
                    link_list[counter] = link
                else:
                    break

            # Error Check
            link = soup.find("div", {"class": "srcar clearfix"}).find("a")["href"]

            s = "Which car do you want to search?\n"

            if len(link_list) == 1:
                link = link_list[1]

            else:
                for i in range(len(name_list)):
                    s += f":{list(alphabet_emoji)[i]}:: **{name_list[i].capitalize()}**\n"
                choice = await ctx.send(s)

                for i in range(len(name_list)):
                    await choice.add_reaction(list(alphabet_emoji.values())[i])

                def r_check(reaction: Reaction, user: Member):
                    return reaction.message.id == choice.id and user == ctx.author and (
                                str(reaction.emoji) in list(alphabet_emoji.values()))

                try:
                    reaction, user = await ctx.bot.wait_for('reaction_add', check=r_check, timeout=15)
                    if reaction:
                        z = 0
                        for i in enumerate(alphabet_emoji.values()):
                            z += 1
                            if i[1] == str(reaction.emoji):
                                car = name_list[i[0]]
                                index = z
                    link = link_list[index]

                except asyncio.TimeoutError:
                    await ctx.send("Timeout!")
                    return

                await choice.edit(content=car)
                # for i in range(len(name_list)):
                #    await choice.remove_reaction(list(alphabet_emoji.values())[i])
                # await ctx.send(link)

        except AttributeError:
            await choice.delete()
            await ctx.send(f"No car found by the name `{car_name.title()}` in the database")
            return

        def get_car_pics(link):
            tm_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
            car_soup = BeautifulSoup(requests.get(link, headers=tm_headers).content, features="lxml")

            try:
                # Car Title
                car_title = car_soup.find("div", {"class": "container2 clearfix"}).find("a")["title"]

            except AttributeError:
                pass

            try:
                # Main Photo
                photo_link = car_soup.find("div", {"class": "galbig posrel"}).find("img")["src"]
                link_list = photo_link.split(" ")
                photo_link_final = "%20".join(link_list)

                # Photo Gallery
                photo_gallery = []
                photo_gallery_links = car_soup.find("div", {"class": "newsgal revgal carsgal"}).findAll("a", {"class": "s_gallery"})
                for i in photo_gallery_links:
                    new_pic = i.find("img")["src"]
                    photo_gallery.append(new_pic)

            except AttributeError:
                pass

            emb = discord.Embed(title=f"Photo Gallery for {car_title}", description="")
            emb.set_image(url=photo_link_final)
            return emb, photo_gallery

        embed, gallery_list = get_car_pics(link)
        buttons = [
            create_button(style=ButtonStyle.blue, emoji="⬅", custom_id="previous"),
            create_button(style=ButtonStyle.blue, emoji="➡", custom_id="next")
        ]
        action_row = create_actionrow(*buttons)
        gallery = await ctx.send(
            embed=embed,
            components=[action_row]
        )

        # time_left = 30
        pos = 0
        # n = 11

        def check(button):
            return button.author == ctx.author

        while True:
            try:
                button_ctx: ComponentContext = await wait_for_component(self.bot, components=action_row, timeout=60.0, check=check)

                # for i in range(1, n):
                    # if time_left >= 0:
            except asyncio.TimeoutError:
                await gallery.edit(embed=embed, components=None)
                break

            else:
                if button_ctx.custom_id == "previous":
                    pos -= 1
                    current_photo = gallery_list[pos]
                    embed.set_image(url=current_photo)
                    await gallery.edit(embed=embed, components=[action_row])
                    pass
                        # n += 1
                        # await button_ctx.edit_origin()
                        # await asyncio.sleep(3)
                elif button_ctx.custom_id == "next":
                    pos += 1
                    current_photo = gallery_list[pos]
                    embed.set_image(url=current_photo)
                    await gallery.edit(embed=embed, components=[action_row])
                    pass
                    # n += 1
                    # await button_ctx.edit_origin()
                    # await asyncio.sleep(3)
                # else:
                #    await asyncio.sleep(3)
                    # time_left -= 3
        # except asyncio.TimeoutError:
        #    await gallery.edit(embed=embed, components=[])
        #    return

def setup(bot):
    bot.add_cog(Gallery(bot))
