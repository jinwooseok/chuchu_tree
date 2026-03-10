def generate_notice_message(category_detail: str | None, content: dict) -> str:
    if category_detail is None:
        return ""
    try:
        if category_detail == "REQUESTED_STUDY_INVITATION":
            return f"{content.get('inviterUserCode', '')}님이 {content.get('studyName', '')}에 초대했습니다."
        if category_detail == "RESPONSED_STUDY_INVITATION":
            code = content.get("inviteeUserCode", "")
            return f"{code}님이 초대를 수락했습니다." if content.get("status") == "ACCEPTED" else f"{code}님이 초대를 거절했습니다."
        if category_detail == "REQUESTED_STUDY_APPLICATION":
            return f"{content.get('applicantUserCode', '')}님이 {content.get('studyName', '')}에 가입 신청했습니다."
        if category_detail == "RESPONSED_STUDY_APPLICATION":
            study_name = content.get("studyName", "")
            return f"{study_name} 가입 신청이 수락되었습니다." if content.get("status") == "ACCEPTED" else f"{study_name} 가입 신청이 거절되었습니다."
        if category_detail == "ASSIGNED_STUDY_PROBLEM":
            return f"{content.get('studyName', '')}에 새 풀문제가 배정되었습니다."
        if category_detail == "UPDATED_USER_PROBLEM":
            return f"새로운 문제 {len(content.get('problems', []))}개를 풀었습니다."
        if category_detail == "UPDATED_USER_TIER":
            return "티어가 변경되었습니다."
    except Exception:
        pass
    return ""
