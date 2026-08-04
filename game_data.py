# game_data.py

MONSTERS = {
    # 1-1 ~ 1-2: 정글 입구 (약한 동식물)
    1: [{
        "name": "🍄 포자 독버섯",
        "hp": 20, "atk": 4, "gold": 10, "exp": 20,
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1000",
        "bg_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000"
    }],
    2: [{
        "name": "🐸 정글 독개구리",
        "hp": 30, "atk": 6, "gold": 18, "exp": 30,
        "image": "https://i.pinimg.com/736x/db/aa/48/dbaa48849fca40a9b05fce57a7fd437c.jpg",
        "bg_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000"
    }],

    # 1-3 ~ 1-4: 밀림 속으로 (맹수 및 식인식물)
    3: [{
        "name": "🌱 식인 덩굴 식물",
        "hp": 45, "atk": 9, "gold": 25, "exp": 45,
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1000",
        "bg_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000"
    }],
    4: [{
        "name": "🐍 대왕 아나콘다",
        "hp": 60, "atk": 12, "gold": 35, "exp": 60,
        "image": "https://images.unsplash.com/photo-1564466809058-bf4114d55352?q=80&w=1000",
        "bg_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000"
    }],

    # 1-5 ~ 1-6: 깊은 밀림 (강력한 정글 맹수)
    5: [{
        "name": "🐒 광란의 붉은 원숭이",
        "hp": 80, "atk": 15, "gold": 50, "exp": 80,
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1000",
        "bg_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000"
    }],
    6: [{
        "name": "🐆 그림자 재규어",
        "hp": 105, "atk": 19, "gold": 70, "exp": 105,
        "image": "https://images.unsplash.com/photo-1564466809058-bf4114d55352?q=80&w=1000",
        "bg_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000"
    }],

    # 1-7 ~ 1-9: 정글의 비경 (요괴 및 고대 지배자)
    7: [{
        "name": "🕷️ 맹독 타란튤라",
        "hp": 130, "atk": 23, "gold": 90, "exp": 135,
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1000",
        "bg_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000"
    }],
    8: [{
        "name": "🦍 흉포한 킹고릴라",
        "hp": 160, "atk": 28, "gold": 120, "exp": 170,
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=1000",
        "bg_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000"
    }],
    9: [{
        "name": "🐊 고대 정글 악어",
        "hp": 200, "atk": 33, "gold": 160, "exp": 220,
        "image": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?q=80&w=1000",
        "bg_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000"
    }],

    # Stage 1-10: [정글의 보스]
    10: [{
        "name": "🔥 [BOSS] 천년묵은 정글 구미호",
        "hp": 300, "atk": 40, "gold": 500, "exp": 500,
        "is_boss": True,
        "dodge_rate": 0.40,  # 40% 회피
        "boss_quote": "네 심장은 꽤 맛있어 보이는구나.",
        "image": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?q=80&w=1000",
        "bg_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1000"
    }]
}