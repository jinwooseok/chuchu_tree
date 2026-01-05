import { create } from 'zustand';
import { combine, devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { User } from '@/entities/user';

type State = {
  user: User | null;
  isInitialized: boolean;
};

const initialState: State = {
  user: null,
  isInitialized: false,
};

const useUserStore = create(
  devtools(
    immer(
      combine(initialState, (set) => ({
        actions: {
          setUser: (user: User) => {
            set((state) => {
              state.user = user;
              state.isInitialized = true;
            });
          },
          clearUser: () => {
            set((state) => {
              state.user = null;
              state.isInitialized = false;
            });
          },
          updateUser: (updates: Partial<User>) => {
            set((state) => {
              if (state.user) {
                Object.assign(state.user, updates);
              }
            });
          },
        },
      })),
    ),
    { name: 'UserStore' },
  ),
);

// Selectors
export const useUser = () => {
  const store = useUserStore();
  return store as typeof store & State;
};

export const useSetUser = () => {
  const setUser = useUserStore((s) => s.actions.setUser);
  return setUser;
};

export const useClearUser = () => {
  const clearUser = useUserStore((s) => s.actions.clearUser);
  return clearUser;
};

export const useUpdateUser = () => {
  const updateUser = useUserStore((s) => s.actions.updateUser);
  return updateUser;
};

export const useIsAuthenticated = () => {
  const isInitialized = useUserStore((s) => s.isInitialized);
  const user = useUserStore((s) => s.user);
  return isInitialized && user !== null;
};
