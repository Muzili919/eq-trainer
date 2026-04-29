from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, echo=settings.debug, connect_args=connect_args)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    _migrate_nullable_columns()


def _migrate_nullable_columns() -> None:
    """确保模型声明为可空的列在数据库中也允许 NULL。
    SQLModel 的 create_all 不会 ALTER 已有表的列约束，需手动迁移。"""
    from sqlalchemy import inspect, text

    with engine.connect() as conn:
        # diary 表：their_words 在 initiate 模式下可以为空
        try:
            insp = inspect(engine)
            cols = {c["name"]: c for c in insp.get_columns("diary")}
            if "their_words" in cols and not cols["their_words"]["nullable"]:
                conn.execute(text("ALTER TABLE diary ALTER COLUMN their_words DROP NOT NULL"))
                conn.commit()
                print("[migrate] diary.their_words → nullable ✓")
        except Exception as e:
            # PostgreSQL / MySQL 语法可能不同，SQLite 也可能不支持 ALTER COLUMN
            # SQLite 不支持 ALTER COLUMN，需要用重建表的方式
            if "near \"ALTER\"" in str(e).lower() or "syntax error" in str(e).lower():
                _sqlite_make_nullable(conn, "diary", "their_words")
            else:
                print(f"[migrate] skipped diary.their_words: {e}")


def _sqlite_make_nullable(conn, table: str, column: str) -> None:
    """SQLite 不支持 ALTER COLUMN，通过重建表来修改列约束。"""
    from sqlalchemy import text

    # 获取当前表定义
    result = conn.execute(text(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'"))
    row = result.fetchone()
    if not row:
        return

    old_sql = row[0]
    # 替换目标列为可空
    import re
    new_sql = re.sub(
        rf'({column}\s+VARCHAR)\s+NOT\s+NULL',
        rf'\1',
        old_sql,
        flags=re.IGNORECASE,
    )
    if new_sql == old_sql:
        return  # 没有变化

    # SQLite 重建表流程
    tmp_table = f"_tmp_{table}"
    conn.execute(text(f"ALTER TABLE {table} RENAME TO {tmp_table}"))
    conn.execute(text(new_sql))
    # 获取新表的列名
    col_result = conn.execute(text(f"PRAGMA table_info({table})"))
    col_names = [r[1] for r in col_result]
    cols_str = ", ".join(col_names)
    conn.execute(text(f"INSERT INTO {table} ({cols_str}) SELECT {cols_str} FROM {tmp_table}"))
    conn.execute(text(f"DROP TABLE {tmp_table}"))
    conn.commit()
    print(f"[migrate] {table}.{column} → nullable (rebuilt table) ✓")


def get_session():
    with Session(engine) as session:
        yield session
