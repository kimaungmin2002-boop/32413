import os
import json
import random
import io
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread

# 1. 분리했던 adventure_ui 모듈에서 모험 로비 불러오기
from adventure_ui import AdventureHomeView

# --- 0. 24시간 웹 서버 유지용 (Keep-Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 1. 백업 채널 설정 및 데이터 관리 ---
BACKUP_CHANNEL_ID = 1529132777461780664
cats_data = {}

async def save_data():
    """데이터가 변경될 때마다 비밀 채널에 백업을 보냅니다."""
    try:
        channel = bot.get_channel(BACKUP_CHANNEL_ID) or await bot.fetch_channel(BACKUP_CHANNEL_ID)
        if channel:
            json_str = json.dumps(cats_data, ensure_ascii=False, indent=2)
            
            # 2,000자 제한 처리: 내용이 너무 길면 파일(Attachment) 형태로 백업
            if len(json_str) > 1900:
                file_data = io.BytesIO(json_str.encode('utf-8'))
                discord_file = discord.File(file_data, filename="backup.json")
                await channel.send("📦 **[자동 백업 파일]**", file=discord_file)
            else:
                await channel.send(f"```json\n{json_str}\n```")
    except Exception as e:
        print(f"❌ 데이터 저장/백업 실패: {e}")

async def load_data():
    """봇이 켜질 때 비밀 채널의 마지막 백업에서 데이터를 복구합니다."""
    global cats_data
    try:
        channel = bot.get_channel(BACKUP_CHANNEL_ID) or await bot.fetch_channel(BACKUP_CHANNEL_ID)
        if channel:
            async for message in channel.history(limit=20):
                if message.author == bot.user:
                    # 1. 파일 첨부형 백업인 경우
                    if message.attachments:
                        for attachment in message.attachments:
                            if attachment.filename == "backup.json":
                                file_bytes = await attachment.read()
                                cats_data = json.loads(file_bytes.decode('utf-8'))
                                print("✅ 비밀 채널(파일)에서 고양이 데이터를 복구했습니다!")
                                return

                    # 2. 텍스트 코드블럭 백업인 경우
                    elif message.content.startswith("```json"):
                        raw_json = message.content.replace("```json", "").replace("```", "").strip()
                        cats_data = json.loads(raw_json)
                        print("✅ 비밀 채널(텍스트)에서 고양이 데이터를 복구했습니다!")
                        return
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        
    print("⚠️ 백업 데이터가 없거나 로드에 실패하여 빈 데이터로 시작합니다.")

# --- 2. 봇 인텐트 설정 ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def create_cat_embed(user_name, cat_data):
    embed = discord.Embed(
        title=f"🐾 {user_name}님의 고양이 [{cat_data['name']}]",
        color=discord.Color.gold()
    )
    embed.add_field(name="🍖 포만감", value=f"{cat_data['fullness']} / 100", inline=True)
    embed.add_field(name="❤️ 애정도", value=f"{cat_data['affection']} / 100", inline=True)
    embed.set_footer(text="버튼을 눌러 고양이와 상호작용해 보세요!")
    return embed

# --- UI 상호작용 버튼 ---
class CatInteractiveView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = str(user_id)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ 다른 사람의 고양이는 돌볼 수 없습니다!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="🐟 밥주기", style=discord.ButtonStyle.success)
    async def feed(self, interaction: discord.Interaction, button: discord.ui.Button):
        cat = cats_data.get(self.user_id)
        if not cat:
            return

        if cat["fullness"] >= 100:
            cat["affection"] = max(0, cat["affection"] - 10)
            await save_data()
            embed = create_cat_embed(interaction.user.display_name, cat)
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(
                f"😾 **{cat['name']}**이가 배가 너무 불러서 밥을 거부하고 냥펀치를 날렸습니다! (❤️ 애정도 -10)", 
                ephemeral=True
            )
            return

        cat["fullness"] = min(100, cat["fullness"] + 20)
        cat["affection"] = min(100, cat["affection"] + 5)
        await save_data()

        embed = create_cat_embed(interaction.user.display_name, cat)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🧶 놀아주기", style=discord.ButtonStyle.primary)
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        cat = cats_data.get(self.user_id)
        if not cat:
            return

        if cat["fullness"] < 20:
            cat["affection"] = max(0, cat["affection"] - 10)
            await save_data()
            embed = create_cat_embed(interaction.user.display_name, cat)
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(
                f"😾 **{cat['name']}**이가 배고파서 예민한데 자꾸 귀찮게 해서 화났습니다! (❤️ 애정도 -10)", 
                ephemeral=True
            )
            return

        if random.random() < 0.1:
            embed = create_cat_embed(interaction.user.display_name, cat)
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(
                f"😴 **{cat['name']}**이가 귀찮은지 장난감을 힐끔 쳐다보기만 하고 뒹굴거립니다...", 
                ephemeral=True
            )
            return

        cat["fullness"] = max(0, cat["fullness"] - 10)
        cat["affection"] = min(100, cat["affection"] + 20)
        await save_data()

        embed = create_cat_embed(interaction.user.display_name, cat)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="✋ 만지기", style=discord.ButtonStyle.secondary)
    async def touch(self, interaction: discord.Interaction, button: discord.ui.Button):
        cat = cats_data.get(self.user_id)
        if not cat:
            return

        if random.random() < 0.7:
            cat["affection"] = max(0, cat["affection"] - 10)
            await save_data()
            embed = create_cat_embed(interaction.user.display_name, cat)
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(
                f"😾 **{cat['name']}**이가 손길을 거부하고 냥펀치를 날렸습니다! (❤️ 애정도 -10)", 
                ephemeral=True
            )
        else:
            cat["affection"] = min(100, cat["affection"] + 10)
            await save_data()
            embed = create_cat_embed(interaction.user.display_name, cat)
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(
                f"😻 **{cat['name']}**이가 기분이 좋은지 손길을 받아들이고 골골송을 부릅니다! (❤️ 애정도 +10)", 
                ephemeral=True
            )

class ConfirmAbandonView(discord.ui.View):
    def __init__(self, user_id, cat_name):
        super().__init__(timeout=30)
        self.user_id = str(user_id)
        self.cat_name = cat_name

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ 본인의 고양이만 결정할 수 있습니다!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="🗑️ 정말 버리기", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.user_id in cats_data:
            del cats_data[self.user_id]
            await save_data()
            
            for child in self.children:
                child.disabled = True
                
            await interaction.response.edit_message(
                content=f"😿 고양이 **[{self.cat_name}]**을(를) 버렸습니다...",
                embed=None,
                view=self
            )

    @discord.ui.button(label="❌ 취소", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
            
        await interaction.response.edit_message(
            content=f"😊 취소되었습니다. **[{self.cat_name}]**이와(가) 계속 함께합니다! 🐾",
            embed=None,
            view=self
        )

# --- 3. 봇 로그인 및 서버 동기화 (중복 방지 깔끔한 수정) ---
@bot.event
async def on_ready():
    await load_data()  # 봇 켜지자마자 백업 데이터 불러오기
    try:
        synced = await bot.tree.sync()
        print(f"✅ 글로벌 명령어 동기화 완료: {len(synced)}개 명령어 등록됨")
    except Exception as e:
        print(f"❌ 슬래시 명령어 동기화 실패: {e}")
    print(f"✅ 로그인 완료: {bot.user.name}")

# --- 4. 슬래시 명령어 ---
@bot.tree.command(name="입양", description="새로운 고양이를 입양합니다.")
@app_commands.describe(이름="입양할 고양이의 이름을 입력하세요.")
async def adopt(interaction: discord.Interaction, 이름: str):
    user_id = str(interaction.user.id)

    if user_id in cats_data:
        await interaction.response.send_message(
            f"⚠️ 이미 입양한 고양이 **[{cats_data[user_id]['name']}]**이(가) 있습니다!",
            ephemeral=True
        )
        return

    cats_data[user_id] = {
        "name": 이름,
        "fullness": 100,
        "affection": 50,
        "level": 1,
        "exp": 0,
        "max_exp": 100,
        "hp": 50,
        "max_hp": 50,
        "atk": 10,
        "def": 2,
        "gold": 100,
        "stage": 1,
        "inventory": [],
        "equipped": {"weapon": None, "armor": None}
    }
    await save_data()

    await interaction.response.send_message(
        f"🎉 **{interaction.user.display_name}**님이 고양이 **[{이름}]**을(를) 성공적으로 입양했습니다!"
    )

@bot.tree.command(name="고양이", description="내 고양이의 상태를 확인하고 돌봅니다.")
async def show_cat(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if user_id not in cats_data:
        await interaction.response.send_message(
            "❌ 아직 입양한 고양이가 없습니다. `/입양 [이름]` 명령어로 먼저 입양해 주세요!",
            ephemeral=True
        )
        return

    cat_data = cats_data[user_id]
    embed = create_cat_embed(interaction.user.display_name, cat_data)
    view = CatInteractiveView(user_id)

    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="버리기", description="입양한 고양이를 버립니다.")
async def abandon(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if user_id not in cats_data:
        await interaction.response.send_message(
            "❌ 아직 버릴 고양이가 없습니다!",
            ephemeral=True
        )
        return

    cat_name = cats_data[user_id]["name"]
    view = ConfirmAbandonView(user_id, cat_name)

    await interaction.response.send_message(
        f"⚠️ 정말로 고양이 **[{cat_name}]**을(를) 버리시겠습니까?\n이 작업은 되돌릴 수 없습니다!",
        view=view,
        ephemeral=True
    )

# ⚔️ 모험 로비 UI로 바로 연결되는 /모험 명령어
@bot.tree.command(name="모험", description="고양이를 데리고 모험 로비로 입장합니다.")
async def adventure(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if user_id not in cats_data:
        await interaction.response.send_message(
            "❌ 먼저 고양이를 입양해야 합니다! `/입양 [이름]` 명령어를 사용하세요.",
            ephemeral=True
        )
        return

    cat_data = cats_data[user_id]

    # 구버전 유저 데이터 누락 방지 스탯 보정
    if "hp" not in cat_data: cat_data["hp"] = 50
    if "max_hp" not in cat_data: cat_data["max_hp"] = 50
    if "atk" not in cat_data: cat_data["atk"] = 10
    if "level" not in cat_data: cat_data["level"] = 1
    if "exp" not in cat_data: cat_data["exp"] = 0
    if "gold" not in cat_data: cat_data["gold"] = 100
    if "stage" not in cat_data: cat_data["stage"] = 1

    # adventure_ui.py의 모험 로비 화면 호출
    view = AdventureHomeView(author=interaction.user, user_id=user_id, cat_data=cat_data)
    
    lobby_embed = discord.Embed(
        title=f"🐾 {cat_data['name']}의 모험 로비",
        description="당신의 여정이 기다리고 있습니다...\n\n원하시는 활동을 선택해주세요!",
        color=discord.Color.blurple()
    )
    lobby_embed.set_image(url="[https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000](https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000)")

    await interaction.response.send_message(embed=lobby_embed, view=view, ephemeral=False)

# --- 5. 실행부 ---
if __name__ == "__main__":
    keep_alive()
    
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    if BOT_TOKEN is None:
        print("❌ BOT_TOKEN이 없습니다. Render 환경변수를 확인하세요.")
    else:
        bot.run(BOT_TOKEN)