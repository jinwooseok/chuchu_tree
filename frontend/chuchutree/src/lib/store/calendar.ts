import { create } from 'zustand';
import { combine, devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

type State = {
  selectedDate: Date | null;
  bigCalendarDate: Date | null;
};

const initialState: State = {
  selectedDate: new Date(),
  bigCalendarDate: new Date(),
};

const calendarStoreInternal = create(
  devtools(
    immer(
      combine(initialState, (set) => ({
        actions: {
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
        },
      })),
    ),
    { name: 'CalendarStore' },
  ),
);

// Selectors
export const useCalendarStore = () => {
  const selectedDate = calendarStoreInternal((s) => s.selectedDate);
  const bigCalendarDate = calendarStoreInternal((s) => s.bigCalendarDate);
  const setSelectedDate = calendarStoreInternal((s) => s.actions.setSelectedDate);
  const setBigCalendarDate = calendarStoreInternal((s) => s.actions.setBigCalendarDate);

  return {
    selectedDate,
    bigCalendarDate,
    actions: {
      setSelectedDate,
      setBigCalendarDate,
    },
  };
};

export const useSetSelectedDate = () => {
  const setSelectedDate = calendarStoreInternal((s) => s.actions.setSelectedDate);
  return setSelectedDate;
};
