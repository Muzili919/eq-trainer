"""种子数据加载器：把 SKILLS / STYLES / SCENARIOS 导入数据库。
启动时调用一次（idempotent，已存在则跳过）"""

from sqlmodel import Session, select

from app.models import ScenarioTemplate, Skill, StyleReference
from app.seed.scenarios_seed import to_db_dicts as scenarios_dicts
from app.seed.skills_seed import to_db_dicts as skills_dicts
from app.seed.styles_seed import to_db_dicts as styles_dicts


def seed_skills(session: Session) -> int:
    """导入 12 个核心技能。已存在 id 跳过"""
    inserted = 0
    for d in skills_dicts():
        exists = session.exec(select(Skill).where(Skill.id == d["id"])).first()
        if exists:
            continue
        session.add(Skill(**d))
        inserted += 1
    session.commit()
    return inserted


def seed_styles(session: Session) -> int:
    """导入风格基准条目。按 (persona, trigger) 去重"""
    inserted = 0
    for d in styles_dicts():
        exists = session.exec(
            select(StyleReference).where(
                StyleReference.persona == d["persona"],
                StyleReference.trigger == d["trigger"],
            )
        ).first()
        if exists:
            continue
        session.add(StyleReference(**d))
        inserted += 1
    session.commit()
    return inserted


def seed_scenarios(session: Session) -> int:
    """导入场景模板。按 title 集合对比，有差异则清空重建"""
    data = scenarios_dicts()
    existing = session.exec(select(ScenarioTemplate)).all()

    seed_titles = {d["title"] for d in data}
    db_titles = {r.title for r in existing}
    if seed_titles == db_titles:
        return 0

    for row in existing:
        session.delete(row)
    session.commit()

    for d in data:
        session.add(ScenarioTemplate(**d))
    session.commit()
    return len(data)


def seed_all(session: Session) -> dict:
    return {
        "skills": seed_skills(session),
        "styles": seed_styles(session),
        "scenarios": seed_scenarios(session),
    }
