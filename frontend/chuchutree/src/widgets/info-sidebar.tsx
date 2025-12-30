'use client';

import { useLayoutStore } from '@/lib/store/layout';
import CalendarSidebar from './calendar-sidebar';
import TagSidebar from './tag-sidebar';

export default function InfoSidebar() {
  const { centerSection } = useLayoutStore();

  return (
    <aside className="w-1/5 border-r bg-card">
      {centerSection === 'calendar' ? <CalendarSidebar /> : <TagSidebar />}
    </aside>
  );
}
