# adventure_ui.py

import discord
import random
import asyncio
from game_data import MONSTERS

class AdventureHomeView(discord.ui.View):
    def __init__(self, author, user_id, cat_data):
        super().__init__(timeout=180)
        self.author = author
        self.user_id = user_id
        self.cat_data = cat_data

    def verify_user(self, interaction_user_id):
        try:
            if self.user_id and int(interaction_user_id) == int(self.user_id):
                return True
        except:
            pass
        try:
            if self.author and hasattr(self.author, 'id') and int(interaction_user_id) == int(self.author.id):
                return True
        except:
            pass
        return False

    @discord.ui.button(label="🧭 모험 떠나기", style=discord.ButtonStyle.success)
    async def start_adventure(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.verify_user(interaction.user.id):
            await interaction.response.send_message("❌ 본인의 고양이만 조작할 수 있습니다!", ephemeral=True)
            return

        next_view = NextStageView(author=self.author, user_id=self.user_id, cat_data=self.cat_data)
        await next_view.trigger_walk(interaction)

    @discord.ui.button(label="👤 내 정보", style=discord.ButtonStyle.secondary)
    async def show_my_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.verify_user(interaction.user.id):
            await interaction.response.send_message("❌ 본인의 고양이만 조작할 수 있습니다!", ephemeral=True)
            return

        current_level = self.cat_data.get('level', 1)
        req_exp = current_level * 100
        
        info_embed = discord.Embed(
            title=f"🐾 {self.cat_data['name']}의 상태창",
            description="현재 모험을 준비 중인 고양이의 정보입니다.",
            color=discord.Color.blue()
        )
        info_embed.add_field(name="레벨", value=f"Lv.{current_level}", inline=True)
        info_embed.add_field(name="현재 진행 스테이지", value=f"🚩 Stage 1-{self.cat_data.get('stage', 1)}", inline=True)
        info_embed.add_field(name="경험치 (EXP)", value=f"{self.cat_data.get('exp', 0)} / {req_exp}", inline=True)
        info_embed.add_field(name="보유 골드", value=f"💰 {self.cat_data.get('gold', 0)} Gold", inline=True)
        info_embed.add_field(name="체력 (HP)", value=f"❤️ {self.cat_data.get('hp', 50)} / {self.cat_data.get('max_hp', 50)}", inline=True)
        info_embed.add_field(name="공격력", value=f"⚔️ {self.cat_data.get('atk', 10)}", inline=True)
        info_embed.set_thumbnail(url="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000")

        await interaction.response.send_message(embed=info_embed, ephemeral=True)


class AdventureView(discord.ui.View):
    def __init__(self, author, user_id, cat_data, stage=1):
        super().__init__(timeout=180)
        self.author = author
        self.user_id = user_id
        self.cat_data = cat_data
        self.stage = stage
        
        stage_monsters = MONSTERS.get(stage, MONSTERS.get(1))
        self.monster = random.choice(stage_monsters).copy()
        self.monster_max_hp = self.monster["hp"]

    def verify_user(self, interaction_user_id):
        try:
            if self.user_id and int(interaction_user_id) == int(self.user_id):
                return True
        except:
            pass
        try:
            if self.author and hasattr(self.author, 'id') and int(interaction_user_id) == int(self.author.id):
                return True
        except:
            pass
        return False

    def create_battle_embed(self, description=""):
        hp_percent = max(0, self.monster["hp"]) / self.monster_max_hp
        bar_length = 10
        filled = int(hp_percent * bar_length)
        hp_bar = "█" * filled + "░" * (bar_length - filled)

        current_level = self.cat_data.get('level', 1)
        req_exp = current_level * 100

        embed = discord.Embed(
            title=f"⚔️ [Stage 1-{self.stage}] 전투 중!",
            description=description or f"야생의 **{self.monster['name']}**이(가) 나타났다!",
            color=discord.Color.red() if not self.monster.get("is_boss") else discord.Color.purple()
        )
        
        if self.monster.get("boss_quote"):
            embed.add_field(name="💬 보스의 한마디", value=f"*\"{self.monster['boss_quote']}\"*", inline=False)

        embed.add_field(
            name=f"🐱 {self.cat_data['name']} (Lv.{current_level})",
            value=f"❤️ HP: `{self.cat_data['hp']}/{self.cat_data['max_hp']}`\n"
                  f"⚔️ 공격력: `{self.cat_data['atk']}`\n"
                  f"📈 EXP: `{self.cat_data.get('exp', 0)} / {req_exp}`",
            inline=True
        )
        embed.add_field(
            name=f"👾 {self.monster['name']}",
            value=f"❤️ HP: `{self.monster['hp']}/{self.monster_max_hp}`\n`[{hp_bar}]`",
            inline=True
        )
        
        if "image" in self.monster:
            embed.set_image(url=self.monster["image"])
            
        embed.set_footer(text=f"💰 보유 골드: {self.cat_data.get('gold', 0)} Gold")
        return embed

    @discord.ui.button(label="⚔️ 공격하기", style=discord.ButtonStyle.danger)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.verify_user(interaction.user.id):
            await interaction.response.send_message("❌ 다른 사람의 전투입니다!", ephemeral=True)
            return

        desc = ""
        dodge_chance = self.monster.get("dodge_rate", 0.0)
        if random.random() < dodge_chance:
            desc += f"💨 **{self.monster['name']}**이(가) 신통력으로 잽싸게 **공격을 회피(MISS)**했습니다!\n"
        else:
            cat_atk = self.cat_data.get("atk", 10)
            damage_to_monster = random.randint(cat_atk - 2, cat_atk + 3)
            self.monster["hp"] -= damage_to_monster
            desc += f"🐾 **{self.cat_data['name']}**의 공격! **{damage_to_monster}**의 데미지를 입혔다!\n"

        if self.monster["hp"] <= 0:
            exp_gain = self.monster["exp"]
            gold_gain = self.monster["gold"]
            
            self.cat_data["exp"] = self.cat_data.get("exp", 0) + exp_gain
            self.cat_data["gold"] = self.cat_data.get("gold", 0) + gold_gain
            self.cat_data["stage"] = self.cat_data.get("stage", 1) + 1

            level_up_msg = ""
            while True:
                current_level = self.cat_data.get("level", 1)
                required_exp = current_level * 100
                if self.cat_data["exp"] >= required_exp:
                    self.cat_data["exp"] -= required_exp
                    self.cat_data["level"] = current_level + 1
                    self.cat_data["atk"] += 4
                    self.cat_data["max_hp"] += 15
                    self.cat_data["hp"] = self.cat_data["max_hp"]
                    level_up_msg += f"\n🎉 **LEVEL UP!** Lv.{self.cat_data['level']} 달성! (공격력+4, 최대체력+15)"
                else:
                    break

            win_title = "🏆 챕터 1 클리어! (보스 처치)" if self.monster.get("is_boss") else "🏆 전투 승리!"
            
            win_embed = discord.Embed(
                title=win_title,
                description=f"✨ **{self.monster['name']}**을(를) 무찔렀습니다!\n\n"
                            f"🎁 **보상 획득**\n"
                            f"- 💰 Gold: `+{gold_gain}` (총 보유: {self.cat_data['gold']}원)\n"
                            f"- 📈 EXP: `+{exp_gain}`{level_up_msg}\n\n"
                            f"🚩 **다음 이동 가능 스테이지:** Stage 1-{self.cat_data['stage']}",
                color=discord.Color.gold() if self.monster.get("is_boss") else discord.Color.green()
            )
            win_embed.set_image(url="https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1000")
            
            next_view = NextStageView(author=self.author, user_id=self.user_id, cat_data=self.cat_data)
            await interaction.response.edit_message(embed=win_embed, view=next_view)
            return

        cat_max_hp = self.cat_data.get("max_hp", 50)
        cat_current_hp = self.cat_data.get("hp", cat_max_hp)
        damage_to_cat = random.randint(self.monster["atk"] - 2, self.monster["atk"] + 2)
        cat_current_hp = max(0, cat_current_hp - damage_to_cat)
        self.cat_data["hp"] = cat_current_hp

        desc += f"⚡ 반격으로 **{self.monster['name']}**이(가) **{damage_to_cat}**의 피해를 주었습니다!"

        if cat_current_hp <= 0:
            current_gold = self.cat_data.get("gold", 0)
            lost_gold = int(current_gold * 0.1)
            self.cat_data["gold"] = max(0, current_gold - lost_gold)
            self.cat_data["hp"] = cat_max_hp
            self.cat_data["stage"] = 1

            lose_embed = discord.Embed(
                title="💀 패배...",
                description=f"🐾 **{self.cat_data['name']}**가 쓰러졌습니다...\n\n"
                            f"💸 정신을 차려보니 소지품을 흘렸습니다!\n"
                            f"- **잃은 골드:** `-{lost_gold} Gold`\n"
                            f"📍 안전한 로비(Stage 1-1)로 후퇴했습니다.",
                color=discord.Color.dark_gray()
            )
            lose_embed.set_image(url="https://images.unsplash.com/photo-1508873696983-2df5c920ac1c?q=80&w=1000")
            
            home_view = AdventureHomeView(author=self.author, user_id=self.user_id, cat_data=self.cat_data)
            await interaction.response.edit_message(embed=lose_embed, view=home_view)
            return

        embed = self.create_battle_embed(description=desc)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🏃 도망가기", style=discord.ButtonStyle.secondary)
    async def run_away(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.verify_user(interaction.user.id):
            await interaction.response.send_message("❌ 다른 사람의 전투입니다!", ephemeral=True)
            return

        escape_embed = discord.Embed(
            title="🏃 무사히 도망쳤다!",
            description=f"🐾 **{self.cat_data['name']}**가 위험을 감지하고 도망쳤습니다!",
            color=discord.Color.orange()
        )
        escape_embed.set_image(url="https://images.unsplash.com/photo-1548802673-380ab8ebc7b7?q=80&w=1000")

        next_view = NextStageView(author=self.author, user_id=self.user_id, cat_data=self.cat_data)
        await interaction.response.edit_message(embed=escape_embed, view=next_view)


class NextStageView(discord.ui.View):
    def __init__(self, author, user_id, cat_data):
        super().__init__(timeout=180)
        self.author = author
        self.user_id = user_id
        self.cat_data = cat_data

    def verify_user(self, interaction_user_id):
        try:
            if self.user_id and int(interaction_user_id) == int(self.user_id):
                return True
        except:
            pass
        try:
            if self.author and hasattr(self.author, 'id') and int(interaction_user_id) == int(self.author.id):
                return True
        except:
            pass
        return False

    async def trigger_walk(self, interaction: discord.Interaction):
        # 1. 3초 타임아웃 방지를 위해 먼저 메시지 수정 처리(Defer 역할)
        next_stage_num = self.cat_data.get("stage", 1)
        new_battle_view = AdventureView(author=self.author, user_id=self.user_id, cat_data=self.cat_data, stage=next_stage_num)
        upcoming_monster = new_battle_view.monster
        bg_url = upcoming_monster.get("bg_image", "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000")

        walk_embed = discord.Embed(
            title=f"🚶 Stage 1-{next_stage_num} 정글 탐사 중...",
            description=f"🐾 **{self.cat_data['name']}**가 울창한 정글 속으로 걸어가는 중...",
            color=discord.Color.light_grey()
        )
        walk_embed.set_image(url=bg_url)

        # 바로 상호작용 응답 전달 (3초 에러 완벽 차단)
        await interaction.response.edit_message(embed=walk_embed, view=None)

        # 2. 1초 연출 후 전투 화면으로 업데이트
        await asyncio.sleep(1.0)
        embed = new_battle_view.create_battle_embed(description=f"⚔️ **{upcoming_monster['name']}**이(가) 나타났습니다!")
        await interaction.message.edit(embed=embed, view=new_battle_view)

    @discord.ui.button(label="🧭 다음 스테이지 도전", style=discord.ButtonStyle.success)
    async def next_stage(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.verify_user(interaction.user.id):
            await interaction.response.send_message("❌ 본인의 고양이만 조작할 수 있습니다!", ephemeral=True)
            return
        await self.trigger_walk(interaction)

    @discord.ui.button(label="🏠 로비로 가기", style=discord.ButtonStyle.secondary)
    async def go_to_lobby(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.verify_user(interaction.user.id):
            await interaction.response.send_message("❌ 본인의 고양이만 조작할 수 있습니다!", ephemeral=True)
            return

        home_view = AdventureHomeView(author=self.author, user_id=self.user_id, cat_data=self.cat_data)
        lobby_embed = discord.Embed(
            title=f"🐾 {self.cat_data['name']}의 모험 로비",
            description=f"현재 진행 중인 최고 스테이지: **Stage 1-{self.cat_data.get('stage', 1)}**",
            color=discord.Color.blurple()
        )
        lobby_embed.set_image(url="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000")
        await interaction.response.edit_message(embed=lobby_embed, view=home_view)