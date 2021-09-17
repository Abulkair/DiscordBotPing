import os
import discord
import json
from discord.ext.commands.help import HelpCommand
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
STEP = 20

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    async def send_bot_help(self, mapping):
        response = f'Welcome to my Discord server!'
        return await self.get_destination().send(response)

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='.', intents = intents, help_command=CustomHelpCommand())

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to my Discord server!')
    print(f'User {member.name} connected to the channel')

@client.event
async def on_member_remove(member):
    print(f'User {member.name} left channel')

def jsonKeys2int(x):
    if isinstance(x, dict):
            return {(int(k) if k.isnumeric() else k):v for k,v in x.items()}
    return x

@client.event
async def on_message(message):
    await client.process_commands(message)
    
    with open('users.json', 'r') as f:
        users = json.load(f, object_hook=jsonKeys2int)

    await update_data(users, message.author)
    await add_experience(users, message.author, 1)
    await level_up(users, message.author, message.channel)

    with open('users.json', 'w') as f:
        json.dump(users, f) 

async def update_data(users, user):
    if not user.id in users:
        users[user.id] = {}
        users[user.id]['experience'] = 0
        users[user.id]['level'] = 1

async def add_experience(users, user, exp):
    users[user.id]['experience'] += exp

async def level_up(users, user, channel):
    experience = users[user.id]['experience']
    level = users[user.id]['level']

    if int(experience) % STEP == 0:
        level += 1
        await channel.send('{} has leveled up to {}'.format(user.mention, level))
        users[user.id]['level'] = level

@client.command(pass_context=True)
async def ping(ctx):
    await ctx.send("pong")

# The below code bans player.
@client.command(pass_context=True)
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been kick')

# The below code unbans player.
@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def unban(ctx, member : discord.Member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

# The below code kicks player
@client.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kick')

client.run(TOKEN)