# main.py

import os
import threading
from flask import Flask
import discord
from discord.ext import commands
# 필요한 UI 모듈/뷰를 import 해줍니다.
from adventure_ui import AdventureHomeView

# 1. Render 포트 바인딩용 Flask 앱 설정
app = Flask(__name__)

@app.route('/')
def home():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

# 디스코드 모험 명령어
@bot.command(name="모험")
async def adventure(ctx):
    # 유저 데이터 기본값 설정 (가상 데이터)
    user_id = ctx.author.id
    cat_data = {
        "name": ctx.author.display_name,
        "level": 1,
        "hp": 50,
        "max_hp": 50,
        "atk": 10,
        "exp": 0,
        "gold": 0,
        "stage": 1
    }
    
    view = AdventureHomeView(author=ctx.author, user_id=user_id, cat_data=cat_data)
    
    embed = discord.Embed(
        title=f"🐾 {cat_data['name']}의 정글 모험 준비",
        description="울창한 정글 속으로 모험을 떠날 준비가 되셨나요?",
        color=discord.Color.green()
    )
    embed.set_image(url="https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000")
    
    await ctx.send(embed=embed, view=view)

if __name__ == "__main__":
    # Flask를 별도 스레드에서 실행하여 Render 응답 지연 방지
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 디스코드 봇 토큰 실행
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if BOT_TOKEN:
        bot.run(BOT_TOKEN)
    else:
        print("❌ [오류] BOT_TOKEN 환경 변수가 설정되어 있지 않습니다!")