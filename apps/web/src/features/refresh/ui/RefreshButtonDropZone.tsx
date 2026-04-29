import { useDroppable } from '@dnd-kit/core';
import { Archive } from 'lucide-react';
import { useSyncExternalStore } from 'react';

interface RefreshButtonDropZoneProps {
  isDragging: boolean;
  showDroppedMessage: boolean;
}

// useSyncExternalStore를 위한 빈 subscribe 함수
const subscribe = () => () => {};

export default function RefreshButtonDropZone({ isDragging, showDroppedMessage }: RefreshButtonDropZoneProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: 'refresh-button-drop-zone',
  });

  // SSR 안전한 mounted 상태 체크
  const mounted = useSyncExternalStore(
    subscribe,
    () => true, // 클라이언트에서는 항상 true
    () => false, // 서버에서는 항상 false
  );

  // SSR 및 초기 hydration 중에는 렌더링하지 않음
  if (!mounted) {
    return null;
  }

  // 드래그 중이 아니고 메시지도 표시 안함 = 완전히 숨김
  if (!isDragging && !showDroppedMessage) {
    return null;
  }

  return (
    <div
      ref={setNodeRef}
      className={`border-only-black bg-antiground absolute right-4 bottom-4 z-10 flex h-10 w-40 items-center justify-center gap-2 rounded-lg border-2 transition-all duration-300 md:right-16 md:bottom-16 ${
        isOver ? 'shadow-[4px_4px_0_0_var(--only-black)]' : ''
      }`}
    >
      {showDroppedMessage ? (
        <div className="flex w-full items-center justify-center gap-2">
          <Archive className="text-only-black h-5 w-5" />
          <div className="flex flex-col items-start">
            <span className="text-only-black text-xs font-semibold">사이드바에서</span>
            <span className="text-only-black text-xs font-semibold">다시 꺼낼 수 있습니다!</span>
          </div>
        </div>
      ) : (
        <div className="flex w-full items-center justify-center gap-2">
          <Archive className="text-only-black h-5 w-5" />
          <div className="flex flex-col items-start">
            <span className="text-only-black text-xs font-semibold">버튼을 사이드바에</span>
            <span className="text-only-black text-xs font-semibold">보관하세요!</span>
          </div>
        </div>
      )}
    </div>
  );
}
