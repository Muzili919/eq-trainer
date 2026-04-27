"""每日打卡 / 连击服务

统一更新 DailyLog（每日聚合）和 DailyStreak（连击天数）。
所有"用户做了点事"的入口都应该调 touch_daily_log()。
"""

from datetime import date, timedelta

from sqlmodel import Session, select

from app.models.streak import DailyLog, DailyStreak


def touch_daily_log(
    user_id: int,
    session: Session,
    *,
    practice_completed: bool = False,
    diary_added: bool = False,
    score: float | None = None,
) -> None:
    """记录用户今日活动。

    practice_completed=True 时 practices_completed +1
    diary_added=True 时 diary_count +1
    score 提供时累计平均
    """
    today = date.today()

    log = session.exec(
        select(DailyLog)
        .where(DailyLog.user_id == user_id)
        .where(DailyLog.log_date == today)
    ).first()
    if not log:
        log = DailyLog(user_id=user_id, log_date=today)

    if practice_completed:
        log.practices_completed = (log.practices_completed or 0) + 1
    if diary_added:
        log.diary_count = (log.diary_count or 0) + 1
    if score is not None:
        cnt = log.practices_completed or 1
        prev = log.avg_score or 0
        log.avg_score = round((prev * (cnt - 1) + score) / cnt, 1)

    session.add(log)
    session.commit()

    # ── 同步连击 ──
    streak = session.exec(
        select(DailyStreak).where(DailyStreak.user_id == user_id)
    ).first()
    if not streak:
        streak = DailyStreak(user_id=user_id)

    if streak.last_active_date == today:
        # 今天已经记过了，不重复加
        session.add(streak)
        session.commit()
        return

    yesterday = today - timedelta(days=1)
    if streak.last_active_date == yesterday:
        streak.current_streak = (streak.current_streak or 0) + 1
    else:
        streak.current_streak = 1
    streak.longest_streak = max(streak.longest_streak or 0, streak.current_streak)
    streak.last_active_date = today
    streak.total_days = (streak.total_days or 0) + 1

    session.add(streak)
    session.commit()
