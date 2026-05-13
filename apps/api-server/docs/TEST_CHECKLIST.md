# ChuChu Tree 테스트 체크리스트

| 버전 | 수정일 | 수정 사항 |
| --- | --- | --- |
| 자동생성 | 2026-02-04 | pytest 결과 기반 자동 업데이트 |

---

## 범례

- [ ] 미완료 / 실패
- [x] 통과

---

## 1. Auth 도메인

### 1.1 Integration Test

#### GET /api/v1/auth/me 테스트
- [ ] 유효한 토큰으로 인증 확인 - 성공
  > **Error:** AttributeError: 'function' object has no attribute 'container'
  ```
    ...
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  C:\Python313\Lib\asyncio\runners.py:118: in run
      return self._loop.run_until_complete(task)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  C:\Python313\Lib\asyncio\base_events.py:725: in run_until_complete
      return future.result()
             ^^^^^^^^^^^^^^^
  ..\..\..\..\AppData\Local\pypoetry\Cache\virtualenvs\backend-3vqVEanh-py3.13\Lib\site-packages\pytest_asyncio\plugin.py:309: in setup
      res = await gen_obj.__anext__()
            ^^^^^^^^^^^^^^^^^^^^^^^^^
  tests\conftest.py:55: in test_user
      container = app_with_container.container
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  E   AttributeError: 'function' object has no attribute 'container'
  ```
- [x] 토큰 없이 호출 - NO_LOGIN_STATUS 에러
- [ ] 만료된 토큰 - EXPIRED_TOKEN 에러
  > **Error:** AttributeError: 'function' object has no attribute 'container'
  ```
    ...
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  C:\Python313\Lib\asyncio\runners.py:118: in run
      return self._loop.run_until_complete(task)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  C:\Python313\Lib\asyncio\base_events.py:725: in run_until_complete
      return future.result()
             ^^^^^^^^^^^^^^^
  ..\..\..\..\AppData\Local\pypoetry\Cache\virtualenvs\backend-3vqVEanh-py3.13\Lib\site-packages\pytest_asyncio\plugin.py:309: in setup
      res = await gen_obj.__anext__()
            ^^^^^^^^^^^^^^^^^^^^^^^^^
  tests\conftest.py:55: in test_user
      container = app_with_container.container
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  E   AttributeError: 'function' object has no attribute 'container'
  ```
- [x] 유효하지 않은 토큰 - INVALID_TOKEN 에러


---

## 테스트 완료 요약

| 도메인 | Unit Test | Integration Test | 완료율 |
| --- | --- | --- | --- |
| Auth | 0/0 | 2/4 | 50% |
| **총계** | **0/0** | **2/4** | **50%** |
