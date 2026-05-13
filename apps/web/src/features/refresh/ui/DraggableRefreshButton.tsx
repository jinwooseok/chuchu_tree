import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import RefreshButton from './RefreshButton';

export default function DraggableRefreshButton() {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: 'refresh-button',
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    opacity: isDragging ? 0.5 : 1,
    cursor: isDragging ? 'grabbing' : 'grab',
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <RefreshButton />
    </div>
  );
}
