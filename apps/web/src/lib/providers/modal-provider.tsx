'use client';

import { createContext, useContext, useState, useCallback, useSyncExternalStore, ReactNode } from 'react';
import { createPortal } from 'react-dom';

interface Modal {
  id: string;
  component: ReactNode;
}

interface ModalContextType {
  openModal: (id: string, component: ReactNode) => void;
  closeModal: (id: string) => void;
  closeAll: () => void;
}

const ModalContext = createContext<ModalContextType | undefined>(undefined);

// useSyncExternalStore를 위한 빈 subscribe 함수
const subscribe = () => () => {};

export function ModalProvider({ children }: { children: ReactNode }) {
  const [modals, setModals] = useState<Modal[]>([]);

  // SSR 안전한 mounted 상태 체크
  const mounted = useSyncExternalStore(
    subscribe,
    () => true, // 클라이언트에서는 항상 true
    () => false, // 서버에서는 항상 false
  );

  const openModal = useCallback((id: string, component: ReactNode) => {
    setModals((prev) => {
      // 이미 같은 ID의 모달이 있으면 교체
      const exists = prev.find((modal) => modal.id === id);
      if (exists) {
        return prev.map((modal) => (modal.id === id ? { id, component } : modal));
      }
      return [...prev, { id, component }];
    });
  }, []);

  const closeModal = useCallback((id: string) => {
    setModals((prev) => prev.filter((modal) => modal.id !== id));
  }, []);

  const closeAll = useCallback(() => {
    setModals([]);
  }, []);

  return (
    <ModalContext.Provider value={{ openModal, closeModal, closeAll }}>
      {children}
      {mounted &&
        createPortal(
          <div id="modal-root">
            {modals.map((modal) => (
              <div key={modal.id}>{modal.component}</div>
            ))}
          </div>,
          document.body,
        )}
    </ModalContext.Provider>
  );
}

export function useModal() {
  const context = useContext(ModalContext);
  if (!context) {
    throw new Error('useModal must be used within ModalProvider');
  }
  return context;
}
