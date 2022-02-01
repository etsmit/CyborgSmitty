#discord bot

#evanpy / python3

#from funcs import *


import os
import discord

import numpy as np

from dotenv import load_dotenv

from datetime import datetime
#from apscheduler.scheduler import Scheduler

import threading

import time
from datetime import datetime
import pause

from discord.ext import commands, tasks

#=======================================================
#inits
#=======================================================
#after restarting bot, wait until 4:20pm to log in
print('waiting til 4:20')
pause.until(datetime(2022,1,13,16,20))
print('done waiting! logging in now...')



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


#this needs to be replaced to be me and anyone with 'Fat Minister' role
bot_admin_userlist = ['SpectralSmitty#4102','TheTowerKnight#6883','Spooky Shoryu#8161','Yuzzie#9469','a_gamer_in_pink#1312','crossraincloud#1633','crisisangelwolf#1107','Aervid#6679']

cursed_userlist = ['SpectralSmitty#4102','TheTowerKnight#6883','Spooky Shoryu#8161','Yuzzie#9469','crossraincloud#1633','Viz#8325','ViciousMuse#9205','Xanxus85#3888','bumpkinbatchboi#7429','TwoFacePessimist#4020','RyVador#2565']


attacs_chan_id = 818478301588619334

#daily damage required to kill (determined by past data - typically 7 ppl attac and avg dmg roll is 24)
kill_threshold = 180

boss_maxhealth = 400

#sched = Scheduler
#sched.start()

tgt_health_max=kill_threshold
tgt_health=tgt_health_max
tgt_AC = 2

#xanxus85 can attac 10 times a day
xanxus = 0

#cloud gets the attac X times
cloud = 0
    
#days until next boss fight
boss_countdown = 0#np.random.randint(1,high=7)
print(boss_countdown)
bossfight = True
boss_AC = 8

#buffs to player attacs (num of extra d10s)
boss_attac_buff=0

#50% chance for boss to miss?
#true if true
boss_weak = False

#amount of times resurrected player has attacked
#can attac 3x (done by removing them from attacked_usertwice after their second action)
res_player_attacs = 0

#boss attac count
#has boss attacked?
boss_attac = 0
player_dead = 0


boss_target = ''

help_msg="""
Command : Function

attac       : attack the target 
!raidstatus : status update
!hello      : hello world
!CyborgHalp : this help message
==Admin commands==
!howdoyouturnthison : Revive target, clear people to attac again
!newhealth          : set target's max health (default 500)
!newAC              : set target's AC (default 2)
!kill               : kill target
!clearattacs        : clear all peeps to attac again

BOSS FIGHT ACTIONS:
The boss enters the fight! They can attac one player ONCE and instakill them!
Use your target's full discord username with the numbers, for example "attac bumpkinbatchboi#7429"
Boss has 500 HP

Each player has two actions and can:
    attac     : same attac as usual
    weaken    : lower the boss AC by 1d6 (down to minimum of 2)
    defend    : protect your teammates! 50% chance for the boss to miss their attac!
    buff      : add an extra 1d10 to the rest of the attacs for the day!
    resurrect : (takes 2 actions) resurrect the dead teammate! They come back with 3 actions, +5 to attac roll, and 1d10 damage buff!
"""




#=======================================================
#functions
#=======================================================


#roll 4d6+10 damage (14 - 34),avg 24
#roll 4d10 damage (4 - 40),avg 22
def dmg_roll(buff):
    out = 0
    for i in range(4+buff):
        out += np.random.randint(1,high=13)
    return out
    
def dmg_roll_crit(buff):
    out = 0
    for i in range(8+2*buff):
        out += np.random.randint(1,high=13)
    return out
    
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
    


#pick a new random target from cursed_userlist        
def new_tgt():
    global boss_countdown
    global cloud
    global cursed_userlist
    global bossfight
    bossfight = False
    length = len(cursed_userlist)
    if cloud != 0:
        tgt = 'crossraincloud#1633'
        cloud -= 1
    else:
        ri = np.random.randint(0, high=length)
        tgt = cursed_userlist[ri]
    if boss_countdown == 0:
        boss_countdown = 0#np.random.randint(1,high=8)
        bossfight = True
        print('Boss fight! '+tgt)
    else:
        boss_countdown -= 1
        print('New target: '+tgt)
    return tgt
    
    
#return how many times player has attacked
def attac_counter(msg):
    count = 0
    if (msg.author.name in attacked_userlist):
        count += 1
    if (msg.author.name in attacked_usertwice):
        count += 1
    return count
    
#bool to see if any actions are needed by the player
def action_check(msg):
    actions = ['attac','buff','resurrect','weaken','defend']
    out = False
    for word in actions:
        if msg.content.startswith(word):
            out = True
            break
    return out
    

    
#check action count of player and put their name in the correct lists
def count_player_action(msg):
    global attacked_userlist
    global attacked_usertwice
    action_count = attac_counter(msg)
    if msg.content.startswith('resurrect'):
        if action_count == 0:
            attacked_userlist.append(msg.author.name)
            attacked_usertwice.append(msg.author.name)
        elif action_count > 0:
            return
            #await message.channel.send(content="{} \nNot enough actions left for that!".format(message.author.mention))
    else: 
        if action_count == 0:
            attacked_userlist.append(msg.author.name)
        elif action_count == 1:
            if msg.author.name not in attacked_userlist:
                attacked_userlist.append(msg.author.name)
            else:
                attacked_usertwice.append(msg.author.name)
        elif action_count == 2:
            return
    print(attacked_userlist)
    print(attacked_usertwice)
                #await message.channel.send(content="{} \nYou are out of actions!".format(message.author.mention))
    
#check if a member exists in the server
def check_member_exists(name):
    out = False
    for server in client.guilds:
        if str(server)=="Boletarian Chamber of Commerce":
            for member in server.members:
                print(str(member),name)
                if str(member) == name:
                    out = True
                    print('target found!')
                    break
    return out

    
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
    global tgt_nick
    global bossfight
    global tgt_health
    global boss_maxhealth
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
                    tgt_nick = tgt_member.display_name
                    print(tgt_nick)
                    break
    attacs_chan = client.get_channel(attacs_chan_id)
    if bossfight:
        print ('bossfight')
        out_msg = """The target is {}\n Type !CyborgHalp for the rules!!""" .format(tgt_name)
        tgt_health=boss_maxhealth
    else:
        tgt_health=tgt_health_max
        out_msg = 'I am awakened. The current target is: '+tgt_name
    await attacs_chan.send(out_msg)
    
    


@tasks.loop(hours=24)
async def daily_reset():
    global attacs_chan_id
    global attacked_userlist
    global attacked_usertwice
    global attack_usertwice
    global tgt_health
    global tgt_member
    global tgt_health_max
    global tgt_name
    global tgt_nick
    global boss_countdown
    global boss_maxhealth
    global boss_attac_buff
    global bossfight
    global boss_AC
    global boss_weak
    global res_player_attacs
    global boss_attac
    global boss_target
    global player_dead
    if daily_reset.current_loop != 0:
        for server in client.guilds:
            if str(server)=="Boletarian Chamber of Commerce":
                tower_guild = server
                break
        norights_role = discord.utils.get(tower_guild.roles,name="No Rights")
        #norights_role = discord.utils.get(message.guild.roles,name="No Rights")
        #somerights_role = discord.utils.get(guild.roles,name="Bumpkin, the Raid Boss")
        #norights_role = discord.utils.get(guild.roles,name="Clone")

        #set stuff back to default
        attacked_userlist=[]
        attacked_usertwice = []
        
        boss_AC = 10
        boss_weak = False
        boss_attac = 0
        player_dead = 0
        res_player_attacs = 0
        boss_attac_buff = 0
        boss_target = ''

        print('daily: attac list cleared')
        if (tgt_health == 0):
            try:
                #tgt_member.add_roles(somerights_role)
                await tgt_member.remove_roles(norights_role)
                await tgt_member.edit(nick = tgt_nick)
            except:
                print('couldnt change nickname')
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
        tgt_nick = tgt_member.display_name
        print(tgt_nick)
        tgt_health=tgt_health_max
        attacs_chan = client.get_channel(attacs_chan_id)
        if bossfight:
            print ('bossfight')
            out_msg = """!!! BOSS FIGHT !!!\n The target is {}\n Type !CyborgHalp for the rules!!""" .format(tgt_name)
            tgt_health=boss_maxhealth
        else:
            tgt_health=tgt_health_max
            out_msg = 'I have reset. The new current target is: '+tgt_name
        await attacs_chan.send(out_msg)
   
daily_reset.start()
        
@client.event
async def on_message(message):
    global tgt_health
    global tgt_name
    global attacked_userlist
    global attacked_usertwice
    global bot_admin_userlist
    global tgt_member
    global tgt_health_max
    global tgt_AC
    global tgt_nick
    global help_msg
    global xanxus
    global bossfight
    global boss_AC
    global boss_maxhealth
    global boss_attac_buff
    global boss_weak
    global res_player_attacs
    global boss_attac
    global player_dead
    global boss_target
    #norights_role = discord.utils.get(message.guild.roles,name="Clone")
    norights_role = discord.utils.get(message.guild.roles,name="No Rights")
    #somerights_role = discord.utils.get(message.guild.roles,name="Bumpkin, the Raid Boss")
    #fatministers_role = discord.utils.get(message.guild.roles,name="Fat Ministers")
    
    if message.author == client.user:
        return


    #general stuff    
    #attac
    #print(tgt_nick)
    if action_check(message):
        if bossfight:
            #===============================
            #check action count of player and stop them if theydon't have the actions
            action_count = attac_counter(message)
            print('--')
            print(message.author.name)
            print(message.content)
            print('action count: {}'.format(action_count))
            if action_count >= 2:
                await message.channel.send(content="{} \nYou are out of actions!".format(message.author.mention))
                return
                
            if (action_count > 0) and (message.content.startswith('resurrect')):
                await message.channel.send(content="{} \nYou don't have the actions for that!".format(message.author.mention))
                return
            #===============================
            #now move on to actual actions and doing things (for bossfight)
            
            #attac
            if message.content.startswith('attac'):
                
                #is boss attacking?
                if (str(message.author) == str(tgt_member)) and (boss_attac == 0):
                    if tgt_health == 0:
                        await message.channel.send(content="{}\n You can't attac when you're dead!".format(message.author.mention))
                        return
                    #boss attacs a player
                    boss_target = message.content[6:]
                    if not check_member_exists(boss_target):
                        await message.channel.send(content="{}\n That member doesn't exist! Try again!".format(message.author.mention))
                        return
                    boss_attac = 1
                    if boss_weak:
                        if np.random.randint(0,high=2):
                            if (message.author.name not in attacked_userlist):
                                attacked_userlist.append(boss_target[:-5])
                            if (message.author.name not in attacked_usertwice):
                                attacked_usertwice.append(boss_target[:-5])
                            player_dead = 1
                            await message.channel.send(content="{} killed {}!".format(message.author.mention,boss_target))
                        else:
                            await message.channel.send(content="{} missed their attac!".format(message.author.mention))
                    else:
                        if (message.author.name not in attacked_userlist):
                            attacked_userlist.append(boss_target[:-5])
                        if (message.author.name not in attacked_usertwice):
                            attacked_usertwice.append(boss_target[:-5])
                    player_dead = 1  
                    await message.channel.send(content="{} killed {}!".format(message.author.mention,boss_target))
                    
                #is player attacking?
                elif (message.author.name != tgt_name[:-5]):
                    #is resurrected player attacking?
                    if (message.author.name==boss_target):
                        #player has attacked once while resurrected:
                        #remove them from attacked_usertwice so they can go one more time
                        #(then res_player_attacs will be 3 and they are in attacked_usertwice and cannot go)
                        if res_player_attacs == 1:
                            attacked_userlist.remove(message.author.name)
                        res_player_attacs += 1
                        
                    #go through attac sequence 
                    atk = np.random.randint(1,high=21)
                    crit = False
                    if atk==20:
                        crit = True
                    if (message.author.name == boss_target):
                        atk += 5
                    if (atk < boss_AC):
                        out_msg = "{} \n**Attack Roll:** {}\nYou Missed!".format(message.author.mention,atk)#bumpkin_user.mention
                        await message.channel.send(content=out_msg)
                    else:
                        if crit:
                            dmg = dmg_roll_crit(boss_attac_buff)
                            if (message.author.name == boss_target):
                                dmg = dmg_roll_crit(boss_attac_buff+1)
                        else:
                            dmg = dmg_roll(boss_attac_buff)
                            if (message.author.name == boss_target):
                                dmg = dmg_roll_crit(boss_attac_buff+1)
                                
                        if (np.random.randint(1,high=2001)==1):
                            print('super roll')
                            dmg += dmg_roll_super()
                    
                        tgt_health -= dmg
                        if (tgt_health <= 0):
                            tgt_health = 0
                            out_msg = "{} \n**Attack Roll:** {}\nYou hit for {} damage and killed THE BOSS {}!".format(message.author.mention,atk,dmg,tgt_name[:-5])
                            await message.channel.send(content=out_msg)
                            try:
                                await tgt_member.add_roles(norights_role)
                                await tgt_member.edit(nick = 'This motherfucker has died')
                            except:
                                print('couldnt change nickname')
                            print(tgt_member)
                            print('{} attacked by {} for {}dmg and now has {}hp left'.format(tgt_name[:-5],message.author,dmg,tgt_health))
                
                        else:
                            out_msg = "{} \n**Attack Roll:** {}\nYou hit for {} damage, {} has {}/{} hp left!".format(message.author.mention,atk,dmg,tgt_name[:-5],tgt_health,boss_maxhealth)
                            await message.channel.send(content=out_msg)
                            print('{} attacked by {} for {}dmg and now has {}hp left'.format(tgt_name[:-5],message.author,dmg,tgt_health))
                    count_player_action(message)

            #boss can't do any of this stuff
            elif (message.author.name != tgt_name[:-5]):
            
                #buff attacs
                if message.content.startswith('buff'):
                    boss_attac_buff += 1
                    print('attac buff set to {}'.format(boss_attac_buff))
                    out_msg = "{} \n You have buffed all subsequent attacs by 1d10!".format(message.author.mention)
                    await message.channel.send(content=out_msg)
                    count_player_action(message)
            
                #defend players so boss has only 50% chance to hit
                elif message.content.startswith('defend'):
                    if boss_weak or boss_attac:
                        print('player failed to weaken boss')
                        out_msg = "{} \n Boss attacs are already weakened / They have already attacked!".format(message.author.mention)
                        await message.channel.send(content=out_msg)
                    else:
                        boss_weak = True
                        print('setting boss_weak to true')
                        out_msg = "{} \n Boss has a 50% chance to miss when attacking!".format(message.author.mention)
                        await message.channel.send(content=out_msg)
                        count_player_action(message)
                        
                #weaken boss AC
                elif message.content.startswith('weaken'):
                    if (boss_AC == 2):
                        out_msg = "{} \n Boss AC is already 2!".format(message.author.mention,boss_AC)
                        await message.channel.send(content=out_msg)
                        return
                    boss_AC -= np.random.randint(1,high=7)
                    if boss_AC < 2:
                        boss_AC = 2
                    print('boss AC set to {}'.format(boss_AC))
                    out_msg = "{} \n You lowered the boss AC to {}!".format(message.author.mention,boss_AC)
                    await message.channel.send(content=out_msg)
                    count_player_action(message)
                
                #resurrect dead player      
                elif message.content.startswith('resurrect'):    
                    if not player_dead:
                        print('player failed to resurrect')
                        out_msg = "{} \n Theres no dead player to resurrect!".format(message.author.mention)
                        await message.channel.send(content=out_msg)
                    else:
                        print(boss_target)
                        print(boss_target[:-5])
                        try:
                            attacked_userlist.remove(boss_target[:-5])
                            attacked_usertwice.remove(boss_target[:-5])
                        except:
                            out_msg = "{} \n mm nope".format(message.author.mention,boss_target)
                            await message.channel.send(content=out_msg)
                            return
                        out_msg = "{} \n You resurrected {}! They are buff AF!".format(message.author.mention,boss_target)
                        await message.channel.send(content=out_msg)
                        count_player_action(message)
            
        #============================
        #if normal day - no boss fight
            
        else:    
            if message.content.startswith('attac'):
                if (message.author.name not in attacked_userlist) and (message.author.name != tgt_name[:-5]): 
                    attacked_userlist.append(message.author.name)
                    atk = np.random.randint(1,high=21)
                    if atk < tgt_AC:
                        out_msg = "{} \n**Attack Roll:** {}\nYou Missed!".format(message.author.mention,atk)#bumpkin_user.mention
                        await message.channel.send(content=out_msg)
                    else:
                        if atk==20:
                            dmg = dmg_roll_crit(boss_attac_buff)
                        else:
                            dmg = dmg_roll(boss_attac_buff)               
                        if (np.random.randint(1,high=2001)==1):
                            print('super roll')
                            dmg += dmg_roll_super()
                    
                        tgt_health -= dmg
                        
                        if (tgt_health <= 0):
                            tgt_health = 0
                            out_msg = "{} \n**Attack Roll:** {}\nYou hit for {} damage and killed {}!".format(message.author.mention,atk,dmg,tgt_name[:-5])
                            await message.channel.send(content=out_msg)
                            try:
                                await tgt_member.add_roles(norights_role)
                                await tgt_member.edit(nick = 'This motherfucker has died')
                            except:
                                print('couldnt change nickname')
                            print(tgt_member)
                            print('{} attacked by {} for {}dmg and now has {}hp left'.format(tgt_name[:-5],message.author,dmg,tgt_health))

                        else:
                            out_msg = "{} \n**Attack Roll:** {}\nYou hit for {} damage, {} has {}/{} hp left!".format(message.author.mention,atk,dmg,tgt_name[:-5],tgt_health,tgt_health_max)
                            await message.channel.send(content=out_msg)
                            print('{} attacked by {} for {}dmg and now has {}hp left'.format(tgt_name[:-5],message.author,dmg,tgt_health))
                
                else:
                    await message.channel.send(content="{} \nYou already rolled today!".format(message.author.mention))
                if str(message.author) == str(tgt_member):
                    await message.channel.send(content="{} \nYou can't attac yourself!".format(message.author.mention))

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
            try:
                await tgt_member.remove_roles(norights_role)
                await tgt_member.edit(nick = tgt_nick)
            except:
                print('cant')
            daily_reset()
            #os.environ['bumpkin_health'] = str(bumpkinhealth)
            await message.channel.send(content='target hp has been reset to max, daily reset forced')
            print('target hp has been reset to max, daily reset forced')

        #kill bumpkin
        if message.content.startswith('!kill'):
            #await client.add_roles(bumpkin_user,norights_role)
            tgt_health=0
            try:
                await tgt_member.add_roles(norights_role)
                await tgt_member.edit(nick = 'This motherfucker has died')
            except:
                print('cant')
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


