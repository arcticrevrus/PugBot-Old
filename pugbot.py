import interactions
import asyncio
from config import token

bot = interactions.Client(token, intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

dps_queue = []
healer_queue = []
tank_queue = []
prevmsg = ""
lock = asyncio.Lock()


dps_button = interactions.Button(
	style=interactions.ButtonStyle.DANGER,
	label="DPS",
	custom_id="dps_click",
)

tank_button = interactions.Button(
	style=interactions.ButtonStyle.SECONDARY,
	label="Tank",
	custom_id="tank_click",
)

healer_button = interactions.Button(
	style=interactions.ButtonStyle.SUCCESS,
	label="Healer",
	custom_id="healer_click",
)

@bot.event
async def on_start():
	for guild in bot.guilds:
		chans = await guild.get_all_channels()
		for channel in chans:
			if channel.name == "mythic-plus-pickup":
				await channel.send("********Bot has been reloaded********")
				await channel.send("Click a button to add to the queue.",
						components=[tank_button, healer_button, dps_button])



@bot.event
async def on_message_create(message: interactions.message):
	global prevmsg
	chan = await interactions.get(bot, interactions.Channel, object_id=message.channel_id)
	if str(chan) == "mythic-plus-pickup":
		if message.author != bot.me:
			if prevmsg != "":
				await prevmsg.delete()
				await chan.send("Click a button to add to the queue.",
					components=[tank_button, healer_button, dps_button])
		if message.author == bot.me:
			if "Click a button to add to the queue." in message.content:
				prevmsg = message
			else:
				if prevmsg != "":
					await prevmsg.delete()
					await chan.send("Click a button to add to the queue.",
						components=[tank_button, healer_button, dps_button])
			


async def queue_check(ctx: interactions.ComponentContext):
	if(len(tank_queue) >= 1 and len(dps_queue) >= 3 and len(healer_queue) >= 1):
		for tank in tank_queue:
			filled_queue_notify=[]
			filled_queue=[]
			filled_queue_notify.append(f"<@{tank.id}>")
			filled_queue.append(tank)
			for healer in healer_queue:
				if tank != healer:
					filled_queue_notify.append(f"<@{healer.id}>")
					filled_queue.append(healer)
					for dps in dps_queue:
						if len(filled_queue) < 5:
							if tank != dps:
								if healer != dps:
									filled_queue_notify.append(f"<@{dps.id}>")
									filled_queue.append(dps)
		if(len(filled_queue) == 5):
			await ctx.channel.send("A group has been found!" + ' , '.join(filled_queue_notify))
			for user in filled_queue:
				if user in tank_queue:
					tank_queue.remove(user)
				if user in healer_queue:
					healer_queue.remove(user)
				if user in dps_queue:
					dps_queue.remove(user)
                

@bot.component("dps_click")
async def _click_me(ctx: interactions.ComponentContext):
	user=ctx.user
	member = await interactions.get(bot, interactions.Member, object_id=user.id, guild_id=ctx.guild_id)
	if member.nick == None:
		member = member.username
	else:
		member = member.nick
	async with lock: 
		if user not in dps_queue:
			dps_queue.append(user)
			await ctx.channel.send(f"{member} added to queue as dps!")
			await queue_check(ctx)
		else:
			dps_queue.remove(user)
			await ctx.channel.send(f"{member} has been removed from the dps queue.")

@bot.component("tank_click")
async def _click_me(ctx: interactions.ComponentContext):
	user=ctx.user
	member = await interactions.get(bot, interactions.Member, object_id=user.id, guild_id=ctx.guild_id)
	if member.nick == None:
		member = member.username
	else:
		member = member.nick
	async with lock: 
		if user not in tank_queue:
			tank_queue.append(user)
			await ctx.channel.send(f"{member} added to queue as tank!")
			await queue_check(ctx)
		else:
			tank_queue.remove(user)
			await ctx.channel.send(f"{member} has been removed from the tank queue.")

@bot.component("healer_click")
async def _click_me(ctx: interactions.ComponentContext):
	user=ctx.user
	member = await interactions.get(bot, interactions.Member, object_id=user.id, guild_id=ctx.guild_id)
	if member.nick == None:
		member = member.username
	else:
		member = member.nick
	async with lock: 
		if user not in healer_queue:
			healer_queue.append(user)
			await ctx.channel.send(f"{member} added to queue as healer!")
			await queue_check(ctx)
		else:
			healer_queue.remove(user)
			await ctx.channel.send(f"{member} has been removed from the healer queue.")



@bot.command(
	name="queue",
	description="Show the queue status.",
)
async def queue(ctx: interactions.CommandContext):
	tql = []
	hql = []
	dql = []
	for tank in tank_queue:
		member = await interactions.get(bot, interactions.Member, object_id=tank.id, guild_id=ctx.guild_id)
		if member.nick == None:
			member = member.username
		else:
			member = member.nick
		tql.append(f"{member}")
	for healer in healer_queue:
		member = await interactions.get(bot, interactions.Member, object_id=healer.id, guild_id=ctx.guild_id)
		if member.nick == None:
			member = member.username
		else:
			member = member.nick
		hql.append(f"{member}")
	for dps in dps_queue:
		member = await interactions.get(bot, interactions.Member, object_id=dps.id, guild_id=ctx.guild_id)
		if member.nick == None:
			member = member.username
		else:
			member = member.nick
		dql.append(f"{member}")

	await ctx.send(		"The current queue:" + "\n" +
		"<:tank:444634700523241512> : " + ', '.join(tql) + "\n" +
		"<:heal:444634700363857921> : " + ', '.join(hql) + "\n" +
		"<:dps:444634700531630094> : " + ', '.join(dql))

@bot.command(
	name="add",
	description="Add to the queue.",
	options= [
		interactions.Option(
			name="role",
			description="Roles you want to join as, seperated by comma. Accepted values are: tank, healer, dps.",
			type=interactions.OptionType.STRING,
			required=True,
			autocomplete=True,
		),
	],
)
async def _button(ctx: interactions.CommandContext, role: str = ""):
	user = ctx.user
	member = await interactions.get(bot, interactions.Member, object_id=ctx.user.id, guild_id=ctx.guild_id)
	if member.nick == None:
		member = member.username
	else:
		member = member.nick
	role_add_list = []
	role_remove_list = []
	if role != "":
		if "tank" in role:
			if user not in tank_queue:
				role_add_list.append("Tank")
				tank_queue.append(user)
				await queue_check(ctx)
			else:
				role_remove_list.append("Tank")
				tank_queue.remove(user)

		if "heal" in role:
			if user not in healer_queue:
				role_add_list.append("Healer")
				healer_queue.append(user)
				await queue_check(ctx)
			else:
				role_remove_list.append("Healer")
				healer_queue.remove(user)
		if "dps" in role:
			if user not in dps_queue:
				role_add_list.append("DPS")
				dps_queue.append(user)
				await queue_check(ctx)
			else:
				role_remove_list.append("DPS")
				dps_queue.remove(user)
		if role_add_list != []:
			await ctx.send(f"{member} joined the queue as {', '.join(role_add_list)}.")
		if role_remove_list != []:
			await ctx.send(f"{member} left the queue as {', '.join(role_remove_list)}.")
		if "tank" not in role:
			if "heal" not in role:
				if "dps" not in role:
					await user.send("No valid role specified, acceptable roles are `tank` `healer` and `dps`.")
	else:
		await ctx.send(	"Click a button to add to the queue.",
			components=[tank_button, healer_button, dps_button])

bot.start()