import asyncio
import datetime
import json
import logging
import os
import sys
import uuid
from code import interact
from dis import disco
from lib2to3.pgen2.token import OP

import discord
from discord.commands import Option

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
			bp = bp + "・" + item.mention
		else:
			bp = bp + "・" + item.mention + "\n"
	return bp

# ユーザーIDリスト → ユーザーオブジェクトリスト → ユーザー名箇条書き化
def convertToUserBulletPointsFromIDList(id_list):
	return convertToBulletPointsFromList(convertToUserFromID(id_list))

# トークン読み込み
def loadToken():
	global token

	token = os.getenv("TOKEN")

	if token == None:
		log("トークンが指定されていません...")
		sys.exit("")

# Botの名前
bot_name = "Some0ne"
# Botのバージョン
bot_version = "1.0"

# スプラッシュテキストを表示
print("")
print("---------------------------------------")
print(f" {bot_name} Bot - Version {bot_version}")
print(f" using Pycord {discord.__version__}")
print(f" Developed by Milkeyyy")
print("---------------------------------------")
print("")

# 変数宣言
token = ""

# トークンを読み込む
loadToken()

# インテント
intents = discord.Intents.all()
# くらいあんと
client = discord.Bot(intents = intents)

# ゲーム一覧
game_title_list = ["Rainbow Six Siege", "Apex Legends", "Splatoon 3"]
default_gamelist_item = {"role_id": 0}

guilddata = {}

default_userdata_item =  {"Atmark": False, "Game": "", "NumberOfPeople": 0, "Member": [], "MessageId": 0, "RecID": 0}
userdata = {}

invitedata = {}

def createGameList():
	global game_title_list
	global default_gamelist_item
	global gamelist
	global default_guilddata_item
	global guilddata

	gamelist = {}

	for game in game_title_list:
		gamelist[game] = default_gamelist_item

	default_guilddata_item = {"recruitment_channel_id": 0, "gamelist": gamelist}

# ゲーム一覧を作成
createGameList()

# ユーザーデータを作成
def createUserData():
	global userdata

	for guild in client.guilds:
		userdata[guild.id] = {}
		for member in guild.members:
			userdata[guild.id][member.id] = default_userdata_item

# ギルドデータの保存
def saveGuildData():
	# グローバル変数宣言
	global guilddata

	# 書き込み用にファイルを開く
	file = open("guild.json", "w", encoding="utf-8")
	# 辞書をファイルへ保存
	file.write(json.dumps(guilddata, indent = 2, sort_keys=True))
	file.close()
	loadGuildData()

# ギルドデータの読み込み
def loadGuildData():
	# グローバル変数宣言
	global guilddata

	try: # ファイルが存在しない場合
		# ファイルを作成して初期データを書き込む
		file = open("guild.json", "x", encoding="utf-8")
		file.write(json.dumps(guilddata, indent = 2, sort_keys=True))
		file.close()
		# ファイルから読み込む
		file = open("guild.json", "r", encoding="utf-8")
		guilddata = json.load(file)
		file.close()

	except FileExistsError: # ファイルが存在する場合
		# ファイルから読み込む
		file = open("guild.json", "r", encoding="utf-8")
		guilddata = json.load(file)
		file.close()

# ギルドデータの確認
def checkGuildData():
	global guilddata
	global gamelist
	global game_title_list
	global default_gamelist_item

	loadGuildData()

	log("ギルドデータの確認 開始")
	for guild in client.guilds:
		log(f"- Guild ID: {guild.id}")
		# すべてのギルドのデータが存在するかチェック、存在しないギルドがあればそのギルドのデータを作成する
		if guilddata.get(str(guild.id)) == None:
			log("-- ギルドデータを作成")
			guilddata[str(guild.id)] = default_guilddata_item
		algamelist = list(guilddata[str(guild.id)]["gamelist"].keys())
		# ゲーム一覧にすべてのゲームが存在するかチェック、存在しないゲームがあれば追加する
		log(f"-- ゲーム一覧を確認")
		for game in game_title_list:
			log(f"--- 確認: {game}")
			if game not in algamelist:
				log("---- 作成")
				guilddata[str(guild.id)]["gamelist"][game] = default_gamelist_item
	#log(f"ギルドデータ: {guilddata}")

	saveGuildData()
	log("ギルドデータの確認 完了\n")

# Bot起動時のイベント
@client.event
async def on_ready():
	print("")
	log(f"{client.user} へログインしました！ (ID: {client.user.id})")

	#プレゼンスを設定
	await client.change_presence(activity=discord.Game(name=f"/help | Version {bot_version}"))

	# ユーザーデータを作成
	createUserData()

	# ギルドデータを確認&読み込み
	checkGuildData()

@client.command(description="このBotの情報を表示します。")
async def about(ctx):
	embed = discord.Embed(color=discord.Colour.from_rgb(234,197,28))
	embed.set_author(name=bot_name,icon_url=client.user.display_avatar.url)
	embed.add_field(name=f"Version",value=f"`{bot_version}`")
	embed.add_field(name=f"Pycord",value=f"`{discord.__version__}`")
	embed.set_footer(text=f"Developed by Milkeyyy")
	await ctx.respond(embed=embed)
	print(f"[{now()}] コマンド実行: about / 実行者: {ctx.user}")

#uicmd = client.create_group("ui", description="UIに関する管理を行うためのコマンドです。")

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

		rmsg = interaction.message
		if type(rmsg) != discord.Message:
			return

		async def updateMemberList():
			try:
				original_embed = rmsg.embeds[0]
			except:
				return

			for field in original_embed.fields:
				if field.name.startswith(":busts_in_silhouette: 参加者") is True:
					field.name = f":busts_in_silhouette: 参加者 ({len(invitedata[id]['member'])}/{invitedata[id]['nop'] + 1})"
					field.value = convertToUserBulletPointsFromIDList(invitedata[id]["member"])
			await rmsg.edit(rmsg.content, embed=original_embed, view=InviteView(timeout=invitedata[id]["timeout"]))

		async def sendJoinMessage():
			# 埋め込みメッセージを作成して返信
			embed = discord.Embed(color=discord.Colour.from_rgb(131, 177, 88))
			embed.set_author(name=f"{interaction.user} さんが参加しました", icon_url=interaction.user.display_avatar.url)
			embed.set_footer(text=f"ID: {id}")
			await interaction.response.send_message(embed=embed)

		# 募集IDを取得
		try:
			id = interaction.message.embeds[0].footer.text.lstrip("ID: ")
		except:
			self.clear_items()
			return
		# 募集者のIDを取得
		author_id = invitedata[id]["author_id"]

		# ボタンを押したのが募集者本人の場合
		if author_id == interaction.user.id:
			embed = discord.Embed(color=discord.Colour.from_rgb(205, 61, 66), description=":no_entry_sign: 自分で自分の募集に参加することはできません...:cry:")
			msg = await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
		# それ以外の場合
		else:
			# 既に募集に参加している場合
			if interaction.user.id in invitedata[id]["member"]:
				embed = discord.Embed(color=discord.Colour.from_rgb(205, 61, 66), description=":no_entry_sign: あなたは既にこの募集に参加しています！")
				msg = await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5)
			# 募集に参加していない場合
			else:
				if len(invitedata[id]["member"]) + 1 >= invitedata[id]['nop'] + 1:
					# 募集データにユーザーIDを追加
					invitedata[id]["member"].append(interaction.user.id)
					await updateMemberList()
					await sendJoinMessage()
					await endInvite(1, rmsg.guild.id, rmsg.author.id, rmsg.id)
					return
				else:
					# 募集データにユーザーIDを追加
					invitedata[id]["member"].append(interaction.user.id)
					await updateMemberList()
					await sendJoinMessage()

	# 時間制限が来た時
	async def on_timeout(self):
		rmsg = self.message
		if type(rmsg) != discord.Message:
			return

		try:
			#log(f"{dir(rmsg)}")
			#return
			# メッセージIDからメッセージを取得
			msg = client.get_message(rmsg.id)
			# メッセージから埋め込みを取得
			msgembed = msg.embeds[0]
			# メッセージの埋め込みから募集IDを取得
			id = msgembed.footer.text.lstrip("ID: ")
			# 募集を終了
			await endInvite(1, rmsg.guild.id, rmsg.author.id, rmsg.id)
		except:
			self.clear_items()
			#log("")

@client.command(description = "メンバーの募集を開始します。")
async def recruitment(
	ctx,
	game: Option(str, name = "ゲーム", description = "募集するゲームタイトル", choices = dict.keys(gamelist)),
	nop: Option(int, name = "募集人数", description = "募集する人数 (自分を除く)", autocomplete = discord.utils.basic_autocomplete(list(range(1,31)))),
	timeout: Option(float, required = False, min_value = 5, max_value = 600, default = 60, name = "制限時間", description = "募集を締め切るまでの時間(秒)を指定します。 (指定しない場合は60秒になります。)", autocomplete = discord.utils.basic_autocomplete(list(range(5,601))))
):
	global userdata
	global guilddata
	global invitedata

	ud = userdata[ctx.guild_id][ctx.author.id]
	if ud["Atmark"] == True:
		embed = discord.Embed(color=discord.Colour.from_rgb(205, 61, 66))
		embed.add_field(name=f":no_entry_sign: 既に募集が開始されています！", value=f"再度募集を行うには、一度募集をキャンセルしてください！")
		embed.set_author(name=bot_name, icon_url=client.user.display_avatar.url)
		await ctx.respond(embed=embed, ephemeral=True)
	else:
		ud["Atmark"] = True
		ud["Game"] = game
		# メンションするロールのIDを取得
		rid = guilddata[f"{ctx.guild_id}"]["gamelist"][game]["role_id"]
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
		embed.add_field(name=f"🎮 ゲーム", value=f"{game}")
		embed.add_field(name="**@**", value=f"**`{nop}`**")
		embed.add_field(name=f":busts_in_silhouette: 参加者 (1/{nop + 1})", value=f"・{ctx.author.mention}")
		embed.set_footer(text=f"ID: {id}")
		embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)
		# 募集メッセージを送信 (募集用テキストチャンネルが指定されていない場合は、コマンドが実行されたチャンネルへ送信する)
		if guilddata[f"{ctx.guild_id}"]["recruitment_channel_id"] == 0:
			rch = client.get_channel(ctx.channel_id)
		else:
			rch = client.get_channel(guilddata[f"{ctx.guild_id}"]["recruitment_channel_id"])
		rmsg = await rch.send(f"{role}",embed=embed, view=InviteView(timeout=timeout, disable_on_timeout=True))

		# 募集開始通知用埋め込みメッセージを作成
		notification_embed = discord.Embed(color=discord.Colour.from_rgb(112, 171, 235), title="メンバーの募集を開始しました。", description=f"[クリックで募集メッセージへ]({rmsg.jump_url})")
		notification_embed.add_field(name=f"🎮 ゲーム", value=f"{game}")
		notification_embed.add_field(name="**@**", value=f"**`{nop}`**")
		notification_embed.set_footer(text=f"ID: {id}")
		# 募集開始通知を送信 (返信)
		await ctx.respond(embed=notification_embed, ephemeral=True)
		# メッセージのIDを取得
		msgid = rmsg.id
		# 募集データを作成
		startInvite(ctx.guild_id, ctx.author.id, msgid, game, nop, id, timeout)
		# 参加者一覧に募集者自身を追加する
		invitedata[id]["member"].append(ctx.author.id)

@client.command(description = "メンバーの募集をキャンセルします。")
async def cancelrecruitment(ctx):
	global userdata
	global invitedata

	ud = userdata[ctx.guild_id][ctx.author.id]
	udg = ud["Game"]

	if ud["Atmark"] == True:
		# 募集データを取得
		invd = invitedata[ud["RecID"]]
		# メッセージを取得
		msg = client.get_message(invd["message_id"])
		# メッセージの埋め込みを取得
		msgembed = msg.embeds[0]
		# 募集IDを取得
		id = msgembed.footer.text.lstrip("ID: ")

		# 募集を終了
		await endInvite(2, ctx.guild_id, ctx.author.id, invd["message_id"])
		await ctx.respond(f"募集がキャンセルされました。\n・ID: {id}\n・ゲーム: {udg}", ephemeral=True)
	else:
		await ctx.respond("募集が開始されていません！", ephemeral=True)

def startInvite(guild, author, message, game, nop, id, timeout):
	global userdata
	global invitedata

	ud = userdata[guild][author]
	# ユーザーデータの募集状態を有効に変える
	ud["Atmark"] = True
	# ユーザーデータの募集ゲームタイトルを変える
	ud["Game"] = game
	# ユーザーデータの募集IDを変える
	ud["RecID"] = id
	# 募集状態データを作成
	invitedata[id] = {"author_id": author, "message_id": message, "game": game, "nop": nop, "timeout": timeout, "member": []}
	invd = invitedata[id]
	log(f"募集開始 - ユーザー: {client.get_user(author)}")
	log(f"- 募集情報 - Author ID: {invd['author_id']} | Message ID: {invd['message_id']} | Game Title: {invd['game']} | Number on People: {invd['nop']} | Timeout(sec): {invd['timeout']} | Member List: {invd['member']}")

async def endInvite(endtype, guild, author, message_id):
	global userdata
	global invitedata

	ud = userdata[guild][author]

	# メッセージIDからメッセージを取得
	msg = client.get_message(message_id)
	# メッセージから埋め込みを取得
	msgembed = msg.embeds[0]
	# メッセージの埋め込みから募集IDを取得
	id = msgembed.footer.text.lstrip("ID: ")

	if endtype == 1:
		# 埋め込みメッセージを作成して元の募集メッセージを編集する
		msgembed.color = discord.Colour.from_rgb(205, 61, 66)
		msgembed.description = ":no_entry_sign: この募集は締め切られました。"
		await msg.edit(embed=msgembed, view=None)
	elif endtype == 2:
		# 埋め込みメッセージを作成して送信&編集
		msgembed.color = discord.Colour.from_rgb(228, 146, 16)
		msgembed.description = ":orange_square: この募集はキャンセルされました。"
		await msg.edit(embed=msgembed, view=None)

	# ユーザーデータの募集状態を無効に変える
	ud["Atmark"] = False
	# 募集状態データからこの募集を削除する
	del invitedata[id]

#==================== 設定関連コマンド ====================#
@client.command(description = "ゲームタイトルごとのロールを設定します。", permission=discord.Permissions.administrator)
async def setrole(
	ctx,
	game: Option(str, name = "ゲーム", description = "設定するゲームタイトル", choices = dict.keys(gamelist)),
	role: Option(discord.Role, name = "ロール", description = "募集時にメンションするロール")
):
	global guilddata

	guilddata[str(ctx.guild_id)]["gamelist"][game]["role_id"] = role.id
	saveGuildData()
	await ctx.respond(f"`{game}` の対象ロールを {role} に設定しました。")

@client.command(description = "メンバー募集メッセージを送信するテキストチャンネルを設定します。", permission=discord.Permissions.administrator)
async def setrecruitmentchannel(
	ctx,
	ch: Option(discord.TextChannel, name = "テキストチャンネル", description = "メンバー募集のメッセージを送信するテキストチャンネル")
):
	global guilddata

	# ギルドデータに指定されたテキストチャンネルのIDを設定
	guilddata[str(ctx.guild_id)]["recruitment_channel_id"] = ch.id
	saveGuildData()

	await ctx.respond(f"メンバー募集メッセージの送信チャンネルを <#{ch.id}> に設定しました。")

@client.command(description = "現在設定されているメンバー募集メッセージを送信するテキストチャンネルを削除します。削除した場合、メンバー募集メッセージはコマンドを実行したチャンネルへ送信されます。", permission=discord.Permissions.administrator)
async def deleterecruitmentchannel(ctx):
	global guilddata

	# ギルドデータに指定されているテキストチャンネルIDを0に設定
	guilddata[str(ctx.guild_id)]["recruitment_channel_id"] = 0
	saveGuildData()

	await ctx.respond(f"設定されていたメンバー募集メッセージの送信チャンネルを削除しました。")
#==================== 設定関連コマンド ====================#

@client.command(description = "ヘルプを表示します。")
async def help(ctx):
	embed = discord.Embed(color=discord.Colour.blurple(), title="ヘルプ")
	embed.set_author(name=bot_name, icon_url=client.user.display_avatar.url)
	embed.add_field(name=f"コマンド", value=f"＜通常コマンド＞\n・メンバーの募集を開始\n`/recruitment`\n・メンバーの募集をキャンセル\n`/cancelrecruitment`\n\n＜管理用コマンド＞\n・メンバー募集メッセージの送信チャンネルを設定\n`/setrecruitmentchannel`\n・ゲームごとのメンションロールを設定\n`/setrole`")
	embed.set_footer(text=f"{bot_name} Bot - Version {bot_version}\nDeveloped by Milkeyyy#0625")
	await ctx.respond(embed=embed, ephemeral=True)

#==================== ぼっとへログイン ====================#
client.run(token)
