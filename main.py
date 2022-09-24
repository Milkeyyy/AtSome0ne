import asyncio
from code import interact
import datetime
from lib2to3.pgen2.token import OP
import discord
from discord.commands import Option
import logging
import json
import uuid

logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)

# 今
def now():
	return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

# ログ出力
def log(text):
	print(f"[{now()}] " + text)

# ユーザーID一覧をユーザー一覧に変換
def convertToUserFromID(id_list):
	user_list = []
	for id in id_list:
		user_list.append(client.get_user(id))
	return user_list

# リストを箇条書き化
def convertToBulletPointsFromList(list: list):
	bp = ""
	for index, item in enumerate(list):
		if index == list.count:
			bp = bp + "・" + item.name
		else:
			bp = bp + "・" + item.name + "\n"
	return bp

def convertToUserBulletPointsFromIDList(id_list):
	return convertToBulletPointsFromList(convertToUserFromID(id_list))

#Botの名前
bot_name = "Some0ne"
#Botのバージョン
bot_version = "1.0"

#くらいあんと
intents = discord.Intents.all()
client = discord.Bot(intents = intents)

# ゲーム一覧
gamelist = {"Rainbow Six Siege": {"RoleId": 0}, "Apex Legends": {"RoleId": 0}}

default_guilddata_item = {"recruitment_channel_id": 0, "gamelist": gamelist}
guilddata = {}

default_userdata_item =  {"Atmark": False, "Game": "", "NumberOfPeople": 0, "Member": [], "MessageId": 0}
userdata = {}

invitedata = {}

def createUserData():
	global userdata

	# ユーザーデータを作成
	for guild in client.guilds:
		userdata[guild.id] = {}
		for member in guild.members:
			userdata[guild.id][member.id] = default_userdata_item

# ギルドデータの確認
def checkGuildData():
	global guilddata

	for guild in client.guilds:
		if guilddata.get(guild.id) == None:
			guilddata[guild.id] = default_guilddata_item

# ギルドデータの読み込み
def loadGuildData():
	# グローバル変数宣言
	global guilddata

	checkGuildData()
	try: # ファイルが存在しない場合
		# ファイルを作成して初期データを書き込む
		file = open("guild.json", "x")
		file.write(json.dumps(guilddata, indent = 2, sort_keys=True))
		file.close()
		# ファイルから読み込む
		file = open("guild.json", "r")
		guilddata = json.load(file)
		file.close()

	except FileExistsError: # ファイルが存在する場合
		# ファイルから読み込む
		file = open("guild.json", "r")
		guilddata = json.load(file)
		file.close()

# ギルドデータの保存
def saveGuildData():
	# グローバル変数宣言
	global guilddata

	# 書き込み用にファイルを開く
	file = open("guild.json", "w")
	# 辞書をファイルへ保存
	file.write(json.dumps(guilddata, indent = 2, sort_keys=True))
	file.close()
	loadGuildData()

# Bot起動時のイベント
@client.event
async def on_ready():
	print("---------------------------------------")
	print(f" {bot_name} - Version {bot_version}")
	print(f" using Pycord {discord.__version__}")
	print(f" Developed by Milkeyyy")
	print("---------------------------------------")
	log(f"{client.user} へログインしました！ (ID: {client.user.id})")

	#プレゼンスを設定
	await client.change_presence(activity=discord.Game(name=f"Version {bot_version}"))

	# ユーザーデータを作成
	createUserData()

	# ギルドデータを確認&読み込み
	loadGuildData()

@client.command(description="このBotの情報を表示します。")
async def about(ctx):
	embed = discord.Embed(color=discord.Colour.from_rgb(234,197,28))
	embed.set_author(name=bot_name,icon_url=client.user.display_avatar.url)
	embed.add_field(name=f"Version",value=f"`{bot_version}`")
	embed.add_field(name=f"Pycord",value=f"`{discord.__version__}`")
	embed.set_footer(text=f"Developed by Milkeyyy")
	await ctx.respond(embed=embed)
	print(f"[{now()}] コマンド実行: about / 実行者: {ctx.user}")

uicmd = client.create_group("ui", description="UIに関する管理を行うためのコマンドです。")

class InviteView(discord.ui.View):
	@discord.ui.select(
		placeholder = "ゲームタイトルを選択",
		min_values = 1,
		max_values = 1,
		options = [
			discord.SelectOption(
				label="Rainbow Six Siege",
				description="Ubisoft Montréal"
			),
			discord.SelectOption(
				label="Apex Legends",
				description="Respawn Entertainment"
			)
		]
	)
	async def select_callback(self, select, interaction):
		await interaction.response.send_message(f"Select: {select.values[0]}")

	@discord.ui.button(label="", style=discord.ButtonStyle.green)
	async def button_callback(self, button, interaction):
		await interaction.response.send_message("", ephemeral=True)

#@client.command(description="指定したテキストチャンネルへUIを作成します。")
#async def create(ctx):

class InviteView(discord.ui.View):
	@discord.ui.button(label="参加", emoji="✅", style=discord.ButtonStyle.green)
	async def button_callback(self, button, interaction):
		global userdata
		global invitedata

		# 募集IDを取得
		id = self.message.embeds[0].footer.text.lstrip("ID: ")
		# 募集者のIDを取得
		author_id = invitedata[id]["author_id"]

		# ボタンを押したのが募集者本人の場合
		if author_id == interaction.user.id:
			embed = discord.Embed(color=discord.Colour.from_rgb(205, 61, 66), description=":no_entry_sign: 自分で自分の募集に参加することはできません...:cry:")
			await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
		# それ以外の場合
		else:
			# 既に募集に参加している場合
			if interaction.user.id in invitedata[id]["member"]:
				embed = discord.Embed(color=discord.Colour.from_rgb(205, 61, 66), description=":no_entry_sign: あなたは既にこの募集に参加しています！")
				await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
			# 募集に参加していない場合
			else:
				# 募集データにユーザーIDを追加
				invitedata[id]["member"].append(interaction.user.id)

				# 埋め込みの参加者リストを更新
				original_embed = self.message.embeds[0]
				for field in original_embed.fields:
					if field.name == "参加者":
						field.value = convertToUserBulletPointsFromIDList(invitedata[id]["member"])
				await self.message.edit(self.message.content, embed=original_embed, view=InviteView(timeout=invitedata[id]["timeout"]))

				# 埋め込みメッセージを作成して返信
				embed = discord.Embed(color=discord.Colour.from_rgb(131, 177, 88))
				embed.set_author(name=f"{interaction.user} さんが参加しました", icon_url=interaction.user.display_avatar.url)
				embed.set_footer(text=f"ID: {id}")
				await interaction.response.send_message(embed=embed)

	# 時間制限が来た時
	async def on_timeout(self):
		# 募集IDを取得
		msgembed = self.message.embeds[0] #need fix
		id = msgembed.footer.text.lstrip("ID: ")
		self.clear_items()
		# 募集を終了
		endInvite(self.message.guild.id, self.message.author.id, id)

		#埋め込みメッセージを作成して返信する
		embed = discord.Embed(color=discord.Colour.from_rgb(205, 61, 66), description=":no_entry_sign: この募集は締め切られました。")
		await self.message.edit(embed=embed)

@client.command(description = "メンバーの募集を開始します。")
async def recruitment(
	ctx,
	game: Option(str, name = "ゲーム", description = "募集するゲームタイトル", autocomplete = discord.utils.basic_autocomplete(dict.keys(gamelist))),
	nop: Option(int, name = "人数", description = "募集する人数", autocomplete = discord.utils.basic_autocomplete([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])),
	timeout: Option(float, required = False, min_value = 10, max_value = 600, default = 60, name = "制限時間", description = "募集を締め切るまでの時間(秒) 指定しない場合は60秒になります。", autocomplete = discord.utils.basic_autocomplete([15,30,45,60]))
):
	global userdata
	global guilddata
	global invitedata

	ud = userdata[ctx.guild_id][ctx.author.id]
	if ud["Atmark"] == True:
		ud["Atmark"] = False
		embed = discord.Embed(color=discord.Colour.from_rgb(205, 61, 66))
		embed.add_field(name=f":no_entry_sign: 既に募集が開始されています！", value=f"再度募集を行うには、一度募集をキャンセルしてください！")
		embed.set_author(name=bot_name, icon_url=client.user.display_avatar.url)
		await ctx.respond(embed=embed, ephemeral=True)
	else:
		ud["Atmark"] = True
		ud["Game"] = game
		# メンションするロールのIDを取得
		rid = guilddata[f"{ctx.guild_id}"]["gamelist"][game]["RoleId"]
		# メンションするロールをIDから取得 ロールが設定されていない場合は、メンションしない
		if rid == 0:
			role = ""
		else:
			# ロールが設定されている場合は <@ID> になる
			role = ctx.guild.get_role(rid).mention

		# 募集IDを生成
		id = str(uuid.uuid4())

		# 募集用埋め込みメッセージを作成
		embed = discord.Embed(color=discord.Colour.from_rgb(131, 177, 88), title=":loudspeaker: メンバー募集")
		embed.add_field(name=f"🎮 ゲーム", value=f"**{game}**")
		embed.add_field(name="**@**", value=f"**`{nop}`**")
		embed.add_field(name="参加者", value=f"・{ctx.author}")
		embed.set_footer(text=f"ID: {id}")
		embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)
		# 募集メッセージを送信 (募集用テキストチャンネルが指定されていない場合は、コマンドが実行されたチャンネルへ送信する)
		if guilddata[f"{ctx.guild_id}"]["recruitment_channel_id"] == 0:
			rch = client.get_channel(ctx.channel_id)
		else:
			rch = client.get_channel(guilddata[f"{ctx.guild_id}"]["recruitment_channel_id"])
		rmsg = await rch.send(embed=embed, view=InviteView(timeout=timeout, disable_on_timeout=True))

		# 募集開始通知用埋め込みメッセージを作成
		notification_embed = discord.Embed(color=discord.Colour.from_rgb(131, 177, 88), title="メンバーの募集を開始しました。", description=f"[クリックで募集メッセージへ]({rmsg.jump_url})")
		notification_embed.set_footer(text=f"ID: {id}")
		# 募集開始通知を送信 (返信)
		rp = await ctx.respond(f"{role}", embed=notification_embed, ephemeral=True)
		# メッセージのIDを取得
		om = await rp.original_message()
		ud["MessageId"] = om.id
		# 募集データを作成
		startInvite(ctx.guild_id, ctx.author.id, om.id, game, nop, id, timeout)
		# 参加者一覧に募集者自身を追加する
		invitedata[id]["member"].append(ctx.author.id)



@client.command(description = "メンバーの募集をキャンセルします。")
async def cancelrecruitment(ctx):
	global userdata

	ud = userdata[ctx.guild_id][ctx.author.id]
	udg = ud["Game"]
	# メッセージを取得
	msg = client.get_message(ud["MessageId"])
	# 募集IDを取得
	id = msg.embeds[0].footer.text.lstrip("ID: ")

	if ud["Atmark"] == True:
		# 募集を終了
		endInvite(ctx.guild_id, ctx.author.id, id)

		#埋め込みメッセージを作成
		embed = discord.Embed(color=discord.Colour.from_rgb(205, 61, 66), title=":no_entry_sign: 募集はキャンセルされました", description="この募集には参加できません。")
		await msg.edit(embed=embed)
		await ctx.respond(f"`{udg}` の募集がキャンセルされました。", ephemeral=True)
	else:
		ud["Atmark"] = True
		await ctx.respond("募集が開始されていません！", ephemeral=True)

def startInvite(guild, author, message, game, nop, id, timeout):
	global userdata
	global invitedata

	ud = userdata[guild][author]
	# ユーザーデータの募集状態を有効に変える
	ud["Atmark"] = True
	# ユーザーデータの募集ゲームタイトルを変える
	ud["Game"] = game
	# 募集状態データを作成
	invitedata[id] = {"author_id": author, "message_id": message, "game": game, "nop": nop, "timeout": timeout, "member": []}

def endInvite(guild, author, id):
	global userdata
	global invitedata

	ud = userdata[guild][author]
	# ユーザーデータの募集状態を無効に変える
	ud["Atmark"] = False
	# 募集状態データからこの募集を削除する
	del invitedata[id]

#==================== 設定関連コマンド ====================#
@client.command(description = "ゲームタイトルごとのロールを設定します。")
async def setrole(
	ctx,
	game: Option(str, name = "ゲーム", description = "設定するゲームタイトル", autocomplete = discord.utils.basic_autocomplete(dict.keys(gamelist))),
	role: Option(discord.Role, name = "ロール", description = "募集時にメンションするロール")
):
	global guilddata

	guilddata[str(ctx.guild_id)][game]["RoleId"] = role.id
	saveGuildData()
	await ctx.respond(f"`{game}` の対象ロールを {role} に設定しました。", ephemeral=True)

@client.command(description = "メンバー募集のメッセージを送信するテキストチャンネルを設定します。")
async def setrecruitmentchannel(
	ctx,
	ch: Option(discord.TextChannel, name = "テキストチャンネル", description = "メンバー募集のメッセージを送信するテキストチャンネル")
):
	global guilddata

	# ギルドデータに指定されたテキストチャンネルのIDを設定
	guilddata[str(ctx.guild_id)]["recruitment_channel_id"] = ch.id

	await ctx.respond(f"メンバー募集メッセージの送信チャンネルを <#{ch.id}> に設定しました。", ephemeral=True)
#==================== 設定関連コマンド ====================#

#==================== ぼっとへログイン ====================#
client.run("MTAyMjUwODgwNDkyNTAzODU5Mg.G5p3mD.cjYaQkQw9LWfvFx--MZEGzO3bLZ9t8yPbXLoeg")