import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

// 스터디 섹션 진입 후 자동으로 열릴 다이얼로그 신호
export interface PendingStudyInviteAction {
  studyId: number;
  tab: 'received';
}

interface NotificationState {
  hasUnread: boolean;
  setHasUnread: (value: boolean) => void;
  pendingStudyInviteAction: PendingStudyInviteAction | null;
  setPendingStudyInviteAction: (action: PendingStudyInviteAction | null) => void;
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

      pendingStudyInviteAction: null,

      setPendingStudyInviteAction: (action) =>
        set((state) => {
          state.pendingStudyInviteAction = action;
        }),
    })),
    { name: 'NotificationStore' },
  ),
);
