import json
import discord
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, create_button
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component
from discord_slash import cog_ext, SlashContext
from discord_slash.context import ComponentContext
from discord_slash.http import CustomRoute
import requests
import random
from discord import Member
from discord import Reaction, Embed
from discord.ext import commands
# from discord.utils import get
# from discord.ext.commands import has_permissions, MissingPermissions
from bs4 import BeautifulSoup
import asyncio
import os

import matplotlib
import matplotlib.pyplot as plt

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


class Overview(commands.Cog):
    """Commands used to search for a car"""
    path = os.path.dirname(os.path.realpath(__file__)) + "/"

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="overview",
        description="Searches for the specified car on autoevolution and provides an overview",
        options=[
            create_option(
                name="car_name",
                description="Car Name",
                option_type=3,
                required=True
            )
        ],
    )
    async def overview(self, ctx: SlashContext, car_name: str):
        await ctx.defer()
        msg = await ctx.send(f"<a:Loading:821934206254710875> Searching the overview for `{car_name}`.")
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

                await choice.delete()

        except AttributeError:
            await msg.delete()
            await ctx.send(f"No car found by the name `{car_name.title()}` in the database")
            return

        def get_car_overview(link):
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
            car_soup = BeautifulSoup(requests.get(link, headers=headers).content, features="lxml")

            try:
                # Car Title
                car_title = car_soup.find("div", {"class": "container2 clearfix"}).find("a")["title"]

            except AttributeError:
                pass

            try:
                # Photo
                photo_link = car_soup.find("div", {"class": "galbig posrel"}).find("img")["src"]
                link_list = photo_link.split(" ")
                photo_link_final = "%20".join(link_list)

            except AttributeError:
                pass

            try:
                headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
                soup = BeautifulSoup(requests.get(link, headers=headers).content, features="lxml")

                emb = discord.Embed(title=f"Overview of {car_title}", description="")

                # Car Category
                category_link = soup.find("div", {"class": "newstext modelbox"}).find("p", {"class": "mgbot_20 nomgtop"})
                category_list = str(category_link).split("<b>")[1:]
                category = {}

                for i in category_list:
                    name = i.split("</b>")[0]

                    if name == "Infotainment:":
                        info_list = soup.find("div", {"class": "newstext modelbox"}).findAll("img")
                        itdata = ""
                        for info in info_list:
                            img = (str(info).split('title="')[1].split(' align')[0]).strip('" width="16"/>')
                            itdata += (f"{img}\n")
                        category[name] = itdata

                    else:
                        info = i.split("</b>")[1]
                        if "<br/>" in info:
                            info = info.split("<br/>")[0]
                        category[name] = info

                s = ""
                for i in category:
                    if i == "Infotainment:":
                        s += (f"{i} {category[i]}").strip(" ")
                    else:
                        s += (f"{i} {category[i]}\n").strip(" ")
                s = s.replace("</p>", "").replace("Ã©", "é")
                emb.add_field(name="Car Category", value=s, inline=False)

                # Car Trivia
                trivia_link = soup.find("strong", {"class": "intro"})

                if trivia_link is not None:
                    trivia = str(trivia_link).split("</strong>")[0].split('<strong class="intro"')[1].strip(">")
                    emb.add_field(name="Car Trivia", value=trivia, inline=False)

                # Car Overview
                general_link = soup.find("div", {"class": "fl newstext modelcontainer"}).find("p")
                if general_link is not None:
                    try:
                        if "<br/>\n<br/>\r\n" not in general_link:
                            general = (str(general_link).split("<br/>\r\n"))[:2]
                            s = ""
                            for i in general:
                                s += (f"{i}\n\n").strip(" ").strip("<p>").replace("<br/>", "").replace("</p>", "")
                            emb.add_field(name="Car Overview", value=s, inline=False)
                        else:
                            general = (str(general_link).split("<br/>\n<br/>\r\n"))[:2]
                            s = ""
                            for i in general:
                                s += (f"{i}\n").strip(" ").strip("<p>").replace("<br/>", "").replace("</p>", "")
                            emb.add_field(name="Car Overview", value=s, inline=False)

                    except:
                        if "<br/>\n<br/>\r\n" not in general_link:
                            general = (str(general_link).split("<br/>\r\n"))[:1]
                            s = ""
                            for i in general:
                                s += (f"{i}\n\n").strip(" ").strip("<p>").replace("<br/>", "").replace("</p>", "")
                            emb.add_field(name="Car Overview", value=s, inline=False)
                        else:
                            general = (str(general_link).split("<br/>\n<br/>\r\n"))[:1]
                            s = ""
                            for i in general:
                                s += (f"{i}\n").strip(" ").strip("<p>").replace("<br/>", "").replace("</p>", "")
                            emb.add_field(name="Car Overview", value=s, inline=False)

                else:
                    general_link = soup.find("div", {"class": "fl newstext modelcontainer"})
                    try:
                        if "<br/>\n<br/>\r\n" not in general_link:
                            general = (str(general_link).split("<br/>\r\n"))[1:3]
                            s = ""
                            for i in general:
                                s += (f"{i}\n\n").strip(" ").strip("<p>").replace("<br/>", "").replace("</p>", "")
                            emb.add_field(name="Car Overview", value=s, inline=False)
                        else:
                            general = (str(general_link).split("<br/>\n<br/>\r\n"))[1:3]
                            s = ""
                            for i in general:
                                s += (f"{i}\n").strip(" ").strip("<p>").replace("<br/>", "").replace("</p>", "")
                            emb.add_field(name="Car Overview", value=s, inline=False)

                    except:
                        if "<br/>\n<br/>\r\n" not in general_link:
                            general = (str(general_link).split("<br/>\r\n"))[1:2]
                            s = ""
                            for i in general:
                                s += (f"{i}\n\n").strip(" ").strip("<p>").replace("<br/>", "").replace("</p>", "")
                            emb.add_field(name="Car Overview", value=s, inline=False)
                        else:
                            general = (str(general_link).split("<br/>\n<br/>\r\n"))[1:2]
                            s = ""
                            for i in general:
                                s += (f"{i}\n").strip(" ").strip("<p>").replace("<br/>", "").replace("</p>", "")
                            emb.add_field(name="Car Overview", value=s, inline=False)

                # Car Engine Overall
                engine_info = soup.find("span", {"class": "col-green2"})
                engine = str(engine_info).split("</span")[0].strip('<span class="col-green2">')
                if engine.startswith("."):
                    corr_engine = "2" + engine
                    emb.add_field(name="Engine", value=corr_engine, inline=False)
                else:
                    emb.add_field(name="Engine", value=engine, inline=False)

                # Embed Final cuts
                emb.add_field(name="Car Link", value=link, inline=False)
                emb.set_image(url=photo_link_final)
                emb.set_footer(text=f"Requested by {ctx.author.name}")

            except AttributeError:
                pass

            return emb

        embed = get_car_overview(link)
        await msg.edit(content="<a:Loading:821934206254710875> Gathering information for the overview...")
        await asyncio.sleep(3)
        await msg.delete()
        await ctx.send(content=None, embed=embed)


def setup(bot):
    bot.add_cog(Overview(bot))
