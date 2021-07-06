#discord bot



#from funcs import *


import os
import discord

import numpy as np

from dotenv import load_dotenv

from datetime import datetime
#from apscheduler.scheduler import Scheduler

import threading

import time

from discord.ext import commands, tasks

#=======================================================
#inits
#=======================================================


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
#bumpkinhealth = int(os.getenv('bumpkin_health'))
#print(bumpkinhealth)

print(GUILD)
print('-----------------------------')

intents = discord.Intents.all()

client = discord.Client(intents=intents)

attacked_userlist=[]
attacked_usertwice=[]

voted_userlist=[]
votes = []

#this needs to be replaced to be me and anyone with 'Fat Minister' role
bot_admin_userlist = ['SpectralSmitty#4102','TheTowerKnight#6883','Spooky Shoryu#8161','Yuzzie#9469','a_gamer_in_pink#1312','Crossraincloud#2162','crisisangelwolf#1107','Aervid#6679']

cursed_userlist = ['SpectralSmitty#4102','TheTowerKnight#6883','Spooky Shoryu#8161','Yuzzie#9469','Crossraincloud#2162','Viz#8325','ViciousMuse#9205','Xanxus85#3888','bumpkinbatchboi#7429','TwoFacePessimist#4020']


attacs_chan_id = 818478301588619334



#sched = Scheduler
#sched.start()

tgt_health_max=500
tgt_health=tgt_health_max
tgt_AC = 2

#xanxus85 can attac 10 times a day
xanxus = 0

    



help_msg="""
Command : Function

attac : attack the target 
!raidstatus : status update
!hello : hello world
!CyborgHalp : this help message
==Admin commands==
!howdoyouturnthison : Revive target, clear people to attac again
!newhealth : set target's max health (default 500)
!newAC : set target's AC (default 2)
!kill : kill target
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
    
    


#pick a new random target from cursed_userlist        
def new_tgt():
    global cursed_userlist
    length = len(cursed_userlist)
    ri = np.random.randint(0, high=length)
    tgt = cursed_userlist[ri]
    print('New target: '+tgt)
    return tgt
    
    

    
#=======================================================
#discord events and responses
#=======================================================



            

#@daily_reset.before_loop
#async def before():
    #hrs_til_midnight = 13
    #await asyncio.sleep(3600*hrs_til_midnight)
    #await client.wait_until_ready()




@client.event
async def on_ready():
    global cursed_userlist
    global tgt_member
    global tgt_name
    global attacs_chan_id
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    #print('{} has connected to Discord!'.format(client.user))
    print('We have logged in as {0.user}'.format(client))
    tgt_name = new_tgt()
    for server in client.guilds:
        if str(server)=="Boletarian Chamber of Commerce":
            for member in server.members:
                if str(member) == tgt_name:
                    tgt_member = member
                    print('target found!')
                    print(tgt_member)
                    print(tgt_member.id)
                    break
    attacs_chan = client.get_channel(attacs_chan_id)
    out_msg = 'I am awaken. The current target is: '+tgt_name
    await attacs_chan.send(out_msg)


@tasks.loop(hours=24)
async def daily_reset():
    global attacked_userlist
    global tgt_health
    global tgt_member
    global tgt_health_max
    global tgt_name
    if daily_reset.current_loop != 0:
        for server in client.guilds:
            if str(server)=="Boletarian Chamber of Commerce":
                tower_guild = server
                break
        norights_role = discord.utils.get(tower_guild.roles,name="No Rights")
        #norights_role = discord.utils.get(message.guild.roles,name="No Rights")
        #somerights_role = discord.utils.get(guild.roles,name="Bumpkin, the Raid Boss")
        #norights_role = discord.utils.get(guild.roles,name="Clone")

        attacked_userlist=[]
        print('daily: attac list cleared')
        if (tgt_health == 0):
            #tgt_member.add_roles(somerights_role)
            tgt_health=tgt_health_max
            tgt_member.remove_roles(norights_role)
        tgt_name = new_tgt()
        attacs_chan = client.get_channel(attacs_chan_id)
        out_msg = 'I have reset. The new current target is: '+tgt_name
        await attacs_chan.send(out_msg)
   
daily_reset.start()
        
@client.event
async def on_message(message):
    global tgt_health
    global tgt_name
    global attacked_userlist
    global bot_admin_userlist
    global tgt_member
    global tgt_health_max
    global tgt_AC
    global help_msg
    global xanxus
    #norights_role = discord.utils.get(message.guild.roles,name="Clone")
    norights_role = discord.utils.get(message.guild.roles,name="No Rights")
    #somerights_role = discord.utils.get(message.guild.roles,name="Bumpkin, the Raid Boss")
    #fatministers_role = discord.utils.get(message.guild.roles,name="Fat Ministers")
    
    if message.author == client.user:
        return

    #general stuff    
    #attac    
    if message.content.startswith('attac'):
        if (message.author.name not in attacked_userlist) and (message.author.name != tgt_name[:-5]):
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
                    
            
            if atk<tgt_AC:
                out_msg = "{} \n**Attack Roll:** {}\nYou Missed!".format(message.author.mention,atk)#bumpkin_user.mention
                await message.channel.send(content=out_msg)
            else:
                if atk==20:
                    dmg = dmg_roll_crit()
                else:
                    dmg = dmg_roll()
                #if message.author.name == tgt_name[:-5]:
                #    print('extra dmg for bumpkin')
                #    bumpkindmg = dmg_roll_bump()
                #    dmg += bumpkindmg
                #if message.author.name == 'Xanxus85':
                #    print('extra dmg for xanxus')
                #    xancrit = dmg_roll_crit()
                #    dmg += xancrit                   
                if (np.random.randint(1,high=2001)==1):
                    print('super roll')
                    dmg += dmg_roll_super()
                    
                tgt_health -= dmg
        
                if (tgt_health <= 0):
                    tgt_health = 0
                    #os.environ['bumpkin_health'] = str(bumpkinhealth)
                    out_msg = "{} \n**Attack Roll:** {}\nYou hit for {} damage and killed {}!".format(message.author.mention,atk,dmg,tgt_name[:-5])
                    await message.channel.send(content=out_msg)
                    await tgt_member.add_roles(norights_role)
                    #await bumpkin_user.remove_roles(somerights_role)
                
                else:
                    #os.environ['bumpkin_health'] = str(bumpkinhealth)
                    out_msg = "{} \n**Attack Roll:** {}\nYou hit for {} damage, {} has {}/{} hp left!".format(message.author.mention,atk,dmg,tgt_name[:-5],tgt_health,tgt_health_max)
                    await message.channel.send(content=out_msg)
                    print('{} attacked by {} for {}dmg and now has {}hp left'.format(tgt_name[:-5],message.author,dmg,tgt_health))
        else:
            await message.channel.send(content="{} \nYou already rolled today!".format(message.author.mention))
    #hello            
    if message.content.startswith('!hello'):
        await message.channel.send(content='Hello!')
    
    #status update    
    if message.content.startswith('!raidstatus'):
        out_text = "target health: {}/{}\nYou need to roll a {} or higher to hit\nPeople who have attac'd: ".format(tgt_health,tgt_health_max,tgt_AC)
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
    

    
    #admin stuff
    if (str(message.author) in bot_admin_userlist):
        #revive bumpkin
        if message.content.startswith('!howdoyouturnthison'):
            await message.channel.send(content='{}'.format(message.author.mention))
            attacked_userlist=[]
            tgt_health=tgt_health_max
            xanxus=0
            #await client.remove_roles(bumpkin_user,norights_role)
            #await tgt_member.add_roles(somerights_role)
            await tgt_member.remove_roles(norights_role)
            #os.environ['bumpkin_health'] = str(bumpkinhealth)
            await message.channel.send(content='target hp has been reset to max, daily reset forced')
            print('target hp has been reset to max, daily reset forced')

        #kill bumpkin
        if message.content.startswith('!kill'):
            #await client.add_roles(bumpkin_user,norights_role)
            tgt_health=0
            await tgt_member.add_roles(norights_role)
            #await bumpkin_user.remove_roles(somerights_role)
            await message.channel.send(content='a bot admin killed the target')
            print('a bot admin killed the target')
        
        #set max health    
        if message.content.startswith('!newhealth'):
            #await client.add_roles(bumpkin_user,norights_role)
            try:
                tgt_health_max = int(message.content[11:])
                tgt_health = tgt_health_max
                await message.channel.send(content="target's max health now {}".format(tgt_health_max))
                print("target's max health now {}".format(tgt_health_max))
            except:
                await message.channel.send(content="try putting in an actual integer, dingus")
                
                
        if message.content.startswith('!newAC'):
            #await client.add_roles(bumpkin_user,norights_role)
            try:
                tgt_AC = int(message.content[7:])
                #bumpkin_AC = bumpkin_max
                await message.channel.send(content="target AC now {}".format(tgt_AC))
                print("target AC now {}".format(tgt_AC))
            except:
                await message.channel.send(content="try putting in an actual integer, dingus")
                
        if message.content.startswith('!clearattacs'):
            #await client.add_roles(bumpkin_user,norights_role)
            attacked_userlist=[]
            xanxus = 0
            await message.channel.send(content='Everyone can now attac again')
            print('userlist cleared')
                
         
                          
                 

   

    
client.run(TOKEN)


