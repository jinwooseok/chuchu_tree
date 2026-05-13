import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

interface StudyCalendarStore {
  selectedDate: Date | null;
  bigCalendarDate: Date | null;
  setSelectedDate: (date: Date) => void;
  setBigCalendarDate: (date: Date) => void;
}

export const useStudyCalendarStore = create<StudyCalendarStore>()(
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
    { name: 'StudyCalendarStore' },
  ),
);
