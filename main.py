import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import database
import datetime  # カレンダー機能で必須
import re        # 日付チェックで必須

# .envファイルを読み込む
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Botの設定（インテント）
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 起動時の処理
@bot.event
async def on_ready():
    print(f'ログインしました: {bot.user}')
    
    # データベースの初期化
    database.init_db()
    
    # コマンド同期（重要！）
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} 個のコマンドを同期しました")
    except Exception as e:
        print(f"同期エラー: {e}")

# ---------------------------------------------------------
# 機能1: イベント参加表明 (/attend, /check_event)
# ---------------------------------------------------------
@bot.tree.command(name="attend", description="イベントへの参加表明をします")
@app_commands.describe(event_name="イベント名", char_name="キャラ名", costume="衣装")
async def attend(interaction: discord.Interaction, event_name: str, char_name: str, costume: str):
    database.add_event_entry(event_name, interaction.user.id, char_name, costume)
    await interaction.response.send_message(f"✅ **{event_name}** に参加登録しました！\nキャラ: {char_name} ({costume})")

@bot.tree.command(name="check_event", description="イベントの参加者リストを表示します")
@app_commands.describe(event_name="イベント名")
async def check_event(interaction: discord.Interaction, event_name: str):
    participants = database.get_event_participants(event_name)
    
    if not participants:
        await interaction.response.send_message(f"💦 **{event_name}** の参加者はまだいません。", ephemeral=True)
        return

    text = f"📋 **{event_name} 参加者リスト**\n\n"
    for p in participants:
        user_id, char, cos = p
        text += f"👤 <@{user_id}> : **{char}** ({cos})\n"
    
    await interaction.response.send_message(text)

# ---------------------------------------------------------
# 機能2: 写真共有 (/upload_photo)
# ---------------------------------------------------------
@bot.tree.command(name="upload_photo", description="コスプレ写真をアップロードして共有します")
@app_commands.describe(image="画像ファイル", char_name="キャラ名(任意)")
async def upload_photo(interaction: discord.Interaction, image: discord.Attachment, char_name: str = "未設定"):
    if not image.content_type.startswith("image/"):
        await interaction.response.send_message("⚠️ 画像ファイルを選択してください。", ephemeral=True)
        return

    database.save_photo(interaction.user.id, image.url, char_name)
    await interaction.response.send_message(f"📸 写真を保存しました！\nキャラ: {char_name}\nURL: {image.url}")

# ---------------------------------------------------------
# 機能3: 三面図・資料管理 (/add_ref, /ref)
# ---------------------------------------------------------
@bot.tree.command(name="add_ref", description="三面図や資料URLを登録します（衣装名も指定可能）")
@app_commands.describe(char_name="キャラ名", costume="衣装名 (例: 通常, アイドル, 私服)", url="画像のURL")
async def add_ref(interaction: discord.Interaction, char_name: str, costume: str, url: str):
    if not url.startswith("http"):
        await interaction.response.send_message("💦 URLは `http` から始まる正しいリンクを入力してください。", ephemeral=True)
        return

    database.add_reference(char_name, costume, url)
    await interaction.response.send_message(f"✅ 資料を登録しました！\n**{char_name} ({costume})**\n🔗 {url}")

@bot.tree.command(name="ref", description="登録された三面図や資料を探します")
@app_commands.describe(keyword="キャラ名の一部")
async def ref(interaction: discord.Interaction, keyword: str):
    results = database.search_reference(keyword)
    
    if not results:
        await interaction.response.send_message(f"😢 「{keyword}」に関する資料は見つかりませんでした。\n`/add_ref` で登録してください！", ephemeral=True)
        return

    embed = discord.Embed(title=f"📂 「{keyword}」の検索結果", color=0x00ff00)
    for item in results:
        char_name, costume_name, url = item
        embed.add_field(name=f"👤 {char_name} - {costume_name}", value=f"[画像を見る]({url})", inline=False)

    await interaction.response.send_message(embed=embed)

# ---------------------------------------------------------
# 機能4: 地域別イベントカレンダー (/add_event, /calendar)
# ---------------------------------------------------------
REGION_CHOICES = [
    app_commands.Choice(name="関東", value="関東"),
    app_commands.Choice(name="関西", value="関西"),
    app_commands.Choice(name="北海道・東北", value="北海道・東北"),
    app_commands.Choice(name="中部", value="中部"),
    app_commands.Choice(name="中国・四国", value="中国・四国"),
    app_commands.Choice(name="九州・沖縄", value="九州・沖縄"),
]

@bot.tree.command(name="add_event", description="カレンダーにイベントを登録します")
@app_commands.describe(name="イベント名", date="開催日 (例: 2024-08-12)", region="地域", place="場所・詳細")
@app_commands.choices(region=REGION_CHOICES)
async def add_event(interaction: discord.Interaction, name: str, date: str, region: str, place: str):
    # 日付チェック
    if not re.match(r"\d{4}-\d{2}-\d{2}", date):
        await interaction.response.send_message("💦 日付は `2024-08-12` のようにハイフン区切りで入力してください。", ephemeral=True)
        return

    database.add_schedule_item(name, date, region, place)
    await interaction.response.send_message(f"🗓️ **{region}** のカレンダーに登録しました！\n**{date}** : {name} (@{place})")

@bot.tree.command(name="calendar", description="地域別のイベントカレンダーを表示します")
@app_commands.choices(region=REGION_CHOICES)
async def calendar(interaction: discord.Interaction, region: str):
    events = database.get_schedule_by_region(region)
    
    if not events:
        await interaction.response.send_message(f"🍂 現在登録されている **{region}** の予定はありません。", ephemeral=True)
        return

    embed = discord.Embed(title=f"🗓️ {region} のコスプレイベント情報", color=0xff9900)
    description_text = ""
    
    for event in events:
        date, name, place = event
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        weekday = ["月", "火", "水", "木", "金", "土", "日"][dt.weekday()]
        description_text += f"**{date} ({weekday})**\n🏆 **{name}**\n📍 {place}\n\n"

    embed.description = description_text
    await interaction.response.send_message(embed=embed)

# Botを実行
bot.run(TOKEN)
