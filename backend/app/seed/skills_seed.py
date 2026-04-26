"""12 个核心技能种子数据，对应 docs/SKILLS.md"""

import json

SKILLS_SEED = [
    # ============ 倾听类 ============
    {
        "id": "L1",
        "category": "listening",
        "name": "情绪命名",
        "name_en": "emotion_naming",
        "stage": "basic",
        "description": "用一句话说出对方此刻的感受，让对方'被看见'",
        "patterns": ["你听起来有点 [情绪]", "这件事让你 [情绪] 了对吧", "我感觉到你 [情绪]"],
        "examples_good": [
            {"trigger": "我妈又开始念叨了", "good": "听起来你挺烦的，又不是想真跟她吵"}
        ],
        "examples_bad": [{"trigger": "我妈又开始念叨了", "bad": "哎你别想了"}],
        "socratic_prompts": [
            "对方这句话背后是什么情绪？",
            "如果你是 ta，你最想被听到的是什么？",
            "ta 是想要解决方案，还是想被理解？",
        ],
        "prerequisites": [],
        "icon": "🎧",
        "sort_order": 1,
    },
    {
        "id": "L2",
        "category": "listening",
        "name": "积极倾听复述",
        "name_en": "active_listening_paraphrase",
        "stage": "basic",
        "description": "用自己的话把对方关键意思重述一遍，确认理解 + 让对方感到被听",
        "patterns": ["你的意思是 [复述]，对吗", "我听到的是 [复述]"],
        "examples_good": [
            {
                "trigger": "领导今天又改方案了，我之前白做",
                "good": "你今天等于被推翻重来了，难怪烦",
            }
        ],
        "examples_bad": [{"trigger": "领导今天又改方案了，我之前白做", "bad": "嗯"}],
        "socratic_prompts": [
            "你能用一句话说出 ta 刚刚抱怨的核心吗？",
            "复述跟评价有什么区别？",
        ],
        "prerequisites": [],
        "icon": "👂",
        "sort_order": 2,
    },
    # ============ 表达类 ============
    {
        "id": "E1",
        "category": "expression",
        "name": "我句式",
        "name_en": "i_statement",
        "stage": "basic",
        "description": "用'我感受/我需要'代替'你总是/你从来'，避免触发对方防御",
        "patterns": ["我感觉 [感受]", "我需要 [需要]", "我希望我们能 [想法]"],
        "examples_good": [
            {
                "trigger": "（伴侣不洗碗）",
                "good": "我看到水池里又有碗，有点烦——咱们能不能定个规矩",
            }
        ],
        "examples_bad": [
            {"trigger": "（伴侣不洗碗）", "bad": "你又把碗放水池不洗，你怎么这么懒"}
        ],
        "socratic_prompts": [
            "如果有人对你说『你总是 XX』，你第一反应是什么？",
            "把『你』换成『我』，句子的攻击性变了多少？",
        ],
        "prerequisites": [],
        "icon": "🗣",
        "sort_order": 3,
    },
    {
        "id": "E2",
        "category": "expression",
        "name": "非暴力沟通四步",
        "name_en": "nvc_four_steps",
        "stage": "mid",
        "description": "观察 → 感受 → 需要 → 请求。表达不满或建议时的完整框架",
        "patterns": ["[观察事实] + [我感觉] + [我需要] + [我希望你...]"],
        "examples_good": [
            {
                "trigger": "（伴侣加班没回消息）",
                "good": "我今天给你发了三条没回，心里有点失落，我希望我对你重要，下次忙也回个'晚点说'吗？",
            }
        ],
        "examples_bad": [
            {"trigger": "（伴侣加班没回消息）", "bad": "你今天加班又没回消息，眼里没我"}
        ],
        "socratic_prompts": [
            "你说的是事实还是评价？",
            "你真正需要的，是 ta 道歉，还是 ta 的某种行为？",
            "你的请求具体到 ta 知道下一步怎么做了吗？",
        ],
        "prerequisites": ["L1"],
        "icon": "💬",
        "sort_order": 4,
    },
    # ============ 共情类 ============
    {
        "id": "EM1",
        "category": "empathy",
        "name": "接纳不评判",
        "name_en": "non_judgmental_acceptance",
        "stage": "basic",
        "description": "对方表达情绪时，不评判对错、不给方案、不讲道理，先接住情绪",
        "patterns": ["嗯，难怪你...", "换我也这样", "这事确实够烦的"],
        "examples_good": [
            {"trigger": "我又跟我妈吵架了", "good": "又来了？你当时一定很难受"}
        ],
        "examples_bad": [
            {"trigger": "我又跟我妈吵架了", "bad": "你脾气也太冲了，跟妈妈吵啥呀"}
        ],
        "socratic_prompts": [
            "ta 现在需要的是判断对错，还是一个能接住情绪的人？",
            "如果你给方案，ta 下次还想跟你说吗？",
        ],
        "prerequisites": [],
        "icon": "🤲",
        "sort_order": 5,
    },
    {
        "id": "EM2",
        "category": "empathy",
        "name": "视角切换",
        "name_en": "perspective_taking",
        "stage": "mid",
        "description": "能主动从对方角度想问题，并把这种'我看到你了'传递出来",
        "patterns": ["如果我是你，我可能也会...", "站在你那个位置...", "你那时候做这个决定，肯定考虑了..."],
        "examples_good": [
            {"trigger": "（朋友没拒绝某件事）", "good": "当着那么多人，你那时候要拒绝肯定挺难为情的"}
        ],
        "examples_bad": [{"trigger": "（朋友没拒绝某件事）", "bad": "你当时为啥不直接拒绝？"}],
        "socratic_prompts": ["如果你站在 ta 的位置，那一刻你最在意的是什么？"],
        "prerequisites": ["EM1"],
        "icon": "🔄",
        "sort_order": 6,
    },
    # ============ 边界类 ============
    {
        "id": "B1",
        "category": "boundary",
        "name": "温柔拒绝",
        "name_en": "gentle_decline",
        "stage": "mid",
        "description": "不接对方请求，但不让对方下不来台、不破坏关系",
        "patterns": ["[认可对方] + [简短解释] + [不接] + [留余地]"],
        "examples_good": [
            {
                "trigger": "（同事请你帮忙做 ta 的活）",
                "good": "谢谢你想到我，这周我手上几个事都赶着，下次有类似的再叫我",
            }
        ],
        "examples_bad": [{"trigger": "（同事请你帮忙）", "bad": "不行，我没空"}],
        "socratic_prompts": [
            "拒绝最伤人的不是『不』字，是什么？",
            "你这次拒绝完，下次 ta 还敢找你吗？这是你想要的关系吗？",
        ],
        "prerequisites": ["E1"],
        "icon": "🛡",
        "sort_order": 7,
    },
    # ============ 化解类 ============
    {
        "id": "R1",
        "category": "resolution",
        "name": "转移焦点",
        "name_en": "topic_redirection",
        "stage": "mid",
        "description": "话题不舒服或将引爆冲突时，平滑切到另一个话题，不让对方察觉被避开",
        "patterns": ["[先回应一句] + [自然带出新话题]"],
        "examples_good": [
            {
                "trigger": "你工资多少啊？",
                "good": "够花，主要现在物价你都不知道，我前两天买盒榴莲花了 80",
            }
        ],
        "examples_bad": [{"trigger": "你工资多少啊？", "bad": "这个不太方便说"}],
        "socratic_prompts": ["怎么让转移自然到对方意识不到你在避开？"],
        "prerequisites": [],
        "icon": "🔀",
        "sort_order": 8,
    },
    {
        "id": "R2",
        "category": "resolution",
        "name": "道歉与修复",
        "name_en": "apology_repair",
        "stage": "mid",
        "description": "错了或让对方不舒服了，承认 + 不找借口 + 给修复动作",
        "patterns": ["[具体承认错在哪] + [不解释] + [下次怎么做]"],
        "examples_good": [
            {
                "trigger": "（昨天没回消息）",
                "good": "我昨天没回你消息，把你晾了一下午，是我不对。下次再忙我也回一句'在忙晚点说'",
            }
        ],
        "examples_bad": [
            {
                "trigger": "（昨天没回消息）",
                "bad": "对不起对不起，我也不是故意的，那时候确实忙嘛",
            }
        ],
        "socratic_prompts": [
            "道歉时找借口的代价是什么？",
            "什么样的修复动作让对方真的相信下次不会再发生？",
        ],
        "prerequisites": ["EM1"],
        "icon": "🌱",
        "sort_order": 9,
    },
    # ============ 幽默类（高阶，需前置）============
    {
        "id": "H1",
        "category": "humor",
        "name": "自嘲化解",
        "name_en": "self_deprecating_humor",
        "stage": "advanced",
        "description": "被攻击/被夸/被尴尬时，把矛头转向自己，用降维让对方无处发力",
        "patterns": ["把对方话里的预设反向说成自己的特点"],
        "examples_good": [
            {
                "trigger": "你怎么还没结婚？",
                "good": "（黄渤式）我这条件你也看见了，能赖着活到现在已经不错了",
            },
            {
                "trigger": "你怎么还没结婚？",
                "good": "（徐志胜式）我也想啊，可你看我这脸，月老看一眼都觉得是自己工作没做到位",
            },
        ],
        "examples_bad": [{"trigger": "你怎么还没结婚？", "bad": "关你什么事"}],
        "socratic_prompts": [
            "对方这句话的预设是什么？",
            "你能不能把这个预设反过来当玩笑说？",
            "自嘲的边界在哪——什么样的自嘲是健康的，什么样会变讨好？",
        ],
        "prerequisites": ["EM1", "R1"],
        "icon": "🌟",
        "sort_order": 10,
    },
    {
        "id": "H2",
        "category": "humor",
        "name": "错位反应",
        "name_en": "expectation_subversion",
        "stage": "advanced",
        "description": "对方期待你给 A 反应，你给 B——制造预期落差产生幽默",
        "patterns": ["该认真时装糊涂", "该装糊涂时一本正经", "该接茬时不接"],
        "examples_good": [
            {
                "trigger": "这报告你写得真不错",
                "good": "（李雪琴式）是吧？我也觉得，但不是我写的",
            },
            {
                "trigger": "这报告你写得真不错",
                "good": "（黄渤式）千万别再夸了，再夸领导真就让我多写几个了",
            },
        ],
        "examples_bad": [{"trigger": "这报告你写得真不错", "bad": "哎呀谢谢谢谢"}],
        "socratic_prompts": [
            "对方期待的是什么反应？你能给一个跟期待错位的吗？",
            "错位是夸张，还是反方向？",
        ],
        "prerequisites": ["L1", "R1"],
        "icon": "🎭",
        "sort_order": 11,
    },
    {
        "id": "H3",
        "category": "humor",
        "name": "接梗给梗",
        "name_en": "callback_humor",
        "stage": "advanced",
        "description": "对方抛梗，你不仅接住，还把它升级一层抛回去",
        "patterns": ["抓住对方梗的核心隐喻，扩展或反转"],
        "examples_good": [
            {
                "trigger": "你最近是不是又胖了？",
                "good": "我这是为冬天储备能量，你想想北极熊为啥能活那么久",
            },
            {
                "trigger": "你最近是不是又胖了？",
                "good": "我跟北极熊唯一区别是它有粮票",
            },
        ],
        "examples_bad": [{"trigger": "你最近是不是又胖了？", "bad": "没有啊"}],
        "socratic_prompts": [
            "ta 这个梗的核心比喻是什么？",
            "你能不能顺着这个比喻再往前推一步？",
            "升级梗时，是要扩展（更夸张）还是反转（朝相反方向）？",
        ],
        "prerequisites": ["H1"],  # 或 H2，但 SQL 表只支持一个，先以 H1 为主路径
        "icon": "🎤",
        "sort_order": 12,
    },
]


def to_db_dicts() -> list[dict]:
    """转成可直接 insert 的字典（list/dict 字段序列化为 JSON 字符串）"""
    out = []
    for s in SKILLS_SEED:
        d = dict(s)
        d["patterns"] = json.dumps(s["patterns"], ensure_ascii=False)
        d["examples_good"] = json.dumps(s["examples_good"], ensure_ascii=False)
        d["examples_bad"] = json.dumps(s["examples_bad"], ensure_ascii=False)
        d["socratic_prompts"] = json.dumps(s["socratic_prompts"], ensure_ascii=False)
        d["prerequisites"] = json.dumps(s["prerequisites"], ensure_ascii=False)
        out.append(d)
    return out
