import { create } from 'zustand';
import { combine, devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

type State = {
  num: number;
};

const initialState = {
  num: 0,
} as State;

const useCountStore = create(
  devtools(
    immer(
      combine(initialState, (set) => ({
        actions: {
          plus: (c: number) => {
            set((state) => {
              state.num += c;
            });
          },
          minus: () => {
            set((state) => {
              state.num -= 1;
            });
          },
        },
      })),
    ),
    { name: 'ZustandTestCountStore' },
  ),
);

export const usePlusCount = () => {
  const plus = useCountStore((s) => s.actions.plus);
  return plus;
};
export const useMinusCount = () => {
  const minus = useCountStore((s) => s.actions.minus);
  return minus;
};
export const useCount = () => {
  const store = useCountStore();
  return store as typeof store & State;
};
