from typing import Optional

from fastapi import Cookie, Depends
from dependency_injector.wiring import inject, Provide
from app.common.application.service.auth_service import AuthService
from app.common.domain.vo.current_user import CurrentUser
from app.core.containers import Container


@inject
def get_current_member(access_token: Optional[str] = Cookie(None),
                     auth_service: AuthService= Depends(Provide[Container.auth_service])) -> CurrentUser:
    return auth_service.authenticate_member(access_token)

@inject
def get_current_member_or_none(access_token: Optional[str] = Cookie(None),
                     auth_service: AuthService= Depends(Provide[Container.auth_service])) -> CurrentUser | None:
    try:
        return auth_service.authenticate_member(access_token)
    except:
        return None