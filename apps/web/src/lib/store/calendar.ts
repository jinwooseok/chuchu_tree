import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface CalendarStore {
  selectedDate: Date | null;
  bigCalendarDate: Date | null;
  setSelectedDate: (date: Date) => void;
  setBigCalendarDate: (date: Date) => void;
}

export const useCalendarStore = create<CalendarStore>()(
  devtools(
    immer((set) => ({
      selectedDate: new Date(),
      bigCalendarDate: new Date(),

      setSelectedDate: (date: Date) => {
        set((state) => {
          state.selectedDate = date;
        });
      },

      setBigCalendarDate: (date: Date) => {
        set((state) => {
          state.bigCalendarDate = date;
        });
      },
    })),
    { name: 'CalendarStore' },
  ),
);
