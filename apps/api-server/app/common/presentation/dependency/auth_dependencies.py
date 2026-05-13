from typing import Optional

from fastapi import Cookie, Depends
from dependency_injector.wiring import inject, Provide
from app.common.application.service.auth_application_service import AuthApplicationService
from app.common.domain.vo.current_user import CurrentUser
from app.core.containers import Container


@inject
def get_current_member(access_token: Optional[str] = Cookie(None),
                     auth_application_service: AuthApplicationService= Depends(Provide[Container.auth_application_service])) -> CurrentUser:
    return auth_application_service.authenticate_user(access_token)

@inject
def get_current_member_or_none(access_token: Optional[str] = Cookie(None),
                     auth_application_service: AuthApplicationService= Depends(Provide[Container.auth_application_service])) -> CurrentUser | None:
    try:
        return auth_application_service.authenticate_user(access_token)
    except:
        return None