#MIT License
#
#Copyright (c) 2020 Philipp Göldner
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

# Discord Queue Bot der während der eLearning Challenge https://elearning.mathphys.info/ entstanden ist.

import discord
import json
from discord.ext import commands
from collections import deque
member_queues = {}
enabled = {}



bot = commands.Bot(command_prefix="$")
bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="mit anderen Bots"))


@bot.command(pass_context=True, help="Öffnet die Warteschlange")
async def start(ctx):
    if set([role.name for role in ctx.message.author.roles]) & set(roles):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ob Studis warten"))
        await ctx.send("Warteschlange ist nun geöffnet.")
        enabled[ctx.message.guild.id] = True

@bot.command(pass_context=True, help="Schließt die Warteschlange")
async def stop(ctx):
    if set([role.name for role in ctx.message.author.roles]) & set(roles):
        await ctx.send("Warteschlange ist nun geschlossen.")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="mit anderen Bots"))
        enabled[ctx.message.guild.id] = False
        member_queues.pop(ctx.message.guild.id)

@bot.command(pass_context=True, help="Aktueller Status der Warteschlange")
async def status(ctx):
    # todo this can fail
    if ctx.message.guild.id in enabled:
        if enabled[ctx.message.guild.id]:
            await ctx.send("Warteschlange ist offen")
        else:
            await ctx.send("Warteschlange ist geschlossen")
    else:
        enabled[ctx.message.guild.id] = False


def get_displaynick(author):
    nick = ""
    if author.nick:
        nick = author.nick
    else:
        nick = str(author).split("#")[0]
    return nick


@bot.command(pass_context=True, help="Anstellen in Warteschlange")
async def wait(ctx):
    author = ctx.message.author
    guild = ctx.message.guild.id
    if guild not in enabled:
        enabled[guild] = False

    if not enabled[guild]:
        await ctx.send(f"Hallo {get_displaynick(author)} die Warteschlange ist aktuell geschlossen.")
    else:
        if guild not in member_queues:
                member_queues[guild] = deque()
                member_queues[guild].append(author)
                await ctx.send(f"Hallo {get_displaynick(author)} du bist aktuell in Position {member_queues[guild].index(author)+1}. Mit $wait kannst du dir deine aktuelle Position anzeigen lassen")
        else:
            if author in member_queues[guild]:
                await ctx.send(f"Hallo {get_displaynick(author)} du bist aktuell in Position {member_queues[guild].index(author)+1}. Mit $wait kannst du dir deine aktuelle Position anzeigen lassen")
            else:
                member_queues[guild].append(author)
                await ctx.send(f"Hallo {get_displaynick(author)} du bist aktuell in Position {member_queues[guild].index(author)+1}. Mit $wait kannst du dir deine aktuelle Position anzeigen lassen")


@bot.command(pass_context=True)
async def leave(ctx, help="Verlassen der Warteschlange"):
    author = ctx.message.author
    guild = ctx.message.guild.id
    if guild not in enabled:
        enabled[guild] = False
    if not enabled[guild]:
        await ctx.send(f"Hallo {get_displaynick(author)} die Warteschlange ist aktuell geschlossen. Bei Fragen kannst du unseren 24/7 Chatbot befragen.")
    else:
        if guild not in member_queues:
                await ctx.send(f"Hallo {get_displaynick(author)} du bist aktuell nicht in der Warteschlange. Du kannst dich mit $wait anstellen")
        else:
            if author in member_queues[guild]:
                member_queues[guild].remove(author)
                await ctx.send(f"Hallo {get_displaynick(author)} du hast die Warteschlange verlassen.")
            else:
                await ctx.send(f"Hallo {get_displaynick(author)} du bist aktuell nicht in der Warteschlange. Du kannst dich mit $wait anstellen")


@bot.command(pass_context=True)
async def next(ctx):
    guild = ctx.message.guild.id
    author = ctx.message.author
    voice_state = author.voice
    vc = voice_state.channel

    if guild not in enabled:
        enabled[guild] = False

    if set([role.name for role in ctx.message.author.roles]) & set(roles):
        if not enabled[guild]:
            await ctx.send(f"Hallo {get_displaynick(author)}. Die Warteschlange ist aktuell noch geschlossen. Du kannst sie mit $start öffnen.")
        else:
            if len(member_queues[guild]) >= 1:
                member = member_queues[guild].popleft()
            else:
                await ctx.send("Die Warteschlange ist leer :(")
            try:
                next_member = member_queues[guild].popleft()
                member_queues[guild].appendleft(next_member)
                await ctx.send(f"{get_displaynick(member)} ist dran. Der nächste ist {next_member.mention}")
                await member.move_to(vc)
            except IndexError:
                await member.move_to(vc)
                await ctx.send(f"{get_displaynick(member)} ist dran. Der nächste ist Niemand :(")

@bot.command(pass_context=True)
async def ls(ctx):
    author = ctx.message.author
    guild = ctx.message.guild.id
    if guild not in enabled:
        enabled[guild] = False
    if set([role.name for role in ctx.message.author.roles]) & set(roles):
        if not enabled[guild]:
            await ctx.send(f"Hallo {get_displaynick(author)}. Die Warteschlange ist aktuell noch geschlossen. Du kannst sie mit $start öffnen.")
        else:
            if member_queues[guild]:
                for number, member in enumerate(member_queues[guild]):
                    await ctx.send(f"{number+1}. {get_displaynick(member)}")
            else:
                await ctx.send(f"Es ist im Moment niemand in der Warteschlange!")


with open("config.json") as f:
    config = json.load(f)

api_key = config.get("api_key")
roles = config.get("roles")
if not api_key:
    raise RuntimeError("Config must contain api_key")
if not roles:
    raise RuntimeError("Config must contain roles")
bot.run(api_key)
