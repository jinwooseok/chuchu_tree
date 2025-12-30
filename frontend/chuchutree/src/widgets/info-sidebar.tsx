'use client';

import { useLayoutStore } from '@/lib/store/layout';
import CalendarSidebar from './calendar-sidebar';
import TagSidebar from './tag-sidebar';

export default function InfoSidebar() {
  const { centerSection } = useLayoutStore();

  return (
    <aside className="w-1/5 animate-in slide-in-from-left border-r bg-card duration-300">
      {centerSection === 'calendar' ? <CalendarSidebar /> : <TagSidebar />}
    </aside>
  );
}
