#discord bot



#from funcs import *


import os
import discord

import numpy as np

from dotenv import load_dotenv

from datetime import datetime
#from apscheduler.scheduler import Scheduler

import threading

from discord.ext import commands, tasks

#=======================================================
#inits
#=======================================================


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
bumpkinhealth = int(os.getenv('bumpkin_health'))
#print(bumpkinhealth)

print(GUILD)

intents = discord.Intents.all()

client = discord.Client(intents=intents)

attacked_userlist=[]
attacked_usertwice=[]

voted_userlist=[]
votes = []

#this needs to be replaced to be me and anyone with 'Fat Minister' role
bot_admin_userlist = ['SpectralSmitty#4102','TheTowerKnight#6883','Spooky Shoryu#8161','Yuzzie#9469','a_gamer_in_pink#1312','Crossraincloud#2162','crisisangelwolf#1107','Aervid#6679']

cursed_userlist = ['SpectralSmitty#4102','TheTowerKnight#6883','Spooky Shoryu#8161','Yuzzie#9469','Crossraincloud#2162','Viz#8325','ViciousMuse#9205','Xanxus85#3888','bumpkinbatchboi#7429','TwoFacePessimist#4020']

bumpkin_ID = '550466865248600064'
bumpkin_AC = 2



#sched = Scheduler
#sched.start()

bumpkin_max=42069#400
bumpkinhealth=0#bumpkin_max

#xanxus85 can attac 10 times a day
xanxus = 0

    



help_msg="""
Command : Function

attac : attack bumpkin 
!raidstatus : status update
!hello : hello world
!CyborgHalp : this help message
==Admin commands==
!howdoyouturnthison : Revive bumpkin, clear people to attac again
!bumphealth : set bumpkin's max health (default 400)
!bumpAC : set bumpkin's AC (default 2)
!bumpkill : kill bumpkin
!clearattacs : clear all peeps to attac again
"""



#=======================================================
#functions
#=======================================================


#roll 4d6+10 damage
def dmg_roll():
    out = 0
    for i in range(4):
        out += np.random.randint(1,high=7)
    return out+10
    
def dmg_roll_crit():
    out = 0
    for i in range(8):
        out += np.random.randint(1,high=7)
    return out+10
    
def dmg_roll_bump():
    out=0
    for i in range(30):
        out += np.random.randint(1,high=11)
    return out
    
def dmg_roll_super():
    out = 0
    for i in range(200):
        out += np.random.randint(1,high=21)
    return out
    
def dmg_roll_excalibur():
    out = 0
    for i in range(8):
        out += np.random.randint(1,high=11)
    return out
    
def levelling():
    print('not done')
    
def pingbumpkin():
    print('not done')
    
    
#daily reset
def daily_reset():
    global attacked_userlist
    global bumpkinhealth
    global bumpkin_user
    global bumpkinmax
    for server in client.guilds:
        guild = server
        if str(server)=="Boletarian Chamber of Commerce":
            break
    norights_role = discord.utils.get(guild.roles,name="No Rights")
    somerights_role = discord.utils.get(guild.roles,name="Bumpkin, the Raid Boss")
    #norights_role = discord.utils.get(guild.roles,name="Clone")
    threading.Timer(3600,checkTime).start()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    if (current_time[:2] == '00'):
        attacked_userlist=[]
        if (bumpkinhealth == 0):
            bumpkin_user.add_roles(somerights_role)
            bumpkinhealth=bumpkin_max
            bumpkin_user.remove_roles(norights_role)
        #os.environ['bumpkin_health'] = str(bumpkinhealth)
    
    

    
#=======================================================
#discord events and responses
#=======================================================



@tasks.loop(hours=24)
async def daily_reset():
    global attacked_userlist
    global bumpkinhealth
    global bumpkin_user
    global bumpkinmax
    for server in client.guilds:
        guild = server
        if str(server)=="Boletarian Chamber of Commerce":
            break
    norights_role = discord.utils.get(guild.roles,name="No Rights")
    somerights_role = discord.utils.get(guild.roles,name="Bumpkin, the Raid Boss")
    #norights_role = discord.utils.get(guild.roles,name="Clone")

    attacked_userlist=[]
    print('attac list cleared')
    if (bumpkinhealth == 0):
        bumpkin_user.add_roles(somerights_role)
        bumpkinhealth=bumpkin_max
        bumpkin_user.remove_roles(norights_role)
    print('bumpkin alive again')
            
            
@daily_reset.before_loop
async def before():
    #hrs_til_midnight = 13
    #await asyncio.sleep(3600*hrs_til_midnight)
    await client.wait_until_ready()




@client.event
async def on_ready():
    global bumpkin_ID
    global bumpkin_user
    print(bumpkin_ID)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    #print('{} has connected to Discord!'.format(client.user))
    print('We have logged in as {0.user}'.format(client))
    for server in client.guilds:
        if str(server)=="Boletarian Chamber of Commerce":
            for member in server.members:
                if str(member) == 'bumpkinbatchboi#7429':
                    bumpkin_user = member
                    print('bumpkin found!')
                    print(bumpkin_user)
                    print(bumpkin_user.id)
                    break

    
    

        
@client.event
async def on_message(message):
    global bumpkinhealth
    global attacked_userlist
    global bot_admin_userlist
    global bumpkin_user
    global bumpkin_max
    global bumpkin_AC
    global help_msg
    global xanxus
    global voted_userlist
    global votes
    #norights_role = discord.utils.get(message.guild.roles,name="Clone")
    norights_role = discord.utils.get(message.guild.roles,name="No Rights")
    somerights_role = discord.utils.get(message.guild.roles,name="Bumpkin, the Raid Boss")
    fatministers_role = discord.utils.get(message.guild.roles,name="Fat Ministers")
    
    if message.author == client.user:
        return

    #general stuff    
    #attac    
    if message.content.startswith('attac'):
        if message.author.name not in attacked_userlist:
            atk = np.random.randint(1,high=21)
            if message.author.name=='Xanxus85':
                if xanxus == 9:
                    attacked_userlist.append(message.author.name)
                else:
                    xanxus += 1
                    print('xanxus attacks: {}'.format(xanxus))
            else:
                attacked_userlist.append(message.author.name)
            #if message.author.name=='a_gamer_in_pink':
            #    if atk > 18:
                    
            
            if atk<bumpkin_AC:
                out_msg = "{} (where bumpkin?)\n**Attack Roll:** {}\nYou Missed!".format(message.author.mention,atk)#bumpkin_user.mention
                await message.channel.send(content=out_msg)
            else:
                if atk==20:
                    dmg = dmg_roll_crit()
                else:
                    dmg = dmg_roll()
                if message.author.name == 'bumpkinbatchboi':
                    print('extra dmg for bumpkin')
                    bumpkindmg = dmg_roll_bump()
                    dmg += bumpkindmg
                if message.author.name == 'Xanxus85':
                    print('extra dmg for xanxus')
                    xancrit = dmg_roll_crit()
                    dmg += xancrit                   
                if (np.random.randint(1,high=2001)==1):
                    print('super roll')
                    dmg += dmg_roll_super()
                    
                bumpkinhealth -= dmg
        
                if (bumpkinhealth <= 0):
                    bumpkinhealth = 0
                    os.environ['bumpkin_health'] = str(bumpkinhealth)
                    out_msg = "{} (where bumpkin?)\n**Attack Roll:** {}\nYou hit for {} damage and killed bumpkin!".format(message.author.mention,atk,dmg)
                    await message.channel.send(content=out_msg)
                    await bumpkin_user.add_roles(norights_role)
                    await bumpkin_user.remove_roles(somerights_role)
                
                else:
                    os.environ['bumpkin_health'] = str(bumpkinhealth)
                    out_msg = "{} (where bumkpin?)\n**Attack Roll:** {}\nYou hit for {} damage, bumpkin has {}/{} hp left!".format(message.author.mention,atk,dmg,bumpkinhealth,bumpkin_max)
                    await message.channel.send(content=out_msg)
                    print('bumpkin attacked by {} for {}dmg and now has {}hp left'.format(message.author,dmg,bumpkinhealth))
        else:
            await message.channel.send(content="{} (where bumpkin?)\nYou already rolled today!".format(message.author.mention))
    #hello            
    if message.content.startswith('!hello'):
        await message.channel.send(content='Hello!')
    
    #status update    
    if message.content.startswith('!raidstatus'):
        out_text = "bumpkin health: {}/{}\nYou need to roll a {} or higher to hit\nPeople who have attac'd: ".format(bumpkinhealth,bumpkin_max,bumpkin_AC)
        for name in attacked_userlist:
            out_text = out_text + name + ', '
        out_text = out_text[:-2]
        await message.channel.send(content=out_text) 
    
    #help message    
    if message.content.startswith('!CyborgHalp'):
        await message.channel.send(content=help_msg) 
        
      
    #print out members of servers (to console, not discord)(please don't use/spam this)
    #if message.content.startswith('$members'):
    #    if str(message.author) in bot_admin_userlist:
        #user_list = message.server.members
    #        for server in client.guilds:
    #            print(server)
    #            for member in server.members:
    #                print(member)
    
    #voting
    if message.content.startswith('!vote'):
        if message.author.name not in voted_userlist:
            vote = message.content[6:]
            votes.append(vote)
            this_auth = str(message.author.name)
            voted_userlist.append(this_auth)
            await message.delete()
            print('VOTES: {}'.format(votes))
            print('Already voted: {}'.format(voted_userlist))
            await message.channel.send(content='Vote for "{}" counted!'.format(this_auth))

        else:
            await message.delete()
            await message.channel.send(content='You already voted dweeb')

    
    #admin stuff
    if (str(message.author) in bot_admin_userlist):
        #revive bumpkin
        if message.content.startswith('!howdoyouturnthison'):
            await message.channel.send(content='{}'.format(message.author.mention))
            attacked_userlist=[]
            bumpkinhealth=bumpkin_max
            xanxus=0
            #await client.remove_roles(bumpkin_user,norights_role)
            await bumpkin_user.add_roles(somerights_role)
            await bumpkin_user.remove_roles(norights_role)
            #os.environ['bumpkin_health'] = str(bumpkinhealth)
            await message.channel.send(content='bumpkin hp has been reset to max, daily reset forced')
            print('bumpkin hp has been reset to max, daily reset forced')

        #kill bumpkin
        if message.content.startswith('!bumpkill'):
            #await client.add_roles(bumpkin_user,norights_role)
            bumpkinhealth=0
            await bumpkin_user.add_roles(norights_role)
            await bumpkin_user.remove_roles(somerights_role)
            await message.channel.send(content='a bot admin killed bumpkin')
            print('a bot admin killed bumpkin')
        
        #set max health    
        if message.content.startswith('!bumphealth'):
            #await client.add_roles(bumpkin_user,norights_role)
            try:
                bumpkin_max = int(message.content[12:])
                bumpkinhealth = bumpkin_max
                await message.channel.send(content="bumpkin's max health now {}".format(bumpkin_max))
                print("bumpkin's max health now {}".format(bumpkin_max))
            except:
                await message.channel.send(content="try putting in an actual integer, dingus")
                
                
        if message.content.startswith('!bumpAC'):
            #await client.add_roles(bumpkin_user,norights_role)
            try:
                bumpkin_AC = int(message.content[8:])
                #bumpkin_AC = bumpkin_max
                await message.channel.send(content="bumpkin's AC now {}".format(bumpkin_AC))
                print("bumpkin's AC now {}".format(bumpkin_AC))
            except:
                await message.channel.send(content="try putting in an actual integer, dingus")
                
        if message.content.startswith('!clearattacs'):
            #await client.add_roles(bumpkin_user,norights_role)
            attacked_userlist=[]
            xanxus = 0
            await message.channel.send(content='Everyone can now attac again')
            print('userlist cleared')
                
         
                          
                 

   

    
client.run(TOKEN)


