/**
 * 티어바 유틸리티 함수 테스트
 */

import { User } from '@/entities/user';
import { getTierDetail } from './utils';

describe('getTierDetail', () => {
  it('현재 티어 정보를 반환한다', () => {
    const user: User = {
      userAccount: {
        userAccountId: 1,
        profileImageUrl: null,
        target: {
          targetId: 1,
          targetCode: 'DAILY',
          targetDisplayName: '데일리',
        },
        registeredAt: '2024-01-01',
      },
      bjAccount: {
        bjAccountId: 'testuser',
        stat: {
          tierId: 10, // Silver I
          tierName: 'Silver',
          longestStreak: 10,
          rating: 650,
          class: 1,
          tierStartDate: '2024-01-01',
        },
        streaks: [],
        registeredAt: '2024-01-01',
      },
      linkedAt: '2024-01-01',
    };

    const result = getTierDetail(user);

    expect(result.rowTierId).toBe(10);
    expect(result.rowRating).toBe(650);
    expect(result.tierName).toBe('Silver');
    expect(result.tierNum).toBe('I');
  });

  it('다음 티어 정보를 계산한다', () => {
    const user: User = {
      userAccount: {
        userAccountId: 1,
        profileImageUrl: null,
        target: {
          targetId: 1,
          targetCode: 'DAILY',
          targetDisplayName: '데일리',
        },
        registeredAt: '2024-01-01',
      },
      bjAccount: {
        bjAccountId: 'testuser',
        stat: {
          tierId: 10, // Silver I
          tierName: 'Silver',
          longestStreak: 10,
          rating: 650,
          class: 1,
          tierStartDate: '2024-01-01',
        },
        streaks: [],
        registeredAt: '2024-01-01',
      },
      linkedAt: '2024-01-01',
    };

    const result = getTierDetail(user);

    expect(result.rowNextTierId).toBe(11); // Gold V
    expect(result.nextName).toBe('Gold');
    expect(result.nextNum).toBe('V');
  });

  it('다음 티어까지 남은 레이팅 점수를 계산한다', () => {
    const user: User = {
      userAccount: {
        userAccountId: 1,
        profileImageUrl: null,
        target: {
          targetId: 1,
          targetCode: 'DAILY',
          targetDisplayName: '데일리',
        },
        registeredAt: '2024-01-01',
      },
      bjAccount: {
        bjAccountId: 'testuser',
        stat: {
          tierId: 10, // Silver I (650)
          tierName: 'Silver',
          longestStreak: 10,
          rating: 650,
          class: 1,
          tierStartDate: '2024-01-01',
        },
        streaks: [],
        registeredAt: '2024-01-01',
      },
      linkedAt: '2024-01-01',
    };

    const result = getTierDetail(user);

    // Gold V는 800, Silver I는 650
    // 남은 점수: 800 - 650 = 150
    expect(result.rowRatingToNext).toBe(150);
    // 총 필요 점수: 800 - 650 = 150
    expect(result.rowTotalRatingForNextTier).toBe(150);
  });

  it('티어 비율을 계산한다', () => {
    const user: User = {
      userAccount: {
        userAccountId: 1,
        profileImageUrl: null,
        target: {
          targetId: 1,
          targetCode: 'DAILY',
          targetDisplayName: '데일리',
        },
        registeredAt: '2024-01-01',
      },
      bjAccount: {
        bjAccountId: 'testuser',
        stat: {
          tierId: 10, // Silver I (650)
          tierName: 'Silver',
          longestStreak: 10,
          rating: 725, // 중간 지점
          class: 1,
          tierStartDate: '2024-01-01',
        },
        streaks: [],
        registeredAt: '2024-01-01',
      },
      linkedAt: '2024-01-01',
    };

    const result = getTierDetail(user);

    // 현재: 725, 다음 티어: 800, 현재 티어 시작: 650
    // 총 필요: 150, 남은: 75, 진행: 75
    // 비율: (75 / 150) * 100 = 50%
    expect(result.rowTierRatio).toBe(50);
  });

  it('마스터 티어 (최고 티어)를 처리한다', () => {
    const user: User = {
      userAccount: {
        userAccountId: 1,
        profileImageUrl: null,
        target: {
          targetId: 1,
          targetCode: 'DAILY',
          targetDisplayName: '데일리',
        },
        registeredAt: '2024-01-01',
      },
      bjAccount: {
        bjAccountId: 'testuser',
        stat: {
          tierId: 31, // Master
          tierName: 'Master',
          longestStreak: 10,
          rating: 3000,
          class: 1,
          tierStartDate: '2024-01-01',
        },
        streaks: [],
        registeredAt: '2024-01-01',
      },
      linkedAt: '2024-01-01',
    };

    const result = getTierDetail(user);

    // 마스터는 다음 티어가 없으므로 자기 자신
    expect(result.rowNextTierId).toBe(31);
    expect(result.nextName).toBe('Master');
    expect(result.tierName).toBe('Master');
  });

  it('Bronze 티어를 처리한다', () => {
    const user: User = {
      userAccount: {
        userAccountId: 1,
        profileImageUrl: null,
        target: {
          targetId: 1,
          targetCode: 'BEGINNER',
          targetDisplayName: '초보자',
        },
        registeredAt: '2024-01-01',
      },
      bjAccount: {
        bjAccountId: 'testuser',
        stat: {
          tierId: 3, // Bronze III
          tierName: 'Bronze',
          longestStreak: 5,
          rating: 90,
          class: 0,
          tierStartDate: '2024-01-01',
        },
        streaks: [],
        registeredAt: '2024-01-01',
      },
      linkedAt: '2024-01-01',
    };

    const result = getTierDetail(user);

    expect(result.rowTierId).toBe(3);
    expect(result.tierName).toBe('Bronze');
    expect(result.tierNum).toBe('III');
    expect(result.rowNextTierId).toBe(4); // Bronze II
  });

  it('Unrated 티어를 처리한다', () => {
    const user: User = {
      userAccount: {
        userAccountId: 1,
        profileImageUrl: null,
        target: {
          targetId: 1,
          targetCode: 'BEGINNER',
          targetDisplayName: '초보자',
        },
        registeredAt: '2024-01-01',
      },
      bjAccount: {
        bjAccountId: 'testuser',
        stat: {
          tierId: 0, // Unrated
          tierName: 'Unrated',
          longestStreak: 0,
          rating: 0,
          class: 0,
          tierStartDate: '2024-01-01',
        },
        streaks: [],
        registeredAt: '2024-01-01',
      },
      linkedAt: '2024-01-01',
    };

    const result = getTierDetail(user);

    expect(result.rowTierId).toBe(0);
    expect(result.tierName).toBe('Unrated');
    expect(result.rowNextTierId).toBe(1); // Bronze V
    expect(result.nextName).toBe('Bronze');
  });

  it('Gold 티어에서 레이팅이 높을 때를 처리한다', () => {
    const user: User = {
      userAccount: {
        userAccountId: 1,
        profileImageUrl: null,
        target: {
          targetId: 1,
          targetCode: 'CODING_TEST',
          targetDisplayName: '코딩테스트',
        },
        registeredAt: '2024-01-01',
      },
      bjAccount: {
        bjAccountId: 'testuser',
        stat: {
          tierId: 15, // Gold I
          tierName: 'Gold',
          longestStreak: 20,
          rating: 1500,
          class: 2,
          tierStartDate: '2024-01-01',
        },
        streaks: [],
        registeredAt: '2024-01-01',
      },
      linkedAt: '2024-01-01',
    };

    const result = getTierDetail(user);

    expect(result.rowTierId).toBe(15);
    expect(result.tierName).toBe('Gold');
    expect(result.tierNum).toBe('I');
    expect(result.rowNextTierId).toBe(16); // Platinum V
    expect(result.nextName).toBe('Platinum');
    // Gold I: 1400, Platinum V: 1600
    // 남은 점수: 1600 - 1500 = 100
    expect(result.rowRatingToNext).toBe(100);
    // 총 필요: 1600 - 1400 = 200
    expect(result.rowTotalRatingForNextTier).toBe(200);
    // 진행률: ((200 - 100) / 200) * 100 = 50%
    expect(result.rowTierRatio).toBe(50);
  });

  it('티어 승급 직전을 처리한다', () => {
    const user: User = {
      userAccount: {
        userAccountId: 1,
        profileImageUrl: null,
        target: {
          targetId: 1,
          targetCode: 'DAILY',
          targetDisplayName: '데일리',
        },
        registeredAt: '2024-01-01',
      },
      bjAccount: {
        bjAccountId: 'testuser',
        stat: {
          tierId: 10, // Silver I
          tierName: 'Silver',
          longestStreak: 15,
          rating: 799, // Gold V 직전 (800)
          class: 1,
          tierStartDate: '2024-01-01',
        },
        streaks: [],
        registeredAt: '2024-01-01',
      },
      linkedAt: '2024-01-01',
    };

    const result = getTierDetail(user);

    // 남은 점수: 1
    expect(result.rowRatingToNext).toBe(1);
    // 총 필요: 150
    expect(result.rowTotalRatingForNextTier).toBe(150);
    // 진행률: ((150 - 1) / 150) * 100 ≈ 99.33%
    expect(result.rowTierRatio).toBeCloseTo(99.33, 1);
  });
});
