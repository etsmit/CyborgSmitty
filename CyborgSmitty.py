#discord bot

#evanpy / python3

#from funcs import *


import os
import discord

import numpy as np

from dotenv import load_dotenv

from datetime import datetime


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
pause.until(datetime(2022,2,1,16,20))
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
tgt_maxhealth = 400
tgt_health=tgt_healthmax


#need to roll tgt_AC or higher on the attack to hit
tgt_AC = 8

#xanxus85 can attac X times a day
xanxus = 0

#cloud gets the attac X times
cloud = 0
    

#buffs to player damage (num of extra d10s)
boss_attac_buff=0

#50% chance for boss to miss?
#true if true
boss_weak = False


#amount of times resurrected player has attacked
#can attac 3x (done by removing them from attacked_usertwice after their second action)
res_player_attacs = 0


#boss attack count
#has boss attacked?
boss_attac = 0
player_dead = 0

#boss target has to be initialized as empty string first
boss_target = ''

#save some data to help balance the game
total_daily_dmg_list = []
total_daily_actions_list = []
total_daily_dmg = 0
total_daily_actions = 0

help_msg="""
Command : Function

Each player has two actions and can:
    attac     : same attac as usual
    weaken    : lower the boss AC by 1d6 (down to minimum of 2)
    defend    : protect your teammates! 50% chance for the boss to miss their attac!
    buff      : add an extra 1d10 to the rest of the attacs for the day!
    resurrect : (takes 2 actions) resurrect the dead teammate! They come back with 3 actions, +5 to attac roll, and 1d10 damage buff!

Other commands:
    !raidstatus : status update
    !hello      : hello world
    !CyborgHalp : this help message

Admin commands:
    !howdoyouturnthison : Revive target, clear people to attac again
    !newhealth          : set target's max health (default 500)
    !newAC              : set target's AC (default 2)
    !kill               : kill target
    !clearattacs        : clear all peeps to attac again

For the cursed target:
    The target can attac one player ONCE and instakill them!
    Use your target's full discord username with the numbers, for example "attac bumpkinbatchboi#7429"
"""




#=======================================================
#functions
#=======================================================

#Damage rolls
#roll 4d6+10 damage (14 - 34),avg 24
#roll 4d10 damage (4 - 40),avg 22
def dmg_roll(buff):
    out = 0
    for i in range(4+buff):
        out += np.random.randint(1,high=13)
    return out

#double the amount of dice on a crit
def dmg_roll_crit(buff):
    out = 0
    for i in range(8+2*buff):
        out += np.random.randint(1,high=13)
    return out
    

#1 in 2000 chance of dealing LOTS of damage (200d20) 
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
    global total_daily_actions
    action_count = attac_counter(msg)
    if msg.content.startswith('resurrect'):
        if action_count == 0:
            attacked_userlist.append(msg.author.name)
            attacked_usertwice.append(msg.author.name)
            total_daily_actions += 2
        elif action_count > 0:
            return  
    else: 
        if action_count == 0:
            attacked_userlist.append(msg.author.name)
        elif action_count == 1:
            if msg.author.name not in attacked_userlist:
                attacked_userlist.append(msg.author.name)
                total_daily_actions += 1
            else:
                attacked_usertwice.append(msg.author.name)
                total_daily_actions += 1
        elif action_count == 2:
            return
    print(attacked_userlist)
    print(attacked_usertwice)
  
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

#logging in
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
    
    

#daily restart function
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
    global total_daily_actions
    global total_daily_actions_list
    global total_daily_dmg
    global total_daily_dmg_list
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
        
        #save previous day's data
        total_daily_actions_list.append(total_daily_actions)
        total_daily_actions = 0
        np.save('total_daily_actions.npy',np.array(total_daily_actions_list))
        
        total_daily_dmg_list.append(total_daily_dmg)
        total_daily_dmg = 0
        np.save('total_daily_dmg.npy',np.array(total_daily_dmg_list))
          
        boss_AC = 8
        boss_weak = False
        boss_attac = 0
        player_dead = 0
        res_player_attacs = 0
        boss_attac_buff = 0
        boss_target = ''

        print('daily: attac list cleared')
        if (tgt_health == 0):
            try:
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
        out_msg = """I have reset.\n The target is {}!""" .format(tgt_name)
        tgt_health= tgt_max_health
        await attacs_chan.send(out_msg)
   
daily_reset.start()


#reading actions and commands
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
    global total_daily_dmg

    
    if message.author == client.user:
        return


    if action_check(message):
        if bossfight:
            #===============================
            #check action count of player and stop them if they don't have the actions
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
                        total_daily_dmg += dmg
                        if (tgt_health <= 0):
                            tgt_health = 0
                            out_msg = "{} \n**Attack Roll:** {}\nYou hit for {} damage and killed THE BOSS {}!".format(message.author.mention,atk,dmg,tgt_name[:-5])
                            await message.channel.send(content=out_msg)
                            try:
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
            
    #Other stuff not directly in the raid
    #hello world          
    if message.content.startswith('!hello'):
        await message.channel.send(content='Hello!')
    
    #status update    
    if message.content.startswith('!raidstatus'):
        out_text = "target health: {}/{}\nYou need to roll a {} or higher to hit\nPeople who have attac'd: ".format(tgt_health,tgt_health_max,tgt_AC)
        #count up actions used by players
        for name in attacked_userlist:
            this_count = 1
            if name in attacked_usertwice:
                this_count += 1
            out_text = out_text + name + f' {this_count}/2 || '
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
        #revive target
        if message.content.startswith('!howdoyouturnthison'):
            await message.channel.send(content='{}'.format(message.author.mention))
            attacked_userlist=[]
            attacked_usertwice=[]
            tgt_health=tgt_health_max
            xanxus=0
            #await client.remove_roles(bumpkin_user,norights_role)
            #await tgt_member.add_roles(somerights_role)
            try:
                await tgt_member.edit(nick = tgt_nick)
            except:
                print('cant')
            daily_reset()
            #os.environ['bumpkin_health'] = str(bumpkinhealth)
            await message.channel.send(content='Target hp has been reset to max, daily reset forced')
            print('Target hp has been reset to max, daily reset forced')

        #kill target 
        if message.content.startswith('!kill'):
            tgt_health=0
            try:
                await tgt_member.edit(nick = 'This motherfucker has died')
            except:
                print('cant')
            await message.channel.send(content='A bot admin killed the target')
            print('A bot admin killed the target')
        
        #set max health    
        if message.content.startswith('!newhealth'):
            try:
                tgt_health_max = int(message.content[11:])
                tgt_health = tgt_health_max
                await message.channel.send(content="target's max health now {}".format(tgt_health_max))
                print("Target's max health now {}".format(tgt_health_max))
            except:
                await message.channel.send(content="Try putting in an actual integer")
                
        #set new AC    
        if message.content.startswith('!newAC'):
            try:
                tgt_AC = int(message.content[7:])
                #bumpkin_AC = bumpkin_max
                await message.channel.send(content="target AC now {}".format(tgt_AC))
                print("target AC now {}".format(tgt_AC))
            except:
                await message.channel.send(content="Try putting in an actual integer")
        
        #clear actions of everyone  
        if message.content.startswith('!clearattacs'):
            attacked_userlist=[]
            attacked_usertwice=[]
            xanxus = 0
            await message.channel.send(content='Everyone can now attac again')
            print('userlist cleared')
                
         
                          
                 

   


client.run(TOKEN)


