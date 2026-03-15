'use client';

import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { noticeKeys } from './notice.keys';
import { BaseNotice } from './notice.types';
import { useNotificationStore } from '@/lib/store/notification';
import { clientLog } from '@/lib/logger';

const MAX_RETRIES = 5;

export const useNoticeSSE = (enabled: boolean) => {
  const queryClient = useQueryClient();
  const { setHasUnread } = useNotificationStore();
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!enabled) return;

    let isCancelled = false;
    let retryTimer: ReturnType<typeof setTimeout>;
    let attempt = 0;

    const scheduleReconnect = () => {
      if (isCancelled) return;
      if (attempt >= MAX_RETRIES) {
        clientLog('[NoticeSSE] 최대 재시도 횟수 초과. 재연결 중단.');
        return;
      }

      const delay = 1000 * Math.pow(2, attempt); // 1s, 2s, 4s, 8s, 16s
      attempt++;
      console.log(`[NoticeSSE] 재연결 시도 ${attempt}/${MAX_RETRIES} — ${delay / 1000}초 후`);

      retryTimer = setTimeout(() => {
        if (!isCancelled) connect();
      }, delay);
    };

    const connect = () => {
      if (isCancelled) return;

      const es = new EventSource('/api/v1/user-accounts/me/notices/stream', { withCredentials: true });
      esRef.current = es;

      es.onopen = () => {
        attempt = 0;
        clientLog('[NoticeSSE] SSE 연결됨');
      };

      es.onmessage = (event) => {
        try {
          const parsed: { eventType: string; data: BaseNotice } = JSON.parse(event.data);

          if (parsed.eventType === 'CONNECTED') {
            clientLog('[NoticeSSE] 서버 연결 확인 (CONNECTED)');
            return;
          }

          if (parsed.eventType === 'NOTICE') {
            const notice = parsed.data;
            console.log(`[NoticeSSE] 새 알림 도착 — noticeId: ${notice.noticeId}, category: ${notice.categoryDetail}`);
            queryClient.setQueryData<BaseNotice[]>(noticeKeys.list(), (prev) =>
              prev ? [notice, ...prev] : [notice],
            );
            if (!notice.isRead) setHasUnread(true);
          }
        } catch {
          // JSON 파싱 실패 무시
        }
      };

      es.onerror = () => {
        clientLog('[NoticeSSE] 연결 오류 발생');
        es.close();
        esRef.current = null;
        scheduleReconnect();
      };
    };

    connect();

    return () => {
      isCancelled = true;
      clearTimeout(retryTimer);
      esRef.current?.close();
      esRef.current = null;
    };
  }, [enabled]);
};
