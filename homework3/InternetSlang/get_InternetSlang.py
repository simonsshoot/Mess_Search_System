import json

# 主要英文网络用语列表
internet_slang = [
    # 经典缩写
    "LOL", "OMG", "WTF", "BRB", "TTYL", "ROFL", "LMAO", "SMH", "FML", "TMI",
    "YOLO", "FOMO", "GOAT", "ASAP", "FYI", "IMO", "IMHO", "TBH", "NGL", "IRL",
    
    # 聊天常用
    "AFK", "GTG", "CU", "CYA", "THX", "TY", "YW", "NP", "JK", "IDK", "IDC",
    "IDGAF", "DGAF", "STFU", "GTFO", "RTFM", "TLDR", "ELI5", "FTFY", "IIRC",
    
    # 情感表达
    "LMFAO", "ROTFL", "PMSL", "ROFLMAO", "CTFU", "DEAD", "WEAK", "CRINGE",
    "SALTY", "SAVAGE", "FIRE", "LIT", "STAN", "PERIODT", "SLAY", "FLEX",
    
    # 网络文化
    "MEME", "VIRAL", "TROLL", "NOOB", "PWNED", "REKT", "OWNED", "FAIL",
    "EPIC", "BASED", "CRINGE", "SUS", "CAP", "NOCAP", "FACTS", "MOOD",
    
    # 游戏相关
    "GG", "GGWP", "GGEZ", "GLHF", "RQ", "DC", "LAG", "NERF", "BUFF", "OP",
    "META", "TRYHARD", "CAMPER", "SCRUB", "PWNT", "WASTED", "RESPAWN",
    
    # 社交媒体
    "DM", "PM", "RT", "MT", "FF", "TL", "NSFW", "SFW", "ICYMI", "TBT",
    "OOTD", "SELFIE", "PHOTOBOMB", "HASHTAG", "VIRAL", "TRENDING", "SLIDE",
    
    # 约会/关系
    "DTF", "NSA", "FWB", "BAE", "SO", "BF", "GF", "EX", "THOT", "SIMP",
    "CUCK", "CHAD", "KAREN", "INCEL", "FEMCEL", "PICK ME", "RED FLAG",
    
    # 表达意见
    "BASED", "WOKE", "CANCELLED", "RATIO", "L", "W", "COPE", "SEETHE",
    "DILATE", "RENT FREE", "TOUCH GRASS", "GO OUTSIDE", "CHRONICALLY ONLINE",
    
    # 网络俚语
    "YEET", "YEETED", "SKRRT", "BRUH", "FAM", "BRO", "SIS", "BESTIE",
    "PERIODT", "AND I OOP", "TEA", "SPILL THE TEA", "DRAG", "SHADE",
    
    # 潮流用语
    "BUSSIN", "SLAPS", "HITS DIFFERENT", "VIBE", "VIBES", "VIBING",
    "CHIEF", "LOWKEY", "HIGHKEY", "DEADASS", "STRAIGHT UP", "FR",
    
    # 反应词
    "SHOOK", "PRESSED", "TRIGGERED", "BUTTHURT", "MAD", "BIG MAD",
    "CLAPPED", "COOKED", "FINISHED", "DONE", "OVER", "EXPIRED",
    
    # 赞美/批评
    "QUEEN", "KING", "ICON", "LEGEND", "STAN", "UNSTAN", "FLOP",
    "SERVE", "SERVED", "ATE", "LEFT NO CRUMBS", "DEVOURED", "SLAYED",
    
    # 网络行为
    "LURK", "LURKING", "SPAM", "FLOOD", "SLIDE", "SLIDING", "GHOST",
    "GHOSTED", "CATFISH", "DOXED", "SWATTED", "RATIOED", "BRIGADED",
    
    # 时间相关
    "RN", "ATM", "24/7", "ASAP", "ETA", "TBA", "TBD", "SOON TM",
    
    # 同意/不同意
    "FACTS", "TRUTH", "REAL", "REAL TALK", "PREACH", "THIS", "EXACTLY",
    "NOPE", "NAH", "HELL NO", "ABSOLUTELY NOT", "NEGATIVE", "DENIED",
    
    # 粗俗但常用
    "DAMN", "SHIT", "FUCK", "FUCKING", "ASS", "BITCH", "BASTARD",
    "PISS", "CRAP", "DUMB", "STUPID", "RETARDED", "GAY", "HOMO",
    
    # 网络特有表达
    "KAPPA", "POGGERS", "MONKAS", "PEPEGA", "5HEAD", "OMEGALUL",
    "JEBAITED", "COPIUM", "HOPIUM", "MALDING", "WEIRDCHAMP", "SADGE",
    
    # 其他常见缩写
    "AFAIK", "IIUC", "OTOH", "FWIW", "YMMV", "IANAL", "PITA", "SNAFU",
    "BOHICA", "FUBAR", "TARFU", "REMF", "FIGMO", "DILLIGAF",
    
    # Z世代用语
    "PERIODT", "SKSKSK", "AND I OOP", "VSCO GIRL", "E GIRL", "E BOY",
    "SOFTBOI", "PICK ME GIRL", "NPC", "MAIN CHARACTER", "SIDE CHARACTER",
    
    # TikTok/短视频用语
    "CHEUGY", "UNDERSTOOD THE ASSIGNMENT", "RENT FREE", "ITS THE X FOR ME",
    "TELL ME WITHOUT TELLING ME", "POV", "MAIN CHARACTER ENERGY",
    
    # Discord/游戏社区
    "MALD", "MALDING", "COPEGE", "AWARE", "UNAWARE", "CLUELESS",
    "EZ CLAP", "HARD STUCK", "DIFF", "JUNGLE DIFF", "MID DIFF",
    
    # 更多粗俗用语
    "GTFOH", "STFD", "STFUAJPG", "DILLIGAF",
    
    # 网络迷因
    "DOGE", "STONKS", "HODL", "DIAMOND HANDS", "PAPER HANDS", "TO THE MOON",
    "MONKE", "REJECT HUMANITY", "RETURN TO MONKE", "AMOGUS", "WHEN THE IMPOSTER IS SUS"
]

def generate_jsonl():
    """生成包含网络用语的JSONL文件"""
    
    # 去重并排序
    unique_slang = sorted(list(set(internet_slang)))
    
    print(f"正在生成包含 {len(unique_slang)} 个网络用语的文件...")
    
    # 写入JSONL文件
    with open('Internet_slang.jsonl', 'w', encoding='utf-8') as f:
        for slang in unique_slang:
            json_line = {"name": slang}
            f.write(json.dumps(json_line) + '\n')
    
    print("文件 'Internet_slang.jsonl' 生成完成！")
    
    # 显示前10个条目作为示例
    print("\n前10个条目示例:")
    for i, slang in enumerate(unique_slang[:10]):
        print(f"{i+1}. {slang}")
    
    print(f"\n总共生成了 {len(unique_slang)} 个网络用语")

if __name__ == "__main__":
    generate_jsonl()