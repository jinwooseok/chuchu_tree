# Build Genie 테스트 체크리스트

| 버전 | 수정일 | 수정 사항 |
| --- | --- | --- |
| 자동생성 | 2026-02-12 | 초기 생성 테스트 |

---

## 범례

- [ ] 미완료 / 실패
- [x] 통과

---

## 1. Activity 도메인

> 코드 커버리지: **75.3%** (964/1281 lines)

### 1.1 Unit Test

#### update_will_solve_problems() 테스트
- [x] test_update_new_problems
- [x] test_update_with_duplicate_ids_raises
- [x] test_update_empty_list_deletes_existing

#### update_solved_problems() 테스트
- [x] test_update_new_solved_problems
- [x] test_solved_removes_will_solve

#### batch_create_solved_problems() 테스트
- [x] test_batch_create_success
- [x] test_batch_with_duplicate_problem_ids_raises
- [x] test_batch_empty_records_returns_early

#### ban_problem() / unban_problem() 테스트
- [x] test_ban_problem
- [x] test_unban_problem

#### ban_tag() / unban_tag() 테스트
- [x] test_ban_tag
- [x] test_unban_tag
- [x] test_unban_tag_not_found_raises

#### get_banned_problems() 테스트
- [x] test_no_banned_problems
- [x] test_with_banned_problems

#### get_banned_tags() 테스트
- [x] test_no_banned_tags

#### Activity Controller 단위 테스트 - 함수 직접 호출
- [x] test_update_will_solve_problems_calls_service
- [x] test_update_solved_problems_calls_service
- [x] test_update_solved_and_will_solve_calls_service
- [x] test_batch_create_solved_calls_service
- [x] test_ban_problem_calls_service
- [x] test_unban_problem_calls_service
- [x] test_ban_tag_calls_service
- [x] test_unban_tag_calls_service
- [x] test_get_banned_problems_calls_service
- [x] test_get_banned_tags_calls_service
- [x] test_set_representative_tag_calls_service
- [x] test_get_problem_record_returns_api_response
- [x] test_create_problem_record_returns_api_response

#### UserActivity.create() 팩토리 메서드 테스트
- [x] test_create_user_activity

#### 풀 예정 문제 관련 테스트
- [x] test_mark_problem_to_solve
- [x] test_mark_banned_problem_raises
- [x] test_unmark_problem
- [x] test_mark_deleted_problem_restores

#### 문제 차단 관련 테스트
- [x] test_ban_problem
- [x] test_ban_already_banned_is_idempotent
- [x] test_remove_ban
- [x] test_remove_nonexistent_ban_does_nothing

#### 문제 해결 기록 관련 테스트
- [x] test_record_problem_solved
- [x] test_record_already_solved_is_idempotent
- [x] test_solving_removes_from_will_solve

#### 태그 커스터마이징 관련 테스트
- [x] test_customize_tag_exclude
- [x] test_update_existing_customization
- [x] test_remove_tag_customization
- [x] test_get_excluded_tag_ids

#### Property 테스트 (solved_problem_ids, banned_problem_ids 등)
- [x] test_solved_problem_ids
- [x] test_banned_problem_ids
- [x] test_excluded_tag_ids_property
- [x] test_will_solve_problem_ids

#### UserActivityRepositoryImpl 테스트
- [x] test_find_will_solve_problems_by_date_empty
- [x] test_find_problem_records_by_date_empty
- [x] test_find_problem_records_by_problem_ids_empty


### 1.2 Integration Test

#### Activity API - 인증 필요 엔드포인트
- [x] test_will_solve_without_auth_fails
- [x] test_solved_without_auth_fails
- [x] test_ban_problem_without_auth_fails
- [x] test_ban_tag_without_auth_fails
- [x] test_get_banned_problems_without_auth_fails
- [x] test_get_banned_tags_without_auth_fails

#### Activity API - 인증된 상태
- [x] test_update_will_solve_problems
- [x] test_update_solved_problems
- [x] test_update_solved_and_will_solve
- [x] test_batch_create_solved
- [x] test_ban_and_get_banned_problems
- [x] test_ban_and_get_banned_tags
- [x] test_unban_problem
- [x] test_unban_tag
- [x] test_set_representative_tag
- [x] test_get_problem_record


---

## 2. Auth 도메인

### 2.1 Integration Test

#### GET /api/v1/auth/login/{provider} - 소셜 로그인 URL 리다이렉트
- [x] test_kakao_login_redirects
- [x] test_naver_login_redirects
- [x] test_google_login_redirects
- [x] test_github_login_redirects

#### POST /api/v1/auth/logout
- [x] test_logout_clears_cookies
- [x] test_logout_without_token_fails

#### POST /api/v1/auth/token/refresh
- [x] test_refresh_without_token_fails

#### GET /api/v1/auth/withdraw
- [x] test_withdraw_without_token_fails

#### GET /api/v1/auth/me 테스트
- [x] 유효한 토큰으로 인증 확인 - 성공
- [x] 토큰 없이 호출 - NO_LOGIN_STATUS 에러
- [x] 만료된 토큰 - EXPIRED_TOKEN 에러
- [x] 유효하지 않은 토큰 - INVALID_TOKEN 에러


---

## 3. Baekjoon 도메인

> 코드 커버리지: **70.8%** (1049/1482 lines)

### 3.1 Unit Test

#### LinkBjAccountUsecase.execute() 테스트
- [x] test_existing_account_publishes_event
- [x] test_new_account_fetches_from_solvedac
- [x] test_solvedac_not_found_raises

#### GetBaekjoonMeUsecase.execute() 테스트
- [x] test_success
- [x] test_user_not_found_raises
- [x] test_unlinked_user_raises

#### GetStreaksUsecase.execute() 테스트
- [x] test_success
- [x] test_no_bj_account_raises
- [x] test_empty_streaks

#### GetUnrecordedProblemsUsecase.execute() 테스트
- [x] test_no_bj_account_raises
- [x] test_no_unrecorded_returns_empty
- [x] test_with_unrecorded_problems

#### UpdateBjAccountUsecase.execute() 테스트
- [x] test_solvedac_not_found_raises
- [x] test_update_success_no_new_problems

#### Baekjoon Controller 단위 테스트 - 함수 직접 호출
- [x] test_link_account_calls_usecase
- [x] test_update_link_calls_usecase
- [x] test_get_me_calls_usecase
- [x] test_get_streak_calls_usecase
- [x] test_refresh_calls_usecase
- [x] test_get_unrecorded_calls_usecase

#### BaekjoonAccount.create() 팩토리 메서드 테스트
- [x] test_create_baekjoon_account

#### 티어 관련 도메인 로직 테스트
- [x] test_update_tier
- [x] test_update_same_tier_is_noop
- [x] test_multiple_tier_updates_create_history

#### 통계 및 레이팅 테스트
- [x] test_update_statistics
- [x] test_update_rating

#### 문제 해결 기록 테스트
- [x] test_record_problem_solved
- [x] test_record_problem_with_date
- [x] test_record_multiple_problems

#### 스트릭 관련 테스트
- [x] test_add_streak
- [x] test_add_or_update_streak_new
- [x] test_add_or_update_streak_existing

#### 태그 숙련도 테스트
- [x] test_update_tag_skill

#### BaekjoonAccountRepositoryImpl 테스트
- [x] test_find_by_id_found
- [x] test_find_by_id_not_found
- [x] test_find_all

#### ProblemHistoryRepositoryImpl 테스트
- [x] test_find_solved_ids_by_bj_account_id_empty
- [x] test_find_unrecorded_problem_ids_empty

#### StreakRepositoryImpl 테스트
- [x] test_find_by_account_and_date_range_empty


### 3.2 Integration Test

#### 백준 API - 인증 필요 엔드포인트
- [x] test_link_without_auth_fails
- [x] test_get_me_without_auth_fails
- [x] test_get_streak_without_auth_fails
- [x] test_get_monthly_without_auth_fails
- [x] test_get_unrecorded_without_auth_fails
- [x] test_refresh_without_auth_fails

#### 백준 API - 인증된 상태 (백준 연동 전이라 에러 예상)
- [x] 백준 미연동 유저 → UNLINKED_USER 에러
- [x] test_get_streak_unlinked_user
- [x] test_get_unrecorded_unlinked_user


---

## 4. Common 도메인

> 코드 커버리지: **53.0%** (802/1513 lines)

### 4.1 Unit Test

#### AuthApplicationService.authenticate_user() 테스트
- [x] test_valid_token_returns_current_user
- [x] test_none_token_raises_no_login_status
- [x] test_empty_token_raises_no_login_status
- [x] test_token_without_user_id_raises_authorization_failed
- [x] test_expired_token_propagates_exception

#### AuthApplicationService.get_social_login_url() 테스트
- [x] test_kakao_login_url
- [x] test_naver_login_url
- [x] test_google_login_url
- [x] test_github_login_url
- [x] test_invalid_provider_raises

#### AuthApplicationService.logout() 테스트
- [x] test_logout_clears_cookies

#### AuthApplicationService.refresh_access_token() 테스트
- [x] test_refresh_with_valid_token
- [x] test_refresh_with_none_token_raises

#### Auth Controller 단위 테스트 - 함수 직접 호출
- [x] test_me_returns_api_response
- [x] test_logout_calls_service
- [x] test_refresh_token_calls_service
- [x] test_social_login_returns_redirect
- [x] test_social_login_callback_returns_redirect
- [x] test_withdraw_returns_redirect


---

## 5. Problem 도메인

> 코드 커버리지: **86.8%** (376/433 lines)

### 5.1 Unit Test

#### search_problem_by_keyword() 테스트
- [x] test_search_returns_empty_when_no_results
- [x] test_search_by_id_prefix
- [x] test_search_by_title_keyword

#### get_problems_info() 이벤트 핸들러 테스트
- [x] test_get_problems_info_empty
- [x] test_get_problems_info_with_data

#### _get_problems_info_logic() 내부 로직 테스트
- [x] test_empty_problems_returns_empty
- [x] test_problem_with_tags_and_targets

#### Problem Controller 단위 테스트 - 함수 직접 호출
- [x] test_search_calls_service
- [x] test_search_empty_keyword

#### Problem.create() 팩토리 메서드 테스트
- [x] test_create_problem

#### Problem.update_tier_level() 테스트
- [x] test_update_tier_level
- [x] test_update_same_tier_is_noop

#### Problem.update_title() 테스트
- [x] test_update_title
- [x] test_update_same_title_is_noop

#### Problem 태그 관련 테스트
- [x] test_add_tag
- [x] test_add_duplicate_tag_raises
- [x] test_remove_tag
- [x] test_has_any_tag_true
- [x] test_has_any_tag_false
- [x] test_has_any_tag_empty_list

#### ProblemRepositoryImpl 테스트
- [x] test_find_by_ids_empty
- [x] test_find_by_id_prefix_empty
- [x] test_find_by_title_keyword_empty


### 5.2 Integration Test

#### GET /api/v1/problems/search - 문제 검색
- [x] test_search_returns_200
- [x] test_search_no_results
- [x] test_search_without_keyword_fails


---

## 6. Recommendation 도메인

> 코드 커버리지: **50.1%** (414/826 lines)

### 6.1 Unit Test

#### Recommendation Controller 단위 테스트 - 함수 직접 호출
- [x] test_get_recommended_problems_calls_usecase

#### LevelFilterRepositoryImpl 테스트
- [x] test_find_all_active_empty

#### TagSkillRepositoryImpl 테스트
- [x] test_find_all_active_empty


### 6.2 Integration Test

#### GET /api/v1/user-accounts/me/problems - 문제 추천
- [x] test_recommendation_without_auth_fails
- [x] test_recommendation_with_auth
- [x] test_recommendation_with_filters


---

## 7. Tag 도메인

> 코드 커버리지: **90.1%** (355/394 lines)

### 7.1 Unit Test

#### get_tags() 이벤트 핸들러 테스트
- [x] test_get_tags_success
- [x] test_get_tags_empty

#### get_tag_by_command() 이벤트 핸들러 테스트
- [x] test_get_by_id
- [x] test_get_by_code
- [x] test_tag_not_found_raises

#### Tag Controller 단위 테스트 - 함수 직접 호출
- [x] test_get_all_tags_returns_api_response

#### Tag.create() 팩토리 메서드 테스트
- [x] test_create_tag

#### Tag.exclude() / include() 테스트
- [x] test_exclude_tag
- [x] test_include_tag

#### Tag.add_parent_tag() 테스트
- [x] test_add_parent_tag
- [x] test_add_self_as_parent_raises

#### Tag.add_alias() 테스트
- [x] test_add_alias
- [x] test_add_duplicate_alias_is_idempotent

#### Tag.increment_problem_count() 테스트
- [x] test_increment
- [x] test_multiple_increments

#### TagRepositoryImpl 테스트
- [x] test_find_by_id_found
- [x] test_find_by_id_not_found
- [x] test_find_by_code
- [x] test_find_active_tags


### 7.2 Integration Test

#### GET /api/v1/tags - 전체 태그 목록 (인증 불필요)
- [x] test_get_all_tags_returns_200
- [x] test_get_all_tags_returns_list


---

## 8. Target 도메인

> 코드 커버리지: **93.6%** (263/281 lines)

### 8.1 Unit Test

#### get_all_targets() 테스트
- [x] test_get_all_active_targets
- [x] test_get_all_targets_empty
- [x] test_get_targets_by_ids

#### get_target_by_command() 테스트
- [x] test_get_by_id
- [x] test_get_by_code

#### Target Controller 단위 테스트 - 함수 직접 호출
- [x] test_get_all_targets_calls_service

#### Target.create() 팩토리 메서드 테스트
- [x] test_create_target

#### Target.add_required_tag() / remove_required_tag() 테스트
- [x] test_add_required_tag
- [x] test_add_duplicate_required_tag_raises
- [x] test_remove_required_tag
- [x] test_remove_nonexistent_tag_raises
- [x] test_get_active_tags

#### Target.activate() / deactivate() 테스트
- [x] test_deactivate
- [x] test_activate

#### Target.update_display_name() 테스트
- [x] test_update_display_name
- [x] test_update_empty_name_raises
- [x] test_update_whitespace_name_raises

#### TargetRepositoryImpl 테스트
- [x] test_find_by_id_found
- [x] test_find_by_id_not_found
- [x] test_find_by_code
- [x] test_find_all_active


### 8.2 Integration Test

#### GET /api/v1/targets - 전체 목표 목록 (인증 불필요)
- [x] test_get_all_targets_returns_200
- [x] test_get_all_targets_returns_list
- [x] test_target_items_have_required_fields


---

## 9. Tier 도메인

> 코드 커버리지: **83.6%** (107/128 lines)

### 9.1 Unit Test

#### TierRepositoryImpl 테스트
- [x] test_find_by_id_found
- [x] test_find_by_id_not_found
- [x] test_find_all
- [x] test_find_by_levels
- [x] test_find_by_levels_empty
- [x] test_find_by_level
- [x] test_find_by_code


---

## 10. User 도메인

> 코드 커버리지: **78.0%** (629/806 lines)

### 10.1 Unit Test

#### create_or_find_user_account() 테스트
- [x] test_existing_user_returns_not_new
- [x] test_existing_user_email_updated
- [x] test_new_user_created

#### link_baekjoon_account() 테스트
- [x] test_link_success
- [x] test_link_user_not_found_raises

#### get_user_account_info() 테스트
- [x] test_get_info_success
- [x] test_get_info_user_not_found_raises

#### delete_user_account() 테스트
- [x] test_delete_success
- [x] test_delete_user_not_found_returns_false

#### update_user_target() 테스트
- [x] test_update_target_success
- [x] test_update_target_user_not_found

#### User Controller 단위 테스트 - 함수 직접 호출
- [x] test_set_profile_image_returns_api_response
- [x] test_delete_profile_image_returns_api_response
- [x] test_get_user_tags_calls_usecase
- [x] test_get_user_targets_calls_service
- [x] test_update_user_target_calls_service
- [x] test_get_all_user_accounts_returns_api_response

#### UserAccount.create() 팩토리 메서드 테스트
- [x] test_create_user_account
- [x] test_create_user_account_without_email

#### UserAccount.link_baekjoon_account() 테스트
- [x] test_link_baekjoon_account_first_time
- [x] test_link_already_linked_account_raises
- [x] test_link_within_cooldown_period_raises
- [x] test_link_after_cooldown_period_succeeds
- [x] test_link_deactivates_existing_active_link

#### UserAccount.unlink_baekjoon_account() 테스트
- [x] test_unlink_removes_active_link

#### UserAccount.set_target() / remove_target() 테스트
- [x] test_set_target_first_time
- [x] test_set_same_target_is_idempotent
- [x] test_set_different_target_deactivates_old
- [x] test_remove_target

#### UserAccount.update_profile_image() 테스트
- [x] test_update_profile_image

#### UserAccountRepositoryImpl 테스트
- [x] test_find_by_id_found
- [x] test_find_by_id_not_found
- [x] test_find_by_provider_found
- [x] test_exists_by_id_true
- [x] test_exists_by_id_false


---

## 11. UserAccount 도메인

### 11.1 Integration Test

#### 유저 계정 API - 인증 필요 엔드포인트
- [x] test_profile_image_without_auth_fails
- [x] test_delete_profile_image_without_auth_fails
- [x] test_get_user_tags_without_auth_fails
- [x] test_get_user_targets_without_auth_fails
- [x] test_update_user_target_without_auth_fails

#### 유저 계정 API - 인증된 상태
백준 계정 필요
- [ ] test_get_user_tags
  > **Error:** assert 404 == 200
 +  where 404 = <Response [404 Not Found]>.status_code
  ```
  tests\integration\user_account\test_user_account_flow.py:42: in test_get_user_tags
      assert resp.status_code == 200
  E   assert 404 == 200
  E    +  where 404 = <Response [404 Not Found]>.status_code
  ```
- [x] test_get_user_targets
- [x] test_delete_profile_image

#### GET /api/v1/admin/user-accounts
- [x] test_admin_without_auth_fails
- [x] test_admin_with_auth


---

## 테스트 완료 요약

| 도메인 | Unit Test | Integration Test | 완료율 | 커버리지 |
| --- | --- | --- | --- | --- |
| Activity | 52/52 | 16/16 | 100% | 75.3% |
| Auth | 0/0 | 12/12 | 100% | - |
| Baekjoon | 39/39 | 9/9 | 100% | 70.8% |
| Common | 19/19 | 0/0 | 100% | 53.0% |
| Problem | 23/23 | 3/3 | 100% | 86.8% |
| Recommendation | 3/3 | 3/3 | 100% | 50.1% |
| Tag | 19/19 | 2/2 | 100% | 90.1% |
| Target | 21/21 | 3/3 | 100% | 93.6% |
| Tier | 7/7 | 0/0 | 100% | 83.6% |
| User | 35/35 | 0/0 | 100% | 78.0% |
| UserAccount | 0/0 | 9/10 | 90% | - |
| **총계** | **218/218** | **57/58** | **99%** | **69.4%** |
