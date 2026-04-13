from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from auth.auth_utils import decode_token

# 🔐 OAuth2 Scheme (Swagger uses this)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    description="Enter username and password to authenticate"
)


# 👤 GET CURRENT USER
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# 🔐 ADMIN ONLY
def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


# 🔐 VIEWER + ADMIN
def require_viewer(user: dict = Depends(get_current_user)):
    if user.get("role") not in ["admin", "viewer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewer access required"
        )
    return user