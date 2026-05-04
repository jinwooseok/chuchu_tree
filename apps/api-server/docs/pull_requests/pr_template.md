## 추천 기능 수정 요약

1. exclusion_mode 추가 (제외 수준: 엄격함 (STRICT), 느슨함 (LINIENT))
    - exclusion_mode = "LINIENT" : 태그가 제외되어도 연관 태그에 포함될 수 있습니다.
    - exclusion_mode = "STRICT" : 태그가 제외되었다면 연관 태그에도 포함되지 않습니다.
    
2. 푼 문제가 추천되는 오류 수정
    - 푼 문제 ID 전달 오류가 발생했던 것을 수정했습니다.

3. 유저의 목표 반영
    3-1. 목표 표기명 추가 :{"DAILY": "일상", "CT":"코딩테스트","BEGINNER":"초심자"}
    3-2. 목표 저장 시 비활성화 상태로 저장되는 오류 수정
    3-3. 목표가 추천 시 반영됩니다. 점수 +30점, 
    3-4. 현재 추천 로직 SCORE RULE 요약
        - 타겟 일치 가중치 : 30점
        - 승급 임박 가중치(5문제 이내) : 30점
        - 복습 주기 점수 : 기본 10점 + 초과일 * 2, 처음 푸는 경우 40, 가입 전 기록이 있는데 주기 파악 안되는 경우 20
    
4. 난이도 수정
    너무 쉽거나 어려운 문제가 뜨는 이슈 수정을 위해 데이터 설정을 변경했습니다.
    - 보통 난이도 티어 제한 -5 ~ 0 설정
    - 어려움 난이도 티어 제한 0 ~ 2 설정

5. 문제의 주요 원인 태그 추가
    문제의 추천 태그에 우선 태그 설정을 추가해 추천한 주요 원인 태그를 가장 앞단에 위치시켰습니다.
    
6. 사용자 will solve 문제 점수 로직 제거
    찜한 문제와 관련된 태그에 가중치를 주는 규칙을 제거했습니다. 그 문제를 풀고 싶다는 것이지 태그에 가중치를 주는게 안맞다고 판단했습니다.

### 테스트 결과 (LINIENT 10개 추출)
```cmd
[DEBUG TARGET] User has active target: TargetId(value=2)
[DEBUG TARGET] Target tag count: 45
[DEBUG TARGET] Target tags: ['구현', '다이나믹 프로그래밍', '그리디 알고리즘', '문자열', '브루트포스 알고리즘']...
[DEBUG EXCLUDED] 제외된 태그 (1개): ['수학']
[DEBUG EXCLUDED] Exclusion Mode: LENIENT

[DEBUG TARGET] Tag '구현' (ID: 2) matches target! Score: 42.0
[DEBUG TARGET] Tag '다이나믹 프로그래밍' (ID: 3) matches target! Score: 30.0
[DEBUG TARGET] Tag '그리디 알고리즘' (ID: 6) matches target! Score: 80.0
[DEBUG TARGET] Tag '문자열' (ID: 7) matches target! Score: 50.0
[DEBUG TARGET] Tag '브루트포스 알고리즘' (ID: 8) matches target! Score: 50.0
[DEBUG TARGET] Tag '애드 혹' (ID: 11) matches target! Score: 50.0
[DEBUG TARGET] Tag '트리' (ID: 13) matches target! Score: 80.0
[DEBUG TARGET] Tag '세그먼트 트리' (ID: 15) matches target! Score: 80.0
[DEBUG TARGET] Tag '이분 탐색' (ID: 16) matches target! Score: 80.0
[DEBUG TARGET] Tag '집합과 맵' (ID: 17) matches target! Score: 72.0
[DEBUG TARGET] Tag '시뮬레이션' (ID: 20) matches target! Score: 50.0
[DEBUG TARGET] Tag '누적 합' (ID: 21) matches target! Score: 80.0
[DEBUG TARGET] Tag '너비 우선 탐색' (ID: 23) matches target! Score: 50.0
[DEBUG TARGET] Tag '최단 경로' (ID: 25) matches target! Score: 80.0
[DEBUG TARGET] Tag '비트마스킹' (ID: 26) matches target! Score: 80.0
[DEBUG TARGET] Tag '깊이 우선 탐색' (ID: 27) matches target! Score: 50.0
[DEBUG TARGET] Tag '해시를 사용한 집합과 맵' (ID: 28) matches target! Score: 50.0
[DEBUG TARGET] Tag '데이크스트라' (ID: 29) matches target! Score: 50.0
[DEBUG TARGET] Tag '백트래킹' (ID: 31) matches target! Score: 50.0
[DEBUG TARGET] Tag '분리 집합' (ID: 32) matches target! Score: 50.0
[DEBUG TARGET] Tag '트리에서의 다이나믹 프로그래밍' (ID: 33) matches target! Score: 50.0
[DEBUG TARGET] Tag '트리를 사용한 집합과 맵' (ID: 34) matches target! Score: 70.0
[DEBUG TARGET] Tag '우선순위 큐' (ID: 35) matches target! Score: 50.0
[DEBUG TARGET] Tag '분할 정복' (ID: 39) matches target! Score: 50.0
[DEBUG TARGET] Tag '두 포인터' (ID: 40) matches target! Score: 80.0
[DEBUG TARGET] Tag '스택' (ID: 41) matches target! Score: 50.0
[DEBUG TARGET] Tag '느리게 갱신되는 세그먼트 트리' (ID: 43) matches target! Score: 50.0
[DEBUG TARGET] Tag '최대 유량' (ID: 45) matches target! Score: 50.0
[DEBUG TARGET] Tag '비트필드를 이용한 다이나믹 프로그래밍' (ID: 46) matches target! Score: 50.0
[DEBUG TARGET] Tag '배낭 문제' (ID: 49) matches target! Score: 50.0
[DEBUG TARGET] Tag '재귀' (ID: 52) matches target! Score: 50.0
[DEBUG TARGET] Tag '임의 정밀도 / 큰 수 연산' (ID: 53) matches target! Score: 50.0
[DEBUG TARGET] Tag '유클리드 호제법' (ID: 54) matches target! Score: 50.0
[DEBUG TARGET] Tag '최소 스패닝 트리' (ID: 55) matches target! Score: 50.0
[DEBUG TARGET] Tag '위상 정렬' (ID: 58) matches target! Score: 80.0
[DEBUG TARGET] Tag '에라토스테네스의 체' (ID: 60) matches target! Score: 50.0
[DEBUG TARGET] Tag '격자 그래프' (ID: 62) matches target! Score: 50.0
[DEBUG TARGET] Tag '최소 공통 조상' (ID: 64) matches target! Score: 50.0
[DEBUG TARGET] Tag '플로이드–워셜' (ID: 68) matches target! Score: 50.0
[DEBUG TARGET] Tag '역추적' (ID: 71) matches target! Score: 80.0
[DEBUG TARGET] Tag '트라이' (ID: 78) matches target! Score: 50.0
[DEBUG TARGET] Tag '덱' (ID: 79) matches target! Score: 50.0
[DEBUG TARGET] Tag '슬라이딩 윈도우' (ID: 86) matches target! Score: 50.0
[DEBUG TARGET] Tag '가장 긴 증가하는 부분 수열 문제' (ID: 94) matches target! Score: 50.0
[DEBUG TARGET] Tag '큐' (ID: 111) matches target! Score: 50.0

========== [DEBUG] 태그 점수 Top 20 ==========
1. 그리디 알고리즘             | Score:   80.0 🎯 [TARGET]
2. 트리                   | Score:   80.0 🎯 [TARGET]
3. 세그먼트 트리              | Score:   80.0 🎯 [TARGET]
4. 이분 탐색                | Score:   80.0 🎯 [TARGET]
5. 누적 합                 | Score:   80.0 🎯 [TARGET]
6. 최단 경로                | Score:   80.0 🎯 [TARGET]
7. 비트마스킹                | Score:   80.0 🎯 [TARGET]
8. 두 포인터                | Score:   80.0 🎯 [TARGET]
9. 위상 정렬                | Score:   80.0 🎯 [TARGET]
10. 역추적                  | Score:   80.0 🎯 [TARGET]
11. 집합과 맵                | Score:   72.0 🎯 [TARGET]
12. 트리를 사용한 집합과 맵        | Score:   70.0 🎯 [TARGET]
13. 문자열                  | Score:   50.0 🎯 [TARGET]
14. 브루트포스 알고리즘           | Score:   50.0 🎯 [TARGET]
15. 애드 혹                 | Score:   50.0 🎯 [TARGET]
16. 기하학                  | Score:   50.0
17. 정수론                  | Score:   50.0
18. 시뮬레이션                | Score:   50.0 🎯 [TARGET]
19. 너비 우선 탐색             | Score:   50.0 🎯 [TARGET]
20. 깊이 우선 탐색             | Score:   50.0 🎯 [TARGET]
==================================================

========== [DEBUG] 점수 구성 (Top 5) ==========

1. 그리디 알고리즘 (Total: 80.0)
   ├─ 복습주기: 20.0점
   ├─ 승급임박: 30.0점
   └─ 타겟:     30.0점

2. 트리 (Total: 80.0)
   ├─ 복습주기: 20.0점
   ├─ 승급임박: 30.0점
   └─ 타겟:     30.0점

3. 세그먼트 트리 (Total: 80.0)
   ├─ 복습주기: 20.0점
   ├─ 승급임박: 30.0점
   └─ 타겟:     30.0점

4. 이분 탐색 (Total: 80.0)
   ├─ 복습주기: 20.0점
   ├─ 승급임박: 30.0점
   └─ 타겟:     30.0점

5. 누적 합 (Total: 80.0)
   ├─ 복습주기: 20.0점
   ├─ 승급임박: 30.0점
   └─ 타겟:     30.0점
==================================================


========== [DEBUG] 샘플링된 태그 순서 ==========
총 샘플링 횟수: 12회 (성공: 10, 실패: 2)
1. ✅ 해시를 사용한 집합과 맵
2. ✅ 위상 정렬
3. ✅ 우선순위 큐
4. ✅ 슬라이딩 윈도우
5. ✅ 이분 탐색
6. ✅ 깊이 우선 탐색
7. ❌ 최소 비용 최대 유량
8. ✅ 최대 유량
9. ✅ 이분 탐색
10. ✅ 트리에서의 다이나믹 프로그래밍
11. ❌ 구현
12. ✅ 집합과 맵
==================================================


========== [DEBUG] 최종 추천된 문제 (요청: 10개, 실제: 10개) ==========
1. [2015] 수들의 합 4
   메인 태그: 해시를 사용한 집합과 맵
   전체 태그: ['집합과 맵', '누적 합', '해시를 사용한 집합과 맵', '트리를 사용한 집합과 맵']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
2. [2637] 장난감 조립
   메인 태그: 위상 정렬
   전체 태그: ['다이나믹 프로그래밍', '위상 정렬']
   추천 이유: '위상 정렬' 2문제만 더 풀면 AD 달성!
3. [1655] 가운데를 말해요
   메인 태그: 우선순위 큐
   전체 태그: ['우선순위 큐']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
4. [3078] 좋은 친구
   메인 태그: 슬라이딩 윈도우
   전체 태그: ['집합과 맵', '슬라이딩 윈도우', '큐']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
5. [3151] 합이 0
   메인 태그: 이분 탐색
   전체 태그: ['브루트포스 알고리즘', '정렬', '이분 탐색', '두 포인터']
   추천 이유: '이분 탐색' 3문제만 더 풀면 AD 달성!
6. [11266] 단절점
   메인 태그: 깊이 우선 탐색
   전체 태그: ['깊이 우선 탐색']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
7. [17412] 도시 왕복하기 1
   메인 태그: 최대 유량
   전체 태그: ['최대 유량']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
8. [2539] 모자이크
   메인 태그: 이분 탐색
   전체 태그: ['이분 탐색']
   추천 이유: '이분 탐색' 3문제만 더 풀면 AD 달성!
9. [1135] 뉴스 전하기
   메인 태그: 트리에서의 다이나믹 프로그래밍
   전체 태그: ['다이나믹 프로그래밍', '그리디 알고리즘', '정렬', '트리', '트리에서의 다이나믹 프로그래밍']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
10. [2957] 이진 탐색 트리
   메인 태그: 집합과 맵
   전체 태그: ['집합과 맵', '트리를 사용한 집합과 맵']
   추천 이유: '집합과 맵' 4문제만 더 풀면 MAS 달성!
==================================================

```

### 테스트 결과 (STRICT 10개 추출)
```cmd
[DEBUG TARGET] User has active target: TargetId(value=2)
[DEBUG TARGET] Target tag count: 45
[DEBUG TARGET] Target tags: ['구현', '다이나믹 프로그래밍', '그리디 알고리즘', '문자열', '브루트포스 알고리즘']...
[DEBUG EXCLUDED] 제외된 태그 (1개): ['수학']
[DEBUG EXCLUDED] Exclusion Mode: STRICT

[DEBUG TARGET] Tag '구현' (ID: 2) matches target! Score: 42.0
[DEBUG TARGET] Tag '다이나믹 프로그래밍' (ID: 3) matches target! Score: 30.0
[DEBUG TARGET] Tag '그리디 알고리즘' (ID: 6) matches target! Score: 80.0
[DEBUG TARGET] Tag '문자열' (ID: 7) matches target! Score: 50.0
[DEBUG TARGET] Tag '브루트포스 알고리즘' (ID: 8) matches target! Score: 50.0
[DEBUG TARGET] Tag '애드 혹' (ID: 11) matches target! Score: 50.0
[DEBUG TARGET] Tag '트리' (ID: 13) matches target! Score: 80.0
[DEBUG TARGET] Tag '세그먼트 트리' (ID: 15) matches target! Score: 80.0
[DEBUG TARGET] Tag '이분 탐색' (ID: 16) matches target! Score: 80.0
[DEBUG TARGET] Tag '집합과 맵' (ID: 17) matches target! Score: 72.0
[DEBUG TARGET] Tag '시뮬레이션' (ID: 20) matches target! Score: 50.0
[DEBUG TARGET] Tag '누적 합' (ID: 21) matches target! Score: 80.0
[DEBUG TARGET] Tag '너비 우선 탐색' (ID: 23) matches target! Score: 50.0
[DEBUG TARGET] Tag '최단 경로' (ID: 25) matches target! Score: 80.0
[DEBUG TARGET] Tag '비트마스킹' (ID: 26) matches target! Score: 80.0
[DEBUG TARGET] Tag '깊이 우선 탐색' (ID: 27) matches target! Score: 50.0
[DEBUG TARGET] Tag '해시를 사용한 집합과 맵' (ID: 28) matches target! Score: 50.0
[DEBUG TARGET] Tag '데이크스트라' (ID: 29) matches target! Score: 50.0
[DEBUG TARGET] Tag '백트래킹' (ID: 31) matches target! Score: 50.0
[DEBUG TARGET] Tag '분리 집합' (ID: 32) matches target! Score: 50.0
[DEBUG TARGET] Tag '트리에서의 다이나믹 프로그래밍' (ID: 33) matches target! Score: 50.0
[DEBUG TARGET] Tag '트리를 사용한 집합과 맵' (ID: 34) matches target! Score: 70.0
[DEBUG TARGET] Tag '우선순위 큐' (ID: 35) matches target! Score: 50.0
[DEBUG TARGET] Tag '분할 정복' (ID: 39) matches target! Score: 50.0
[DEBUG TARGET] Tag '두 포인터' (ID: 40) matches target! Score: 80.0
[DEBUG TARGET] Tag '스택' (ID: 41) matches target! Score: 50.0
[DEBUG TARGET] Tag '느리게 갱신되는 세그먼트 트리' (ID: 43) matches target! Score: 50.0
[DEBUG TARGET] Tag '최대 유량' (ID: 45) matches target! Score: 50.0
[DEBUG TARGET] Tag '비트필드를 이용한 다이나믹 프로그래밍' (ID: 46) matches target! Score: 50.0
[DEBUG TARGET] Tag '배낭 문제' (ID: 49) matches target! Score: 50.0
[DEBUG TARGET] Tag '재귀' (ID: 52) matches target! Score: 50.0
[DEBUG TARGET] Tag '임의 정밀도 / 큰 수 연산' (ID: 53) matches target! Score: 50.0
[DEBUG TARGET] Tag '유클리드 호제법' (ID: 54) matches target! Score: 50.0
[DEBUG TARGET] Tag '최소 스패닝 트리' (ID: 55) matches target! Score: 50.0
[DEBUG TARGET] Tag '위상 정렬' (ID: 58) matches target! Score: 80.0
[DEBUG TARGET] Tag '에라토스테네스의 체' (ID: 60) matches target! Score: 50.0
[DEBUG TARGET] Tag '격자 그래프' (ID: 62) matches target! Score: 50.0
[DEBUG TARGET] Tag '최소 공통 조상' (ID: 64) matches target! Score: 50.0
[DEBUG TARGET] Tag '플로이드–워셜' (ID: 68) matches target! Score: 50.0
[DEBUG TARGET] Tag '역추적' (ID: 71) matches target! Score: 80.0
[DEBUG TARGET] Tag '트라이' (ID: 78) matches target! Score: 50.0
[DEBUG TARGET] Tag '덱' (ID: 79) matches target! Score: 50.0
[DEBUG TARGET] Tag '슬라이딩 윈도우' (ID: 86) matches target! Score: 50.0
[DEBUG TARGET] Tag '가장 긴 증가하는 부분 수열 문제' (ID: 94) matches target! Score: 50.0
[DEBUG TARGET] Tag '큐' (ID: 111) matches target! Score: 50.0

========== [DEBUG] 태그 점수 Top 20 ==========
1. 그리디 알고리즘             | Score:   80.0 🎯 [TARGET]
2. 트리                   | Score:   80.0 🎯 [TARGET]
3. 세그먼트 트리              | Score:   80.0 🎯 [TARGET]
4. 이분 탐색                | Score:   80.0 🎯 [TARGET]
5. 누적 합                 | Score:   80.0 🎯 [TARGET]
6. 최단 경로                | Score:   80.0 🎯 [TARGET]
7. 비트마스킹                | Score:   80.0 🎯 [TARGET]
8. 두 포인터                | Score:   80.0 🎯 [TARGET]
9. 위상 정렬                | Score:   80.0 🎯 [TARGET]
10. 역추적                  | Score:   80.0 🎯 [TARGET]
11. 집합과 맵                | Score:   72.0 🎯 [TARGET]
12. 트리를 사용한 집합과 맵        | Score:   70.0 🎯 [TARGET]
13. 문자열                  | Score:   50.0 🎯 [TARGET]
14. 브루트포스 알고리즘           | Score:   50.0 🎯 [TARGET]
15. 애드 혹                 | Score:   50.0 🎯 [TARGET]
16. 기하학                  | Score:   50.0
17. 정수론                  | Score:   50.0
18. 시뮬레이션                | Score:   50.0 🎯 [TARGET]
19. 너비 우선 탐색             | Score:   50.0 🎯 [TARGET]
20. 깊이 우선 탐색             | Score:   50.0 🎯 [TARGET]
==================================================

========== [DEBUG] 점수 구성 (Top 5) ==========

1. 그리디 알고리즘 (Total: 80.0)
   ├─ 복습주기: 20.0점
   ├─ 승급임박: 30.0점
   └─ 타겟:     30.0점

2. 트리 (Total: 80.0)
   ├─ 복습주기: 20.0점
   ├─ 승급임박: 30.0점
   └─ 타겟:     30.0점

3. 세그먼트 트리 (Total: 80.0)
   ├─ 복습주기: 20.0점
   ├─ 승급임박: 30.0점
   └─ 타겟:     30.0점

4. 이분 탐색 (Total: 80.0)
   ├─ 복습주기: 20.0점
   ├─ 승급임박: 30.0점
   └─ 타겟:     30.0점

5. 누적 합 (Total: 80.0)
   ├─ 복습주기: 20.0점
   ├─ 승급임박: 30.0점
   └─ 타겟:     30.0점
==================================================

[DEBUG STRICT] ❌ 문제 1644 제외됨 (excluded 태그 포함): ['수학', '정수론', '두 포인터', '소수 판정', '에라토스테네스의 체']
[DEBUG STRICT] ❌ 문제 1493 제외됨 (excluded 태그 포함): ['수학', '그리디 알고리즘', '분할 정복']

========== [DEBUG] 샘플링된 태그 순서 ==========
총 샘플링 횟수: 13회 (성공: 10, 실패: 3)
1. ❌ 시뮬레이션
2. ✅ 배낭 문제
3. ✅ 우선순위 큐
4. ✅ 역추적
5. ✅ 트리
6. ❌ 두 포인터
7. ✅ 기하학
8. ✅ 애드 혹
9. ✅ 누적 합
10. ❌ 분할 정복
11. ✅ 위상 정렬
12. ✅ 슬라이딩 윈도우
13. ✅ 최소 스패닝 트리
==================================================


========== [DEBUG] 최종 추천된 문제 (요청: 10개, 실제: 10개) ==========
1. [2662] 기업투자
   메인 태그: 배낭 문제
   전체 태그: ['다이나믹 프로그래밍', '배낭 문제', '역추적']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
2. [14427] 수열과 쿼리 15
   메인 태그: 우선순위 큐
   전체 태그: ['세그먼트 트리', '집합과 맵', '우선순위 큐']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
3. [14238] 출근 기록
   메인 태그: 역추적
   전체 태그: ['다이나믹 프로그래밍', '깊이 우선 탐색', '역추적']
   추천 이유: '역추적' 3문제만 더 풀면 AD 달성!
4. [1949] 우수 마을
   메인 태그: 트리
   전체 태그: ['다이나믹 프로그래밍', '트리', '트리에서의 다이나믹 프로그래밍']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
5. [17386] 선분 교차 1
   메인 태그: 기하학
   전체 태그: ['기하학']
   추천 이유: '기하학' 3문제만 더 풀면 AD 달성!
6. [1069] 집으로
   메인 태그: 애드 혹
   전체 태그: ['애드 혹', '기하학']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
7. [16973] 직사각형 탈출
   메인 태그: 누적 합
   전체 태그: ['누적 합', '너비 우선 탐색', '격자 그래프']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
8. [2623] 음악프로그램
   메인 태그: 위상 정렬
   전체 태그: ['위상 정렬']
   추천 이유: '위상 정렬' 태그를 안 푼 지 8일이 지났어요.
9. [13422] 도둑
   메인 태그: 슬라이딩 윈도우
   전체 태그: ['누적 합', '두 포인터', '슬라이딩 윈도우']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
10. [16202] MST 게임
   메인 태그: 최소 스패닝 트리
   전체 태그: ['최소 스패닝 트리']
   추천 이유: '코딩테스트' 목표에 잘 어울리는 문제입니다.
==================================================
```