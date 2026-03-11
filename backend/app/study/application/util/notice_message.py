def _display_name(bj_id: str, user_code: str) -> str:
    return f"{bj_id}#{user_code}"


def generate_notice_message(category_detail: str | None, content: dict) -> str:
    if category_detail is None:
        return ""
    try:
        if category_detail == "REQUESTED_STUDY_INVITATION":
            name = _display_name(content.get("inviterBjAccountId", ""), content.get("inviterUserCode", ""))
            return f"{name}님이 {content.get('studyName', '')}에 초대했습니다."
        if category_detail == "RESPONSED_STUDY_INVITATION":
            name = _display_name(content.get("inviteeBjAccountId", ""), content.get("inviteeUserCode", ""))
            return f"{name}님이 초대를 수락했습니다." if content.get("status") == "ACCEPTED" else f"{name}님이 초대를 거절했습니다."
        if category_detail == "REQUESTED_STUDY_APPLICATION":
            name = _display_name(content.get("applicantBjAccountId", ""), content.get("applicantUserCode", ""))
            return f"{name}님이 {content.get('studyName', '')}에 가입 신청했습니다."
        if category_detail == "RESPONSED_STUDY_APPLICATION":
            study_name = content.get("studyName", "")
            return f"{study_name} 가입 신청이 수락되었습니다." if content.get("status") == "ACCEPTED" else f"{study_name} 가입 신청이 거절되었습니다."
        if category_detail == "ASSIGNED_STUDY_PROBLEM":
            name = _display_name(content.get("assignerBjAccountId", ""), content.get("assignerUserCode", ""))
            return f"{name}님이 {content.get('studyName', '')}에 새 풀문제를 배정했습니다."
        if category_detail == "UPDATED_USER_PROBLEM":
            total = sum(len(entry.get("problems", [])) for entry in content.get("problemsByDate", []))
            return f"새로운 문제 {total}개를 풀었습니다."
        if category_detail == "UPDATED_USER_TIER":
            return "티어가 변경되었습니다."
    except Exception:
        pass
    return ""
