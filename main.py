import os
import threading
from flask import Flask
import discord
from discord.ext import commands
from adventure_ui import AdventureHomeView

# 1. Render 웹 서버용 Flask 설정
app = Flask(__name__)

@app.route('/')
def home():
    return "OK", 200

def run_flask():
    # Render가 지정해주는 포트 사용 (없으면 10000)
    port = int(os.environ.get("PORT", 10000))
    # Werkzeug 로그를 줄이고 백그라운드에서 실행
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# 2. 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)}개의 슬래시 명령어 동기화 완료!")
    except Exception as e:
        print(f"❌ 명령어 동기화 실패: {e}")
    print("====== 🤖 디스코드 봇이 정상적으로 켜졌습니다! ======")

async def start_adventure(ctx_or_interaction, user):
    user_id = user.id
    cat_data = {
        "name": user.display_name,
        "level": 1,
        "hp": 50,
        "max_hp": 50,
        "atk": 10,
        "exp": 0,
        "gold": 0,
        "stage": 1
    }
    
    view = AdventureHomeView(author=user, user_id=user_id, cat_data=cat_data)
    
    embed = discord.Embed(
        title=f"🐾 {cat_data['name']}의 정글 모험 준비",
        description="울창한 정글 속으로 모험을 떠날 준비가 되셨나요?",
        color=discord.Color.green()
    )
    embed.set_image(url="https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000")
    
    if isinstance(ctx_or_interaction, discord.Interaction):
        await ctx_or_interaction.response.send_message(embed=embed, view=view)
    else:
        await ctx_or_interaction.send(embed=embed, view=view)

@bot.command(name="모험")
async def adventure_cmd(ctx):
    await start_adventure(ctx, ctx.author)

@bot.tree.command(name="모험", description="정글 고양이 모험을 시작합니다!")
async def adventure_slash(interaction: discord.Interaction):
    await start_adventure(interaction, interaction.user)

if __name__ == "__main__":
    # 🌟 핵심: Flask를 백그라운드 스레드로 먼저 띄움
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 🌟 메인 스레드에서 디스코드 봇 실행
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if BOT_TOKEN:
        bot.run(BOT_TOKEN)
    else:
        print("❌ [오류] BOT_TOKEN 환경 변수를 찾을 수 없습니다!")