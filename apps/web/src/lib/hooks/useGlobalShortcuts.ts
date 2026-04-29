'use client';

import { useEffect, useCallback } from 'react';

export interface ShortcutConfig {
  key: string; // event.key 값 (예: 'c', '1', ',')
  code?: string; // event.code 값 (예: 'KeyC', 'Digit1', 'Comma') - 더 정확함
  shift?: boolean;
  ctrl?: boolean;
  alt?: boolean;
  meta?: boolean;
  action: () => void;
  preventDefault?: boolean;
  description?: string;
}

export interface UseGlobalShortcutsOptions {
  shortcuts: ShortcutConfig[];
  enabled?: boolean;
  ignoreWhenInputFocused?: boolean;
}

/**
 * 입력 요소에 포커스되어 있는지 확인
 */
const isInputFocused = (): boolean => {
  const activeElement = document.activeElement;
  if (!activeElement) return false;

  const tagName = activeElement.tagName;
  const isContentEditable = activeElement.getAttribute('contenteditable') === 'true';

  return tagName === 'INPUT' || tagName === 'TEXTAREA' || isContentEditable;
};

/**
 * 단축키가 현재 이벤트와 일치하는지 확인
 */
const matchesShortcut = (event: KeyboardEvent, config: ShortcutConfig): boolean => {
  // code가 있으면 code로 비교 (더 정확), 없으면 key로 비교
  let keyMatches = false;
  if (config.code) {
    keyMatches = event.code === config.code;
  } else {
    keyMatches = event.key.toLowerCase() === config.key.toLowerCase();
  }

  // 수정자 키 비교
  const shiftMatches = !!config.shift === event.shiftKey;
  const ctrlMatches = !!config.ctrl === event.ctrlKey;
  const altMatches = !!config.alt === event.altKey;
  const metaMatches = !!config.meta === event.metaKey;

  return keyMatches && shiftMatches && ctrlMatches && altMatches && metaMatches;
};

/**
 * 전역 단축키 관리 훅
 *
 * @example
 * ```tsx
 * useGlobalShortcuts({
 *   shortcuts: [
 *     {
 *       key: 'b',
 *       shift: true,
 *       action: () => toggleSidebar(),
 *       preventDefault: true,
 *       description: '사이드바 토글'
 *     }
 *   ]
 * });
 * ```
 */
export function useGlobalShortcuts(options: UseGlobalShortcutsOptions): void {
  const { shortcuts, enabled = true, ignoreWhenInputFocused = true } = options;

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // 비활성화 상태면 무시
      if (!enabled) return;

      // input 포커스 시 무시 (옵션이 true일 때만)
      if (ignoreWhenInputFocused && isInputFocused()) return;

      // 등록된 단축키 중 일치하는 것 찾기
      for (const shortcut of shortcuts) {
        if (matchesShortcut(event, shortcut)) {
          // preventDefault 처리
          if (shortcut.preventDefault !== false) {
            event.preventDefault();
          }

          // 액션 실행
          shortcut.action();

          // 첫 번째 일치하는 단축키만 실행
          break;
        }
      }
    },
    [enabled, ignoreWhenInputFocused, shortcuts],
  );

  useEffect(() => {
    if (!enabled) return;

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [enabled, handleKeyDown]);
}
