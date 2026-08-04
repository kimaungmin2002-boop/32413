import os
import json
import random
import io
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread

# --- 0. 24?�간 ???�버 ?��???(Keep-Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 1. 백업 채널 ?�정 �??�이??관�?(?�정?�료) ---
# ?�️ ?�래 ?�자�?질문?�님??'비�? 채널 ID' (?�자)�?�?바꿔주세??
BACKUP_CHANNEL_ID = 1529132777461780664
cats_data = {}

async def save_data():
    """?�이?��? 변경될 ?�마??비�? 채널??백업??보냅?�다."""
    try:
        channel = bot.get_channel(BACKUP_CHANNEL_ID) or await bot.fetch_channel(BACKUP_CHANNEL_ID)
        if channel:
            json_str = json.dumps(cats_data, ensure_ascii=False, indent=2)
            
            # 2,000???�한 처리: ?�용???�무 길면 ?�일(Attachment) ?�태�?백업
            if len(json_str) > 1900:
                file_data = io.BytesIO(json_str.encode('utf-8'))
                discord_file = discord.File(file_data, filename="backup.json")
                await channel.send("?�� **[?�동 백업 ?�일]**", file=discord_file)
            else:
                await channel.send(f"```json\n{json_str}\n```")
    except Exception as e:
        print(f"???�이???�??백업 ?�패: {e}")

async def load_data():
    """봇이 켜질 ??비�? 채널??마�?�?백업?�서 ?�이?��? 복구?�니??"""
    global cats_data
    try:
        channel = bot.get_channel(BACKUP_CHANNEL_ID) or await bot.fetch_channel(BACKUP_CHANNEL_ID)
        if channel:
            async for message in channel.history(limit=20):
                if message.author == bot.user:
                    # 1. ?�일 첨�???백업??경우
                    if message.attachments:
                        for attachment in message.attachments:
                            if attachment.filename == "backup.json":
                                file_bytes = await attachment.read()
                                cats_data = json.loads(file_bytes.decode('utf-8'))
                                print("??비�? 채널(?�일)?�서 고양???�이?��? 복구?�습?�다!")
                                return

                    # 2. ?�스??코드블럭 백업??경우
                    elif message.content.startswith("```json"):
                        raw_json = message.content.replace("```json", "").replace("```", "").strip()
                        cats_data = json.loads(raw_json)
                        print("??비�? 채널(?�스???�서 고양???�이?��? 복구?�습?�다!")
                        return
    except Exception as e:
        print(f"???�이??로드 ?�패: {e}")
        
    print("?�️ 백업 ?�이?��? ?�거??로드???�패?�여 �??�이?�로 ?�작?�니??")

# --- 2. �??�텐???�정 ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def create_cat_embed(user_name, cat_data):
    embed = discord.Embed(
        title=f"?�� {user_name}?�의 고양??[{cat_data['name']}]",
        color=discord.Color.gold()
    )
    embed.add_field(name="?�� ?�만�?, value=f"{cat_data['fullness']} / 100", inline=True)
    embed.add_field(name="?�️ ?�정??, value=f"{cat_data['affection']} / 100", inline=True)
    embed.set_footer(text="버튼???�러 고양?��? ?�호?�용??보세??")
    return embed

# --- UI ?�호?�용 버튼 ---
class CatInteractiveView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = str(user_id)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("???�른 ?�람??고양?�는 ?�볼 ???�습?�다!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="?�� 밥주�?, style=discord.ButtonStyle.success)
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
                f"?�� **{cat['name']}**?��? 배�? ?�무 불러??밥을 거�??�고 ?��?치�? ?�렸?�니?? (?�️ ?�정??-10)", 
                ephemeral=True
            )
            return

        cat["fullness"] = min(100, cat["fullness"] + 20)
        cat["affection"] = min(100, cat["affection"] + 5)
        await save_data()

        embed = create_cat_embed(interaction.user.display_name, cat)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="?�� ?�?�주�?, style=discord.ButtonStyle.primary)
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
                f"?�� **{cat['name']}**?��? 배고?�서 ?��??�데 ?�꾸 귀�?�� ?�서 ?�났?�니?? (?�️ ?�정??-10)", 
                ephemeral=True
            )
            return

        if random.random() < 0.1:
            embed = create_cat_embed(interaction.user.display_name, cat)
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(
                f"?�� **{cat['name']}**?��? 귀�??지 ?�난감을 ?�끔 쳐다보기�??�고 ?�굴거립?�다... (?�치 변???�음)", 
                ephemeral=True
            )
            return

        cat["fullness"] = max(0, cat["fullness"] - 10)
        cat["affection"] = min(100, cat["affection"] + 20)
        await save_data()

        embed = create_cat_embed(interaction.user.display_name, cat)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="??만�?�?, style=discord.ButtonStyle.secondary)
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
                f"?�� **{cat['name']}**?��? ?�길??거�??�고 ?��?치�? ?�렸?�니?? (?�️ ?�정??-10)", 
                ephemeral=True
            )
        else:
            cat["affection"] = min(100, cat["affection"] + 10)
            await save_data()
            embed = create_cat_embed(interaction.user.display_name, cat)
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(
                f"?�� **{cat['name']}**?��? 기분??좋�?지 ?�길??받아?�이�?골골?�을 붑니?? (?�️ ?�정??+10)", 
                ephemeral=True
            )

class ConfirmAbandonView(discord.ui.View):
    def __init__(self, user_id, cat_name):
        super().__init__(timeout=30)
        self.user_id = str(user_id)
        self.cat_name = cat_name

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("??본인??고양?�만 결정?????�습?�다!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="?���??�말 버리�?, style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.user_id in cats_data:
            del cats_data[self.user_id]
            await save_data()
            
            for child in self.children:
                child.disabled = True
                
            await interaction.response.edit_message(
                content=f"?�� 고양??**[{self.cat_name}]**??�? 버렸?�니??..",
                embed=None,
                view=self
            )

    @discord.ui.button(label="??취소", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
            
        await interaction.response.edit_message(
            content=f"?�� 취소?�었?�니?? **[{self.cat_name}]**?��?(가) 계속 ?�께?�니?? ?��",
            embed=None,
            view=self
        )

# --- 3. �?로그??�??�버 ?�동 ?�기??---
@bot.event
async def on_ready():
    await load_data()  # �?켜�??�마??백업 ?�이??불러?�기
    try:
        for guild in bot.guilds:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"??[{guild.name}] ?�버??즉시 ?�기???�료: {len(synced)}�?명령???�록??)
    except Exception as e:
        print(f"???�래??명령???�기???�패: {e}")
    print(f"??로그???�료: {bot.user.name}")

# --- 4. ?�래??명령??---
