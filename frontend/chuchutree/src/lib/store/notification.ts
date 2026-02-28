import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface NotificationState {
  hasUnread: boolean;
  setHasUnread: (value: boolean) => void;
}

export const useNotificationStore = create<NotificationState>()(
  devtools(
    immer((set) => ({
      // SSE 연동 전 초기값 false. SSE 연결 후 unread 알림 수신 시 true로 업데이트 예정
      hasUnread: false,

      setHasUnread: (value) =>
        set((state) => {
          state.hasUnread = value;
        }),
    })),
    { name: 'NotificationStore' },
  ),
);
