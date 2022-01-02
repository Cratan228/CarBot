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
import requests
from bs4 import BeautifulSoup
import asyncio
import os

import matplotlib
import matplotlib.pyplot as plt

alphabet_emoji = {
        "regional_indicator_a":u"\U0001F1E6",
        "regional_indicator_b":u"\U0001F1E7",
        "regional_indicator_c":u"\U0001F1E8",
        "regional_indicator_d":u"\U0001F1E9",
        "regional_indicator_e":u"\U0001F1EA",
        "regional_indicator_f":u"\U0001F1EB",
        "regional_indicator_g":u"\U0001F1EC",
        "regional_indicator_h":u"\U0001F1ED",
        "regional_indicator_i":u"\U0001F1EE",
        "regional_indicator_j":u"\U0001F1EF",
        "regional_indicator_k":u"\U0001F1F0",
        "regional_indicator_l":u"\U0001F1F1",
        "regional_indicator_m":u"\U0001F1F2",
        "regional_indicator_n":u"\U0001F1F3",
        "regional_indicator_o":u"\U0001F1F4",
        "regional_indicator_p":u"\U0001F1F5",
        "regional_indicator_q":u"\U0001F1F6",
        "regional_indicator_r":u"\U0001F1F7",
        "regional_indicator_s":u"\U0001F1F8"
    }

class Search(commands.Cog):
    """Commands used to search for a car"""
    path = os.path.dirname(os.path.realpath(__file__)) + "/"

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="search",
        description="Searches for the specified car on autoevolution and provides specifications",
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
        msg = await ctx.send(f"<a:Loading:821934206254710875> Searching for `{car_name}`.")
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

        with open(f"{self.path}search.txt", "w") as f:
            json.dump(str(soup), f)

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
                    return reaction.message.id == choice.id and user == ctx.author and (str(reaction.emoji) in list(alphabet_emoji.values()))

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
                # await ctx.send(link)

        except AttributeError:
            await msg.delete()
            await ctx.send(f"No car found by the name `{car_name.title()}` in the database")
            return

        def get_car_info(link):
            tm_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
            car_soup = BeautifulSoup(requests.get(link, headers=tm_headers).content, features="lxml")

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

                emb = discord.Embed(title=f"Specs of {car_title}", description="")

                # Engine Specifications
                engine_spec = soup.find("dl", {"title": "General Specs"})
                engine_spec_list = str(engine_spec).split("<dt>")[1:]
                engine_specs = {}

                if engine_spec is not None:
                    for i in engine_spec_list:
                        name = i.split("</em>")[0].split("<em>")[1]
                        spec = i.split("<dd>")[1].split("</dd>")[0].strip()
                        if "<br/>" in spec:
                            specs_list = spec.split("<br/>")
                            spec = "\n".join(specs_list)
                        engine_specs[name] = spec

                    s = ""
                    for spec in engine_specs:
                        s += (f"{spec} - {engine_specs[spec]}\n").strip(">")
                    emb.add_field(name="General Specs", value=s, inline=False)

                # Performance Specifications
                performance_spec = soup.find("dl", {"title": "Performance Specs"})
                performance_spec_list = str(performance_spec).split("<dt>")[1:]
                performance_specs = {}

                if performance_spec is not None:
                    for i in performance_spec_list:
                        name = i.split("</em>")[0].split("<em")[1]
                        spec = i.split("<dd>")[1].split("</dd>")[0].strip()
                        if "<br/>" in spec:
                            specs_list = spec.split("<br/>")
                            spec = "\n".join(specs_list)
                        performance_specs[name] = spec

                    s = ""
                    for spec in performance_specs:
                        s += (f"{spec} - {performance_specs[spec]}\n").strip(">")
                    emb.add_field(name="Performance Specs", value=s, inline=False)

                # Transmission Specifications
                transmission_spec = soup.find("dl", {"title": "Transmission Specs"})
                transmission_spec_list = str(transmission_spec).split("<dt>")[1:]
                transmission_specs = {}

                if transmission_spec is not None:
                    for i in transmission_spec_list:
                        name = i.split("</em>")[0].split("<em")[1]
                        spec = i.split("<dd>")[1].split("</dd>")[0].strip()
                        if "<br/>" in spec:
                            specs_list = spec.split("<br/>")
                            spec = "\n".join(specs_list)
                        transmission_specs[name] = spec

                    s = ""
                    for spec in transmission_specs:
                        s += (f"{spec} - {transmission_specs[spec]}\n").strip(">")
                    emb.add_field(name="Transmission Specs", value=s, inline=False)

                # Brakes Specifications
                brake_spec = soup.find("dl", {"title": "Brakes Specs"})
                brake_spec_list = str(brake_spec).split("<dt>")[1:]
                brake_specs = {}

                if brake_spec is not None:
                    for i in brake_spec_list:
                        name = i.split("</em>")[0].split("<em")[1]
                        spec = i.split("<dd>")[1].split("</dd>")[0].strip()
                        if "<br/>" in spec:
                            specs_list = spec.split("<br/>")
                            spec = "\n".join(specs_list)
                        brake_specs[name] = spec

                    s = ""
                    for spec in brake_specs:
                        s += (f"{spec} - {brake_specs[spec]}\n").strip(">")
                    emb.add_field(name="Brakes Specs", value=s, inline=False)

                # Tires Specifications
                tire_spec = soup.find("dl", {"title": "Tires Specs"})
                tire_spec_list = str(tire_spec).split("<dt>")[1:]
                tire_specs = {}

                if tire_spec is not None:
                    for i in tire_spec_list:
                        name = i.split("</em>")[0].split("<em")[1]
                        spec = i.split("<dd>")[1].split("</dd>")[0].strip()
                        if "<br/>" in spec:
                            specs_list = spec.split("<br/>")
                            spec = "\n".join(specs_list)
                        tire_specs[name] = spec

                    s = ""
                    for spec in tire_specs:
                        s += (f"{spec} - {tire_specs[spec]}\n").strip(">")
                    emb.add_field(name="Tires Specs", value=s, inline=False)

                # Dimensions Specifications
                dimension_spec = soup.find("dl", {"title": "Dimensions Specs"})
                dimension_spec_list = str(dimension_spec).split("<dt>")[1:]
                dimension_specs = {}

                if dimension_spec is not None:
                    for i in dimension_spec_list:
                        name = i.split("</em>")[0].split("<em")[1]
                        spec = i.split("<dd>")[1].split("</dd>")[0].strip()
                        if "<br/>" in spec:
                            specs_list = spec.split("<br/>")
                            spec = "\n".join(specs_list)
                        dimension_specs[name] = spec

                    s = ""
                    for spec in dimension_specs:
                        s += (f"{spec} - {dimension_specs[spec]}\n").strip(">")
                    emb.add_field(name="Dimensions Specs", value=s, inline=False)

                # Weight Specifications
                weight_spec = soup.find("dl", {"title": "Weight Specs"})
                weight_spec_list = str(weight_spec).split("<dt>")[1:]
                weight_specs = {}

                if weight_spec is not None:
                    for i in weight_spec_list:
                        name = i.split("</em>")[0].split("<em")[1]
                        spec = i.split("<dd>")[1].split("</dd>")[0].strip()
                        if "<br>" in spec:
                            specs_list = spec.split("<br/>")
                            spec = "\n".join(specs_list)
                        weight_specs[name] = spec

                    s = ""
                    for spec in weight_specs:
                        s += (f"{spec} - {weight_specs[spec]}\n").strip(">")
                    emb.add_field(name="Weight Specs", value=s, inline=False)

                # Fuel Economy (NEDC) Specifications
                fuel_spec = soup.find("dl", {"title": "Fuel Economy (NEDC) Specs"})
                fuel_spec_list = str(fuel_spec).split("<dt>")[1:]
                fuel_specs = {}

                if fuel_spec is not None:
                    for i in fuel_spec_list:
                        name = i.split("</em>")[0].split("<em")[1]
                        spec = i.split("<dd>")[1].split("</dd>")[0].strip()
                        if "<br/>" in spec:
                            specs_list = spec.split("<br/>")
                            spec = "\n".join(specs_list)
                        fuel_specs[name] = spec

                    s = ""
                    for spec in fuel_specs:
                        s += (f"{spec} - {fuel_specs[spec]}\n").strip(">")
                    emb.add_field(name="Fuel Economy (NEDC) Specs", value=s, inline=False)

                # Power System Specifications
                ps_spec = soup.find("dl", {"title": "Power System Specs"})
                ps_spec_list = str(ps_spec).split("<dt>")[1:]
                ps_specs = {}

                if ps_spec is not None:
                    for i in ps_spec_list:
                        name = i.split("</em>")[0].split("<em")[1]
                        spec = i.split("<dd>")[1].split("</dd>")[0].strip()
                        if "<br/>" in spec:
                            specs_list = spec.split("<br/>")
                            spec = "\n".join(specs_list)
                        ps_specs[name] = spec

                    s = ""
                    for spec in ps_specs:
                        s += (f"{spec} - {ps_specs[spec]}\n").strip(">")
                    emb.add_field(name="Power System Specs", value=s, inline=False)

                emb.add_field(name="Car Link", value=link, inline=False)
                emb.set_image(url=photo_link_final)
                emb.set_footer(text=f"Requested by {ctx.author.name}")

            except AttributeError:
                pass

            return emb

        embed = get_car_info(link)
        await msg.edit(content="<a:Loading:821934206254710875> Gathering information for the specifications...")
        await asyncio.sleep(3)
        await msg.delete()
        await ctx.send(content=None, embed=embed)

def setup(bot):
    bot.add_cog(Search(bot))
