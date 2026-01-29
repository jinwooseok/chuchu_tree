/**
 * 온보딩 관련 유틸리티 함수들
 */

export interface ElementPosition {
  x: number;
  y: number;
  width: number;
  height: number;
}

/**
 * 요소의 위치와 크기 계산
 */
export function getElementPosition(selector: string): ElementPosition | null {
  const element = document.querySelector(selector);
  if (!element) return null;

  const rect = element.getBoundingClientRect();
  return {
    x: rect.left,
    y: rect.top,
    width: rect.width,
    height: rect.height,
  };
}

/**
 * 요소가 렌더링될 때까지 대기 (최대 timeout ms)
 */
export function waitForElement(selector: string, timeout = 5000): Promise<Element> {
  console.log('렌더링 대기');

  return new Promise((resolve, reject) => {
    const element = document.querySelector(selector);
    if (element) {
      resolve(element);
      return;
    }

    let timer: NodeJS.Timeout | null = null;

    const observer = new MutationObserver(() => {
      const element = document.querySelector(selector);
      if (element) {
        observer.disconnect();
        if (timer) clearTimeout(timer);
        resolve(element);
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    timer = setTimeout(() => {
      observer.disconnect();
      reject(new Error(`Element ${selector} not found within ${timeout}ms`));
    }, timeout);
  });
}

/**
 * 요소가 화면에 보이도록 스크롤
 */
export function scrollToElement(selector: string): void {
  const element = document.querySelector(selector);
  if (!element) return;

  element.scrollIntoView({
    behavior: 'smooth',
    block: 'center',
    inline: 'center',
  });
}

/**
 * Tooltip 위치 계산 (화면 밖으로 나가지 않도록 조정)
 */
export function calculateTooltipPosition(
  targetPosition: ElementPosition,
  placement: 'top' | 'bottom' | 'left' | 'right',
  tooltipWidth = 300,
  tooltipHeight = 150,
  offset = 16,
): { x: number; y: number; adjustedPlacement: 'top' | 'bottom' | 'left' | 'right' } {
  const viewport = {
    width: window.innerWidth,
    height: window.innerHeight,
  };

  let x = 0;
  let y = 0;
  let adjustedPlacement = placement;

  // 기본 위치 계산
  switch (placement) {
    case 'top':
      x = targetPosition.x + targetPosition.width / 2 - tooltipWidth / 2;
      y = targetPosition.y - tooltipHeight - offset;
      // 위쪽에 공간이 없으면 아래로
      if (y < 0) {
        adjustedPlacement = 'bottom';
        y = targetPosition.y + targetPosition.height + offset;
      }
      break;
    case 'bottom':
      x = targetPosition.x + targetPosition.width / 2 - tooltipWidth / 2;
      y = targetPosition.y + targetPosition.height + offset;
      // 아래쪽에 공간이 없으면 위로
      if (y + tooltipHeight > viewport.height) {
        adjustedPlacement = 'top';
        y = targetPosition.y - tooltipHeight - offset;
      }
      break;
    case 'left':
      x = targetPosition.x - tooltipWidth - offset;
      y = targetPosition.y + targetPosition.height / 2 - tooltipHeight / 2;
      // 왼쪽에 공간이 없으면 오른쪽으로
      if (x < 0) {
        adjustedPlacement = 'right';
        x = targetPosition.x + targetPosition.width + offset;
      }
      break;
    case 'right':
      x = targetPosition.x + targetPosition.width + offset;
      y = targetPosition.y + targetPosition.height / 2 - tooltipHeight / 2;
      // 오른쪽에 공간이 없으면 왼쪽으로
      if (x + tooltipWidth > viewport.width) {
        adjustedPlacement = 'left';
        x = targetPosition.x - tooltipWidth - offset;
      }
      break;
  }

  // 최종 위치 보정 (화면 안에 들어오도록)
  x = Math.max(8, Math.min(x, viewport.width - tooltipWidth - 8));
  y = Math.max(8, Math.min(y, viewport.height - tooltipHeight - 8));

  return { x, y, adjustedPlacement };
}
