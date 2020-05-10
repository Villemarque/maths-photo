#!/usr/local/bin/python3
#coding: utf-8

#Author: Solal LORCY

#Licence: GNU AGPLv3

import asyncio
import datetime
import discord
import discord.utils
import logging
import logging.handlers
import os
import re
import sys

from dateutil.relativedelta import relativedelta
from discord import utils
from dotenv import load_dotenv
from io import BytesIO
from pathlib import Path

############
#Constantes#
############

load_dotenv()
math_photo_dir = Path(__file__).parent.absolute()

if __debug__:
    CHANNEL_SOURCE_ID = int(os.getenv("CHANNEL_SOURCE_DEBUG"))
    GUILD_DEST = int(os.getenv("GUILD_DEST_DEBUG"))
    TOKEN = os.getenv("TOKEN_DEBUG")
    LOG_NAME = math_photo_dir / "discord_debug.log"

else:
    CHANNEL_SOURCE_ID = int(os.getenv("CHANNEL_SOURCE"))
    GUILD_DEST = int(os.getenv("GUILD_DEST"))
    TOKEN = os.getenv("TOKEN")
    LOG_NAME = math_photo_dir / "discord.log"

OWNER = int(os.getenv("OWNER"))

DURATION_PARSER = re.compile(
    r"((?P<years>\d+?) ?(years|year|Y|y) ?)?"
    r"((?P<months>\d+?) ?(months|month|m) ?)?"
    r"((?P<weeks>\d+?) ?(weeks|week|W|w) ?)?"
    r"((?P<days>\d+?) ?(days|day|D|d) ?)?"
    r"((?P<hours>\d+?) ?(hours|hour|H|h) ?)?"
    r"((?P<minutes>\d+?) ?(minutes|minute|M) ?)?"
    r"((?P<seconds>\d+?) ?(seconds|second|S|s))?"
    )

REMOVE_CHECK_CMD = "$rmc!!!"
RETRO_CMD = "$retro "

######
#Logs#
######

log = logging.getLogger("bot")
if __debug__:
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.INFO)

logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.WARNING)

format_string = "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s"

#5242880 bytes = 5 Mo
handler = logging.handlers.RotatingFileHandler(LOG_NAME, maxBytes=5242880, backupCount=1, encoding="utf8")
handler.setFormatter(logging.Formatter(format_string))
log.addHandler(handler)

handler_2 = logging.StreamHandler(sys.stdout)
handler_2.setFormatter(logging.Formatter(format_string))
log.addHandler(handler_2)

#########
#Classes#
#########

class Mybot(discord.Client):


    async def on_ready(self) -> None:
        log.info(f"Logged in as {self.user.name}, {self.user.id}, debug mode : {__debug__}")
        #En cas d'allumage tardif, on vérifie automatiquement les messages postés 10 minutes avant
        await self.catch_up_pics(datetime.datetime.utcnow() - relativedelta(minutes=10))


    async def on_message(self, mes: discord.Message) -> None:
        log.debug("on_message triggered")
        if self.check_message(mes):
            log.debug(f"message {mes.channel.id} in the correct channel")
            if mes.content.startswith(RETRO_CMD) and mes.author.id == OWNER:
                await self.retroactive_cmd(mes)
            elif mes.content.startswith(REMOVE_CHECK_CMD) and mes.author.id == OWNER:
                await self.remove_check_cmd(mes)
            else:
                await self.transfert(mes)


    async def retroactive_cmd(self, mes: discord.Message) -> None:
        """
        Va chercher dans l'historique du salon du tous les message entre maintenant et la date indiqué (temps relatif),
        et transfère les photos prisent durant cet intervalle.
        Ex: $retro 7d -> Transfère toutes les photos prise il y a moins d'une semaine
        """
        log.info(f"{mes.author.id} requested `retro` cmd in {mes.id}")
        arg = await self.convert(mes)
        await self.catch_up_pics(arg)


    async def convert(self, mes: discord.Message) -> datetime.datetime:
        """
        Converts a `duration` string to a datetime object that's `duration` in the future.
        The converter supports the following symbols for each unit of time:
        - years: `Y`, `y`, `year`, `years`
        - months: `m`, `month`, `months`
        - weeks: `w`, `W`, `week`, `weeks`
        - days: `d`, `D`, `day`, `days`
        - hours: `H`, `h`, `hour`, `hours`
        - minutes: `M`, `minute`, `minutes`
        - seconds: `S`, `s`, `second`, `seconds`
        The units need to be provided in descending order of magnitude.
        """
        #On supprime `RETRO_CMD` du message pour juste récupérer les paramètres
        duration = mes.content[len(RETRO_CMD):]
        match = DURATION_PARSER.fullmatch(duration)
        if not match:
            log.error(f"`{duration}` is not a valid duration string.")
            await  mes.add_reaction("❌")
            return mes.created_at

        duration_dict = {unit: int(amount) for unit, amount in match.groupdict(default=0).items()}
        delta = relativedelta(**duration_dict)
        return mes.created_at - delta

    async def catch_up_pics(self, after: datetime.datetime) -> None:
        """
        Va chercher dans l'historique du salon du tous les message entre `now` et la date indiqué (temps absolu),
        et transfère les photos prisent durant cet intervalle.
        """
        log.info(f"Checking messages posted after {after}")
        now = datetime.datetime.utcnow()
        channel_source = self.get_channel(CHANNEL_SOURCE_ID)
        history = channel_source.history(before=now,after=after,limit=None,oldest_first=True)
        async for mes in history:
            #TEMPO enlevé `and not self.already_transfered(mes)`
            if self.check_message(mes) and not self.already_transfered(mes):
                await self.transfert(mes)
        log.info("All fetched messages processed")


    async def remove_check_cmd(self, mes: discord.Message) -> None:
        channel_source = self.get_channel(CHANNEL_SOURCE_ID)
        history = channel_source.history(limit=None)
        await mes.delete()
        async for message_h in history:
            if self.already_transfered(message_h):
                await message_h.remove_reaction("✅", self.user)
                log.info(f"check removed from {message_h.id}")
        log.info("All check removed")


    def already_transfered(self, mes: discord.Message) -> bool:
        """Pour éviter de traiter un message deux fois en cas de déconnexion"""
        for reaction in mes.reactions:
            if str(reaction.emoji) == "✅" and reaction.me:
                log.info(f"Message {mes.id} already handled")
                return True

        return False


    def check_message(self, mes: discord.Message) -> bool:
        """Renvoie `true` si le message n'a pas été envoyé par un bot, et posté dans le bon salon"""
        return (not mes.author.bot) and (mes.channel.id == CHANNEL_SOURCE_ID)


    async def transfert(self, mes: discord.Message) -> None:
        if not mes.attachments:
            log.debug(f"message {mes.id} does NOT contain attachements")
            return

        log.info(f"message {mes.id} contains attachements")
        date_creation = mes.created_at
        channel_dest = await self.get_channel_destination(date_creation.date())
        await channel_dest.send(
                    content=f"Z{date_creation.hour}h{date_creation.minute}m{date_creation.second}s:  {mes.content}",
                    files=[discord.File(fp=BytesIO(await a.read()),filename=a.filename) for a in mes.attachments]
                    )

        await mes.add_reaction("✅")
        log.info(f"message {mes.id} successfully transfered")


    async def get_channel_destination(self, date_mes: datetime.date) -> discord.TextChannel:
        """On vérifie d'abord si le salon du jour n'existe pas déjà.
        Ensuite on vérifie si la catégorie (cad le mois) existe:
        -Si elle existe on ajoute un salon avec le nouveau jour à cette catégorie
        -Sinon cela veut dire que l'on a débuté un nouveau mois, il faut créer la catégorie correspondante
        et ensuite le salon.
        """
        guild_dest = self.get_guild(GUILD_DEST)
        name_channel_dest = (
            f"{str(date_mes.month).zfill(2)}"
            "-"
            f"{str(date_mes.day).zfill(2)}"
            )
        channel_dest = discord.utils.get(guild_dest.channels, name=name_channel_dest)
        if channel_dest is not None: #Si le salon existe déjà
            return channel_dest

        name_category_dest = f"mois-{str(date_mes.month).zfill(2)}"
        category_dest = discord.utils.get(guild_dest.categories, name=name_category_dest)
        if category_dest is not None: #Si la catégorie existe déjà
            return await self.create_new_channel(name=name_channel_dest,category_dest=category_dest)

        category_dest = await guild_dest.create_category(name_category_dest)
        log.info(f"Category {name_category_dest} created")
        return await self.create_new_channel(name=name_channel_dest,category_dest=category_dest)


    async def create_new_channel(self, name: str, category_dest: discord.CategoryChannel) -> discord.TextChannel:
        """Crée un salon nommé `name` dans la catégorie `category_dest`
        
        Infos sur les limites d'un serveur discord: https://discordia.me/en/server-limits
        500 Salons en tout, 50 par catégorie
        """
        channel_dest = await category_dest.create_text_channel(name)
        log.info(f"Channel {channel_dest.name}, id: {channel_dest.id} created")
        if channel_dest.position >= 39:
            log.warning(f"This is channel number {channel_dest.position}, a category can only handle 50")
        return channel_dest

#####################
#programme principal#
#####################

if __name__ == "__main__":
    print('#'*80)
    bot = Mybot()
    bot.run(TOKEN)