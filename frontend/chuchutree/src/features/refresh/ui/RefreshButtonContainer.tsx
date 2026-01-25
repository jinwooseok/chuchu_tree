import { DndContext, DragEndEvent, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { useState, useEffect } from 'react';
import { useRefreshButtonStore } from '@/lib/store/refreshButton';
import DraggableRefreshButton from './DraggableRefreshButton';
import RefreshButtonDropZone from './RefreshButtonDropZone';

export function RefreshButtonContainer() {
  const { isRefreshButtonVisible, hideRefreshButton } = useRefreshButtonStore();
  const [isDragging, setIsDragging] = useState(false);
  const [showDroppedMessage, setShowDroppedMessage] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px 이동 후 드래그 시작
      },
    }),
  );

  const handleDragStart = () => {
    setIsDragging(true);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    setIsDragging(false);

    const { active, over } = event;

    // RefreshButton을 DropZone에 드롭한 경우
    if (active.id === 'refresh-button' && over?.id === 'refresh-button-drop-zone') {
      hideRefreshButton();
      setShowDroppedMessage(true);
    }
  };

  // 드롭 메시지 2초 후 숨김
  useEffect(() => {
    if (showDroppedMessage) {
      const timer = setTimeout(() => {
        setShowDroppedMessage(false);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [showDroppedMessage]);

  return (
    <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      {isRefreshButtonVisible && (
        <div className="absolute right-4 bottom-4 z-10 md:right-16 md:bottom-16">
          <DraggableRefreshButton />
        </div>
      )}
      <RefreshButtonDropZone isDragging={isDragging} showDroppedMessage={showDroppedMessage} />
    </DndContext>
  );
}
