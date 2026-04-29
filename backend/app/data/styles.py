"""8 门派风格数据 + 手法库"""

# ── 手法库（24 个，4 大类）──

TECHNIQUES = {
    # 化解类（拆弹）
    "自嘲解围": "把自己放低，让对方没法攻击你",
    "反转预期": "对方以为A，你突然B，制造惊喜",
    "以退为进": "先答应一部分，再条件交换",
    "转移焦点": "不正面接招，把话题引走",
    "降维打击": "把严肃问题说轻松，让紧张感消解",
    "假装认同": "先顺着说，再180度转弯",
    # 共情类（接人）
    "情绪镜像": "重复对方感受，让他觉得被看见",
    "先接后引": "先认同情绪，再引导方向",
    "换位描述": "替对方说出他没说出口的感受",
    "沉默留白": "不急着答，给空间让对方自己想",
    "先肯定后补充": "不直接否定，先说对再加而且",
    "抛回反问": "把问题变成问题，让对方自己回答",
    # 幽默类（加分）
    "夸张比喻": "把小事说大或大事说小，制造画面感",
    "谐音双关": "语音或语义的意外关联",
    "接梗反弹": "抓住对方关键词，弹一个新梗回去",
    "反差萌": "严肃场景说轻松话，或反过来",
    "一本正经胡说": "用认真语气说荒诞内容",
    "自我矮化": "把自己的短板当武器",
    # 节奏类（控场）
    "重复关键词": "重复对方的话，给自己思考时间",
    "话题切割": "把大问题切成小块，逐个击破",
    "总结确认": "所以你的意思是…对吗？",
    "故意误解": "假装理解成另一个意思，制造笑点",
    "递进式让步": "让三步进一步，每步都有条件",
    "适时示弱": "这个我真不太懂，你教教我",
}

# ── 8 门派风格 ──

STYLES = {
    "huangbo": {
        "name": "黄渤",
        "school": "自嘲反转派",
        "philosophy": "真正的幽默不是嘲笑别人，而是敢于先笑自己",
        "famous_scene": "被问「你和葛优谁演得好」→「这个时代不会阻止你自己闪耀，但也覆盖不了任何人的光辉」",
        "learn": ["自嘲解围", "反转预期", "夸张比喻", "故意误解", "接梗反弹"],
        "for_who": "想学「又好笑又有分寸」的人",
        "icon": "🎭",
    },
    "hejiong": {
        "name": "何炅",
        "school": "温暖共情派",
        "philosophy": "说话的最高境界，是让对方觉得被看见",
        "famous_scene": "颁奖典礼嘉宾手链断裂，他一句话把事故变成笑谈，全场紧张变轻松",
        "learn": ["情绪镜像", "先接后引", "先肯定后补充", "总结确认", "适时示弱"],
        "for_who": "想学「让谁都舒服」的人",
        "icon": "🌟",
    },
    "caikangyong": {
        "name": "蔡康永",
        "school": "温和智慧派",
        "philosophy": "说话不是为了表达自己，而是为了让对方听得进去",
        "famous_scene": "写《说话之道》，教的不只是技巧，而是「你怎样看待和你说话的人」",
        "learn": ["换位描述", "沉默留白", "递进式让步", "话题切割", "假装认同"],
        "for_who": "想学「四两拨千斤」的人",
        "icon": "📖",
    },
    "jialing": {
        "name": "贾玲",
        "school": "暖心示弱派",
        "philosophy": "让人喜欢你，不是靠完美，而是靠真诚",
        "famous_scene": "包贝尔婚礼上有人要扔柳岩下水，她一挡一推一自嘲，护人又没得罪任何人",
        "learn": ["自我矮化", "适时示弱", "先接后引", "自嘲解围", "以退为进"],
        "for_who": "想学「让人没法讨厌你」的人",
        "icon": "💛",
    },
    "sabeining": {
        "name": "撒贝宁",
        "school": "机智控场派",
        "philosophy": "幽默是最好的盾，学识是最好的矛",
        "famous_scene": "各种直播事故现场，总能一句话把事故变成段子，观众甚至期待他翻车",
        "learn": ["谐音双关", "一本正经胡说", "反差萌", "夸张比喻", "故意误解"],
        "for_who": "想学「随时都能抖机灵」的人",
        "icon": "⚡",
    },
    "dongqing": {
        "name": "董卿",
        "school": "优雅从容派",
        "philosophy": "真正的从容，不是不紧张，而是紧张时依然保持尊重",
        "famous_scene": "采访翻译大师许渊冲，老先生坐轮椅不便，她自然跪地平视采访，全程优雅",
        "learn": ["抛回反问", "重复关键词", "总结确认", "换位描述", "以退为进"],
        "for_who": "想学「正式场合也能优雅应对」的人",
        "icon": "🌸",
    },
    "wanghan": {
        "name": "汪涵",
        "school": "文化底蕴派",
        "philosophy": "书读多了，话自然就说好了",
        "famous_scene": "《歌手》直播孙楠突然退赛，他即兴救场3分钟，引经据典化解危机",
        "learn": ["话题切割", "沉默留白", "转移焦点", "先肯定后补充", "反转预期"],
        "for_who": "想学「有文化的高级幽默」的人",
        "icon": "📚",
    },
    "madong": {
        "name": "马东",
        "school": "理性幽默派",
        "philosophy": "最高级的说服，是对方笑着接受了你的观点",
        "famous_scene": "《奇葩说》用幽默包装尖锐话题，让观众在笑声中重新思考",
        "learn": ["假装认同", "反转预期", "抛回反问", "夸张比喻", "降维打击"],
        "for_who": "想学「笑着把事办了」的人",
        "icon": "🎯",
    },
}


def get_style_info(style_id: str) -> dict | None:
    return STYLES.get(style_id)


def get_all_styles() -> list[dict]:
    return [
        {"id": k, **v}
        for k, v in STYLES.items()
    ]


def get_user_techniques(target_styles: list[str]) -> list[str]:
    """返回用户选择的风格覆盖的所有手法（去重）"""
    seen = set()
    result = []
    for sid in target_styles:
        style = STYLES.get(sid)
        if style:
            for t in style["learn"]:
                if t not in seen:
                    seen.add(t)
                    result.append(t)
    return result


def get_technique_description(name: str) -> str:
    return TECHNIQUES.get(name, "")


def build_technique_prompt_block(target_styles: list[str]) -> str:
    """为 P3 prompt 构建手法参考段落"""
    lines = []
    for sid in target_styles:
        style = STYLES.get(sid)
        if not style:
            continue
        techs = "、".join(style["learn"])
        lines.append(f"**{style['name']}（{style['school']}）**：{techs}")
    return "\n".join(lines)


def build_style_rewrite_block(target_styles: list[str]) -> str:
    """为 P3 prompt 构建改写要求段落"""
    parts = []
    for sid in target_styles:
        style = STYLES.get(sid)
        if not style:
            continue
        name = style["name"]
        parts.append(
            f'  {{ "style": "{sid}", "style_name": "{name}", '
            f'"text": "假设是{name}本人，面对当前对话局面（不是第一轮！看对话历史），他此刻会说的一句话（1-2句口语，匹配当前紧张度，不是改用户的回应）", '
            f'"techniques": ["用到的手法1", "手法2"], '
            f'"technique_breakdown": "手法1（怎么用的）→ 手法2（怎么用的）" }}'
        )
    return "[\n" + ",\n".join(parts) + "\n]"
