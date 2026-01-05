import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import database  # 作成したdatabase.pyを読み込み

# .envからトークンを読み込み
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 設定
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class VspoBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)

    async def setup_hook(self):
        # スラッシュコマンドを同期
        await self.tree.sync()

bot = VspoBot()

# 起動時の処理
@bot.event
async def on_ready():
    database.init_db()
    print(f'ログインしました: {bot.user}')
    print('------')

# ---------------------------------------------------------
# 機能1: イベント参加表明 (/attend) & リスト確認 (/check_event)
# ファンも「一般参加」「カメコ参加」として登録して楽しめます
# ---------------------------------------------------------
@bot.tree.command(name="attend", description="イベントへの参加表明をします")
@app_commands.describe(event_name="イベント名 (例: コミケ104)", char_name="キャラ名・目的", costume="衣装・詳細")
async def attend(interaction: discord.Interaction, event_name: str, char_name: str, costume: str):
    database.add_event_entry(event_name, interaction.user.id, char_name, costume)
    await interaction.response.send_message(f"✅ **{event_name}** に `{char_name} ({costume})` で登録しました！", ephemeral=False)

@bot.tree.command(name="check_event", description="イベントの参加者リストを表示します")
async def check_event(interaction: discord.Interaction, event_name: str):
    participants = database.get_event_participants(event_name)
    if not participants:
        await interaction.response.send_message(f"💦 **{event_name}** の参加者はまだいません。", ephemeral=True)
        return

    embed = discord.Embed(title=f"📅 {event_name} 参加予定リスト", color=0x00ff00)
    text = ""
    for p in participants:
        user_id, char, cos = p
        text += f"• <@{user_id}> : **{char}** ({cos})\n"
    
    embed.description = text
    await interaction.response.send_message(embed=embed)

# ---------------------------------------------------------
# 機能2: 資料リファレンス (/ref) & 登録 (/add_ref)
# 公式のイラストやツイートをサッと出して「尊い」を共有するのに便利です
# ---------------------------------------------------------
@bot.tree.command(name="ref", description="衣装や武器の資料URLを呼び出します")
async def ref(interaction: discord.Interaction, char_name: str):
    data = database.search_reference(char_name)
    if data:
        name, url = data
        await interaction.response.send_message(f"📚 **{name}** の資料:\n{url}")
    else:
        await interaction.response.send_message(f"💦 `{char_name}` の資料は見つかりませんでした。", ephemeral=True)

@bot.tree.command(name="add_ref", description="【管理者用】資料を登録します")
async def add_ref(interaction: discord.Interaction, char_name: str, url: str):
    database.add_reference(char_name, url)
    await interaction.response.send_message(f"✅ 資料を登録しました: {char_name}", ephemeral=True)

# ---------------------------------------------------------
# 機能3: 写真アーカイブ (画像投稿を監視)
# 「写真館」チャンネルに投稿された画像を自動保存します
# ---------------------------------------------------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 「写真館」という名前が含まれるチャンネルのみ反応
    if "写真館" in message.channel.name and message.attachments:
        img_url = message.attachments[0].url
        database.save_photo(message.author.id, img_url)
        await message.add_reaction('📸') # 保存完了合図
        # ファンが「見たよ！」という意味でリアクションしやすくしています

    # コマンド処理も継続
    await bot.process_commands(message)
    # --- (ここまでは既存コード) ---

# ---------------------------------------------------------
# 新機能: 地域別イベントカレンダー
# ---------------------------------------------------------

# 地域の選択肢を定義
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
    # 日付フォーマットチェック（簡易）
    import re
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
        # 曜日を計算しておしゃれにする
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        weekday = ["月", "火", "水", "木", "金", "土", "日"][dt.weekday()]
        
        description_text += f"**{date} ({weekday})**\n🏆 **{name}**\n📍 {place}\n\n"

    embed.description = description_text
    await interaction.response.send_message(embed=embed)

# --- (Bot起動コードの手前に入れる) ---

# Bot起動
bot.run(TOKEN)
