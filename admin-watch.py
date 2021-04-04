import discord
import json
import traceback
import configparser
from time import time
#from time import sleep

#admins_data_cfg = configparser.ConfigParser()
#admins_data_cfg.read("admins_data.ini")
admins_data = {}
config = configparser.ConfigParser()
config.read("config.ini")
try: whitelist = [int(wl) for wl in config["whitelist"]["list"].split(',')]
except ValueError : whitelist = []
try: owners = [int(owner) for owner in config["owners"]["list"].split(',')]
except ValueError : owners = []

#loading configparser into dictionary
#for admin_id in admins_data_cfg:
#	if admin_id.isdigit():
#		admins_data[int(admin_id)] = {}
#		for action in admin_id:
#			admins_data[int(admin_id)][action] = {}
#			for key in action:
#				admins_data[int(admin_id)][action][key] = int(admins_data_cfg[admin_id][action][key])
try:
	with open('admins_data.json', 'r') as of:
		admins_data = json.load(of)
except:
	pass
async def write_into_data(admin,action,guild,client):
	#sleep(5)
	#print("here")
	admin_id = admin.id
	_admin_id = str(admin_id)
	if (config[action]["state"] == "off") or (admin_id in whitelist or admin_id in owners) or (guild.id != int(config["guild"]["id"])):
		return
	#print("here2")
	try:
		if int(admins_data[_admin_id][action]["first_try_time"])+int(config[action]["actionInterval"]) < time() :
			del admins_data[_admin_id][action]
	except :
		pass
	if _admin_id in admins_data.keys():
		if action in admins_data[_admin_id].keys():
			admins_data[_admin_id][action]["actionCount"] = int(admins_data[_admin_id][action]["actionCount"]) + 1
		else:
			admins_data[_admin_id][action] = {}
			admins_data[_admin_id][action]["actionCount"] = 1
			admins_data[_admin_id][action]["first_try_time"] = time()
	else:
		admins_data[_admin_id] = {}
		admins_data[_admin_id][action] = {}
		admins_data[_admin_id][action]["actionCount"] = 1
		admins_data[_admin_id][action]["first_try_time"] = time()
	warningEmbed= discord.Embed(
		title="**action:**    "+action,
		color=0xff00d0)
	warningEmbed.add_field(name=":warning: **warnings:**",value="{0}/{1}".format(admins_data[_admin_id][action]["actionCount"],config[action]["actionLimit"]),inline=False)
	if int(admins_data[_admin_id][action]["actionCount"]) != int(config[action]["actionLimit"]):
		warningEmbed.add_field(name=":watch: **timer:**",value="{0} sanie ta pak shodan warning ha".format(int((int(admins_data[_admin_id][action]["first_try_time"])+int(config[action]["actionInterval"]))-time())),inline=False)
	warningEmbed.add_field(name=":bust_in_silhouette: **executer:**",value="<@{0}>".format(admin_id),inline=False)
	await client.get_channel(int(config[action]["logChannel"])).send(
		embed=warningEmbed)

	#admin = client.get_user(admin_id)
	#print(admin.dm_channel)
	if int(admins_data[_admin_id][action]["actionCount"]) >= int(config[action]["actionLimit"]):
		try:
			await guild.kick(user=admin,reason=action+'|'+str(config[action]["actionLimit"])+'|'+str(config[action]["actionInterval"]))
			await client.get_channel(int(config['guild']['adminkick_channel'])).send(content=":white_check_mark: <@{0}> kick shod | action: {1}".format(admin_id,action))
#			dm_channel = admin.dm_channel or await admin.create_dm()
#			await dm_channel.send(content="man shoma ra kick kardam shoma mitunid dobare join bedid\nhttps://discord.gg/KVWZCpX")
		except discord.errors.Forbidden:
			await client.get_channel(int(config['guild']['adminkick_channel'])).send(content=":x:Permission Error:x: <@{0}> kick nemishe | action: {1}\n<@{2}>".format(admin_id,action,705884643379118090))
		except:
			await client.get_channel(int(config['guild']['adminkick_channel'])).send(content=":x:Unknown Error:x: <@{0}> kick nemishe | action: {1}\n<@{2}>".format(admin_id,action,705884643379118090))
			traceback.print_exc()
		try:
			del admins_data[_admin_id]
		except KeyError:
			pass
	with open('admins_data.json', 'w') as of:
		json.dump(admins_data,of)

async def find(entries,id):
	async for entry in entries:
		#print(entry.user)
		#print(entry.target.id)
		if entry.target.id == id:
			return entry

async def send_help_message(channel):
	embedVar = discord.Embed(title="example", description=".command 5346463645343", color=0x00ff00)
	#embedVar.add_field(name=".addwl", value="Add To White List", inline=False)
	#embedVar.add_field(name=".rmwl", value="Remove From White List", inline=False)
	embedVar.add_field(name=".owners",value="Owners",inline=False)
	embedVar.add_field(name=".wl",value="White List",inline=False)
	await channel.send(embed=embedVar)
	#await channel.send("example: .command 5346463645343")
def update_config(list_name,_list):#owners|whitelist , remove|add , 435453 , owners|whitelist
	config[list_name]["list"] = ""
	for body in _list:
		config[list_name]["list"] += str(body)
		if body != _list[-1]:
			config[list_name]["list"] += ',' 
	with open('config.ini','w') as cfg:
		config.write(cfg)

class MyClient(discord.Client):#bot add - 
	async def on_ready(self):
		print("library version: "+discord.__version__)
		print('Logged on as {0}!'.format(self.user))
		await self.change_presence(status=discord.Status.do_not_disturb,activity=discord.Activity(type=discord.ActivityType.watching, name="Admins"))

	async def on_message(self, message):#.addwl | .rmwl | .addowner | .rmowner | .wl | .owners
		#print('Message from {0.author}: {0.content}'.format(message))
		if message.author.id in owners:
			if isinstance(message.channel,discord.DMChannel):
				if len(message.content.split(' ')) > 1 and message.content.split(' ')[1].isdigit():
					_id = int(message.content.split(' ')[1])
					if message.content.startswith(".addowner"):
						owners.append(_id)
						await message.channel.send("new owner : <@"+str(_id)+">")
						update_config(list_name="owners",_list=owners)
					elif message.content.startswith(".rmowner"):
						if _id in owners:
							owners.remove(_id)
							await message.channel.send("owner removed : <@"+str(_id)+">")
							update_config(list_name="owners",_list=owners)
						else:
							await message.channel.send("<@"+str(_id)+"> is not in list")
					elif message.content.startswith(".addwl"):
						whitelist.append(_id)
						await message.channel.send("new whitelist : <@"+str(_id)+">")
						update_config(list_name="whitelist",_list=whitelist)
					elif message.content.startswith(".rmwl"):
						if _id in whitelist:
							whitelist.remove(_id)
							await message.channel.send("removed from whitelist : <@"+str(_id)+">")
							update_config(list_name="whitelist",_list=whitelist)
						else:
							await message.channel.send("<@"+str(_id)+"> is not in list")
					else:
						await send_help_message(message.channel)
				elif message.content.startswith(".wl") :
					embedOfList = discord.Embed(title="whitelist",color=0x0000ff)
					for body in whitelist:
						embedOfList.add_field(name=whitelist.index(body),value="<@"+str(body)+">",inline=False)
					await message.channel.send(embed=embedOfList)

				elif message.content.startswith(".owners") :
					embedOfList = discord.Embed(title="owners",color=0x0000ff)
					for body in owners:
						embedOfList.add_field(name=owners.index(body),value="<@"+str(body)+">",inline=False)
					await message.channel.send(embed=embedOfList)
				else:
					await send_help_message(message.channel)
	
	#async def on_message_delete(self,message):
		#messageID = message.id
	#	print(message)
	#	if message.guild:
	#		entries = message.guild.audit_logs(limit=None,action=discord.AuditLogAction.message_delete)
	#		entry = await find(entries=entries,id=message.id)
	#		if entry:
	#			await write_into_data(admin=entry.user,action="message_delete",guild=message.guild,client=self)
	async def on_guild_channel_create(self,channel):
		#if channel.guild == premium:
		channelID = channel.id
		if channel.guild:
			entries = channel.guild.audit_logs(limit=None,action=discord.AuditLogAction.channel_create)
			entry = await find(entries=entries,id=channelID)
			if entry:
				await write_into_data(admin=entry.user,action="channel_create",guild=channel.guild,client=self)


	async def on_guild_channel_delete(self,channel):
		#if channel.guild == premium:
		channelID = channel.id
		if channel.guild:
			entries = channel.guild.audit_logs(limit=None,action=discord.AuditLogAction.channel_delete)
			entry = await find(entries=entries,id=channelID)
			if entry:
				await write_into_data(admin=entry.user,action="channel_delete",guild=channel.guild,client=self)
	async def on_guild_channel_update(self,before,after):
		#if channel.guild == premium:
		channelID = before.id
		if before.guild:
			entries = before.guild.audit_logs(limit=None,action=discord.AuditLogAction.channel_update)
			entry = await find(entries=entries,id=channelID)
			if entry:
				await write_into_data(admin=entry.user,action="channel_update",guild=before.guild,client=self)
	#on_guild_channel_delete
	#on_guild_channel_update
	async def on_member_remove(self,member):#kick&ban
		memberID = member.id
		#print("remove")
		entries = member.guild.audit_logs(limit=None,action=discord.AuditLogAction.kick)
		entry = await find(entries=entries,id=memberID)
		entries2 = member.guild.audit_logs(limit=None,action=discord.AuditLogAction.ban)
		entry2 = await find(entries=entries2,id=memberID)
		if entry and not entry2:
			await write_into_data(admin=entry.user,action="member_kick",guild=member.guild,client=self)
		elif entry2 and not entry:
			await write_into_data(admin=entry2.user,action="member_ban",guild=member.guild,client=self)
		elif entry and entry2:
			entry1_time = entry.created_at.timestamp()
			entry2_time = entry2.created_at.timestamp()
			if entry1_time < entry2_time:
				await write_into_data(admin=entry2.user,action="member_ban",guild=member.guild,client=self)
			elif entry2_time < entry1_time:
				await write_into_data(admin=entry.user,action="member_kick",guild=member.guild,client=self)
	async def on_member_unban(self,guild,user):#kick&ban
		userID = user.id
		entries = guild.audit_logs(limit=None,action=discord.AuditLogAction.unban)
		entry = await find(entries=entries,id=userID)
		if entry:
			await write_into_data(admin=entry.user,action="member_unban",guild=guild,client=self)

	#on_member_unban
	#on_guild_role_create
	#on_guild_role_delete
	async def on_guild_role_create(self,role):
		roleID = role.id
		entries = role.guild.audit_logs(limit=None,action=discord.AuditLogAction.role_create)
		entry = await find(entries=entries,id=roleID)
		if entry:
			await write_into_data(admin=entry.user,action="role_create",guild=role.guild,client=self)
	async def on_guild_role_delete(self,role):
		roleID = role.id
		entries = role.guild.audit_logs(limit=None,action=discord.AuditLogAction.role_delete)
		entry = await find(entries=entries,id=roleID)
		if entry:
			await write_into_data(admin=entry.user,action="role_delete",guild=role.guild,client=self)
	async def on_guild_role_update(self,before, after):
		roleID = before.id
		entries = before.guild.audit_logs(limit=None,action=discord.AuditLogAction.role_update)
		entry = await find(entries=entries,id=roleID)
		if entry:
			await write_into_data(admin=entry.user,action="role_update",guild=before.guild,client=self)


client = MyClient(max_messages=1000000000000000000)
client.run('')

