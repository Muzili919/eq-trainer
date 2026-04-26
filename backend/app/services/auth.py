"""认证服务 - 注册/登录/token 验证"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.models.user import User

bearer = HTTPBearer()


def register_user(username: str, password: str, session: Session, target_role: str = "general") -> User:
    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    valid_roles = {"general", "property_manager", "decoration_boss"}
    role = target_role if target_role in valid_roles else "general"
    user = User(username=username, password_hash=hash_password(password), target_role=role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def login_user(username: str, password: str, session: Session) -> str:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return create_access_token(user.id)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_session),
) -> User:
    sub = decode_token(credentials.credentials)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
        )
    user_id = int(sub)
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
