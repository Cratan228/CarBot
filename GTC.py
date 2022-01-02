import json
import discord
import requests
import random
from discord import Member
from discord import Reaction, Embed
from discord.utils import get
from discord.ext.commands import has_permissions, MissingPermissions
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, create_button
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component
from discord_slash import cog_ext, SlashContext
from discord_slash.context import ComponentContext
from discord_slash.http import CustomRoute
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import has_permissions, MissingPermissions
from bs4 import BeautifulSoup
import asyncio
import os
import io

import matplotlib
import matplotlib.pyplot as plt

class GTC(commands.Cog):
    """Commands used to search for a car"""
    path = os.path.dirname(os.path.realpath(__file__)) + "/"

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="gtc",
        description="Gives you a 'guess the car' question, randomly selected from the autoevolution database",
    )
    async def gtc(self, ctx):
        msg = await ctx.send(f"<a:Loading:821934206254710875> Fetching a game...")
        trans_table = {ord("é"): ord("e"), ord("è"): ord("e"), ord("ê"): ord("e"), ord("ë"): ord("e"),
                           ord("à"): ord("a"), ord("á"): ord("a")
            , ord("â"): ord("a"), ord("ä"): ord("a"), ord("ò"): ord("o"), ord("ó"): ord("o"), ord("ô"): ord("o"),
                           ord("ö"): ord("o"), ord("õ"): ord("o")
            , ord("ã"): ord("a"), ord("ñ"): ord("n"), ord("í"): ord("i"), ord("ï"): ord("i"), ord("ü"): ord("u"),
                           ord("ú"): ord("u")}

        tm_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        car_database = "https://www.autoevolution.com/cars/"
        soup = BeautifulSoup(requests.get(car_database, headers=tm_headers).content, features="lxml")

        with open(f"{self.path}gtc.txt", "w") as f:
                json.dump(str(soup), f)

        def get_gtc():
            try:
                tm_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
                car_database = "https://www.autoevolution.com/cars/"
                soup = BeautifulSoup(requests.get(car_database, headers=tm_headers).content, features="lxml")

                emb = discord.Embed(title="Guess the Car!", description="", colour= discord.Colour.gold())

                raw_mfg_list = soup.findAll("div", {"class": "col2width fl bcol-white carman"})
                mfg_list = []
                for m in raw_mfg_list:
                    mfg_link = m.find("a")["href"]
                    mfg_list.append(mfg_link)
                mfg = random.choice(mfg_list)
                print(mfg)

                mfg_soup = BeautifulSoup(requests.get(mfg, headers=tm_headers).content, features="lxml")
                try:
                    try:
                        mfg_history = mfg_soup.find("div", {"class": "histbox sidebox2"}).find("div", {"class": "txt prodhist"})
                        mfg_hist_txt = (str(mfg_history)).split("<br/>")[0].replace("&nbsp;", "").replace('class="txt prodhist" itemprop="description">', "")
                        mfg_txt_final = mfg_hist_txt.strip("</div>").replace('div class="txt prodhist" itemprop="description">', "")
                        emb.add_field(name="Manufacturer Overview", value=mfg_txt_final, inline=False)

                    except:
                        pass

                    try:
                        mfg_logo = mfg_soup.find("div", {"class": "pic"}).find("img")["src"]
                    except:
                        mfg_logo = mfg_soup.find("div", {"class": "mpic fr"}).find("img")["src"]

                    try:
                        raw_car_list = mfg_soup.findAll("div", {"class": "carmod clearfix disc"})
                        car_list = []
                        car_img_list = {}
                        for cars in raw_car_list:
                            car = cars.find("a")
                            car_link = cars.find("a")["href"]
                            img_soup = BeautifulSoup(requests.get(car_link, headers=tm_headers).content, features="lxml")
                            raw_car_name = cars.find("a")["title"]  # (str(car).split("<h4"))[1]
                            car_name = (raw_car_name.split(" specs and photos"))[0]
                            car_img_link = img_soup.find("div", {"class": "col1width fl"}).find("img")["src"]
                            #raw_car_name = (str(car).split("<h4>"))[1]
                            #car_name = (raw_car_name.split("</h4>"))[0]
                            car_img_list[car_name] = car_img_link
                            car_list.append(car_name)

                        if len(car_list) == 1:
                            car = car_list[0]
                        else:
                            car = random.choice(car_list)
                        car_img = car_img_list[car]
                        print(car)

                    except:
                        pass

                except:
                    try:
                        mfg_history = mfg_soup.find("div", {"class": "histbox sidebox2"}).find("div", {"class": "txt prodhist"})
                        mfg_hist_txt = (str(mfg_history)).split("<br/>")[0].replace("&nbsp;", "").replace('class="txt prodhist" itemprop="description">', "")
                        mfg_txt_final = mfg_hist_txt.strip("</div>").replace('div class="txt prodhist" itemprop="description">', "").replace("&amp;", "&")
                        emb.add_field(name="Manufacturer Overview", value=mfg_txt_final, inline=False)

                    except:
                        pass

                    try:
                        mfg_logo = mfg_soup.find("div", {"class": "pic"}).find("img")["src"]
                    except:
                        mfg_logo = mfg_soup.find("div", {"class": "mpic fr"}).find("img")["src"]

                    raw_car_list = mfg_soup.findAll("div", {"class": "carmod clearfix "})
                    car_list = []
                    car_img_list = {}
                    for cars in raw_car_list:
                        car = cars.find("a")
                        car_link = cars.find("a")["href"]
                        raw_car_name = cars.find("a")["title"]
                        car_name = (raw_car_name.split(" specs and photos"))[0]
                        car_list.append(car_name)
                        img_soup = BeautifulSoup(requests.get(car_link, headers=tm_headers).content, features="lxml")
                        car_img_link = img_soup.find("div", {"class": "col1width fl"}).find("img")["src"]
                        car_img_list[car_name] = car_img_link

                    if len(car_list) == 1:
                        car = car_list[0]
                    else:
                        car = random.choice(car_list)
                    car_img = car_img_list[car]
                    print(car)

                with open(f"{self.path}gtc_ans.json", "w") as data:
                    json.dump({ctx.guild.id: (car.lower())}, data)

                with open(f"{self.path}gtc_img.json", "w") as data:
                    json.dump({"car": car_img}, data)

                try:
                    emb.set_thumbnail(url=mfg_logo)
                except:
                    pass
                emb.set_image(url=car_img)

            except AttributeError:
                pass

            return emb

        embed = get_gtc()
        question = await ctx.send(content=None, embed=embed)
        await msg.delete()
        time = await ctx.send("Time left: `30s`")

        for i in range(1, 11):
            with open(f"{self.path}gtc_ans.json") as f_data:
                data = json.load(f_data)
            await asyncio.sleep(3)

            try:
                c_data = (data[str(ctx.message.guild.id)]).title()
                time_left = 30 - (3 * i)
                await time.edit(content=f"Time left: `{time_left}s`")

            except KeyError:
                await time.edit(content="Answering time ended.")
                break

        await time.edit(content="Answering time ended.")
        await question.delete()
        emb_answer = discord.Embed(title="Guess the Car!", description="", colour=discord.Colour.green())
        emb_answer.add_field(name="Answer", value=c_data, inline=False)
        with open(f"{self.path}gtc_img.json") as img_data:
            data = json.load(img_data)
            car_img = data["car"]
        emb_answer.set_image(url=car_img)
        await ctx.send(content=None, embed=emb_answer)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith("c: "):
            try:
                guess = " ".join(message.content.split(" ")[1:])
                with open(f"{self.path}gtc_ans.json") as f_data:
                    data = json.load(f_data)

                if guess.lower() == data[str(message.guild.id)]:
                    with open(f"{self.path}gtc_ans.json", "w") as f:
                        json.dump({}, f)
                    await message.add_reaction("✅")
                    await message.reply(f"**Correct!**")

                else:
                    await message.add_reaction("❌")
            except KeyError:
                pass

def setup(bot):
    bot.add_cog(GTC(bot))