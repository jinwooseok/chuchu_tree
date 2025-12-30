'use client';

import { useLayoutStore } from '@/lib/store/layout';
import CalendarSidebar from './calendar-sidebar';
import TagSidebar from './tag-sidebar';

export default function InfoSidebar() {
  const { centerSection } = useLayoutStore();

  return <aside className="animate-in slide-in-from-left bg-card w-1/3 border-r duration-300 md:w-1/4 xl:w-1/5">{centerSection === 'calendar' ? <CalendarSidebar /> : <TagSidebar />}</aside>;
}
