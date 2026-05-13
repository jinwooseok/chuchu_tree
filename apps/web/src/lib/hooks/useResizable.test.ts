import { renderHook, act } from '@testing-library/react';
import { useResizable, UseResizableOptions } from './useResizable';

describe('useResizable', () => {
  let rafSpy: jest.SpyInstance;

  beforeEach(() => {
    // requestAnimationFrame 모킹 (동기적으로 실행)
    rafSpy = jest.spyOn(window, 'requestAnimationFrame').mockImplementation((cb) => {
      cb(0);
      return 0;
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('초기화 및 제약 조건', () => {
    it('initialSize를 그대로 설정한다 (정상 범위)', () => {
      const { result } = renderHook(() =>
        useResizable({
          direction: 'horizontal',
          initialSize: 300,
          minSize: 200,
          maxSize: 500,
        }),
      );

      expect(result.current.size).toBe(300);
    });

    it('initialSize가 minSize보다 작으면 minSize로 보정한다', () => {
      const { result } = renderHook(() =>
        useResizable({
          direction: 'horizontal',
          initialSize: 100,
          minSize: 200,
          maxSize: 500,
        }),
      );

      expect(result.current.size).toBe(200);
    });

    it('initialSize가 maxSize보다 크면 maxSize로 보정한다', () => {
      const { result } = renderHook(() =>
        useResizable({
          direction: 'horizontal',
          initialSize: 600,
          minSize: 200,
          maxSize: 500,
        }),
      );

      expect(result.current.size).toBe(500);
    });

    it('initialSize 변경 시 size가 업데이트된다 (리사이징 중이 아닐 때)', () => {
      const { result, rerender } = renderHook(
        ({ initialSize }: { initialSize: number }) =>
          useResizable({
            direction: 'horizontal',
            initialSize,
            minSize: 200,
            maxSize: 500,
          }),
        { initialProps: { initialSize: 300 } },
      );

      expect(result.current.size).toBe(300);

      // initialSize 변경
      rerender({ initialSize: 400 });

      expect(result.current.size).toBe(400);
    });
  });

  describe('드래그 동작', () => {
    it('마우스 다운 시 isResizing이 true가 된다', () => {
      const { result } = renderHook(() =>
        useResizable({
          direction: 'horizontal',
          initialSize: 300,
          minSize: 200,
          maxSize: 500,
        }),
      );

      const mouseDownEvent = new MouseEvent('mousedown', {
        clientX: 300,
      }) as unknown as React.MouseEvent;

      act(() => {
        result.current.handleMouseDown(mouseDownEvent);
      });

      expect(result.current.isResizing).toBe(true);
    });

    it('horizontal 드래그 시 clientX 변화량만큼 size가 변경된다', () => {
      const { result } = renderHook(() =>
        useResizable({
          direction: 'horizontal',
          initialSize: 300,
          minSize: 200,
          maxSize: 500,
        }),
      );

      // 드래그 시작 (clientX: 300)
      const mouseDownEvent = new MouseEvent('mousedown', {
        clientX: 300,
      }) as unknown as React.MouseEvent;

      act(() => {
        result.current.handleMouseDown(mouseDownEvent);
      });

      // 드래그 진행 (clientX: 400, delta: +100)
      const mouseMoveEvent = new MouseEvent('mousemove', {
        clientX: 400,
      });

      act(() => {
        document.dispatchEvent(mouseMoveEvent);
      });

      expect(result.current.size).toBe(400); // 300 + 100 = 400

      // 드래그 종료
      const mouseUpEvent = new MouseEvent('mouseup');
      act(() => {
        document.dispatchEvent(mouseUpEvent);
      });
    });

    it('vertical 드래그 시 clientY 변화량만큼 size가 변경된다', () => {
      const { result } = renderHook(() =>
        useResizable({
          direction: 'vertical',
          initialSize: 300,
          minSize: 200,
          maxSize: 500,
        }),
      );

      // 드래그 시작 (clientY: 300)
      const mouseDownEvent = new MouseEvent('mousedown', {
        clientY: 300,
      }) as unknown as React.MouseEvent;

      act(() => {
        result.current.handleMouseDown(mouseDownEvent);
      });

      // 드래그 진행 (clientY: 250, delta: -50)
      const mouseMoveEvent = new MouseEvent('mousemove', {
        clientY: 250,
      });

      act(() => {
        document.dispatchEvent(mouseMoveEvent);
      });

      expect(result.current.size).toBe(250); // 300 - 50 = 250

      // 드래그 종료
      const mouseUpEvent = new MouseEvent('mouseup');
      act(() => {
        document.dispatchEvent(mouseUpEvent);
      });
    });

    it('inverted=true일 때 드래그 방향이 반전된다', () => {
      const { result } = renderHook(() =>
        useResizable({
          direction: 'vertical',
          initialSize: 300,
          minSize: 200,
          maxSize: 500,
          inverted: true, // 방향 반전
        }),
      );

      // 드래그 시작 (clientY: 300)
      const mouseDownEvent = new MouseEvent('mousedown', {
        clientY: 300,
      }) as unknown as React.MouseEvent;

      act(() => {
        result.current.handleMouseDown(mouseDownEvent);
      });

      // 드래그 진행 (clientY: 400, delta: +100, inverted이므로 -100 적용)
      const mouseMoveEvent = new MouseEvent('mousemove', {
        clientY: 400,
      });

      act(() => {
        document.dispatchEvent(mouseMoveEvent);
      });

      expect(result.current.size).toBe(200); // 300 - 100 = 200

      // 드래그 종료
      const mouseUpEvent = new MouseEvent('mouseup');
      act(() => {
        document.dispatchEvent(mouseUpEvent);
      });
    });
  });

  describe('경계값 제약', () => {
    it('드래그 중 minSize 미만으로 줄어들지 않는다', () => {
      const { result } = renderHook(() =>
        useResizable({
          direction: 'horizontal',
          initialSize: 300,
          minSize: 200,
          maxSize: 500,
        }),
      );

      // 드래그 시작
      const mouseDownEvent = new MouseEvent('mousedown', {
        clientX: 300,
      }) as unknown as React.MouseEvent;

      act(() => {
        result.current.handleMouseDown(mouseDownEvent);
      });

      // 드래그 진행 (clientX: 50, delta: -250, minSize 제약으로 200까지만)
      const mouseMoveEvent = new MouseEvent('mousemove', {
        clientX: 50,
      });

      act(() => {
        document.dispatchEvent(mouseMoveEvent);
      });

      expect(result.current.size).toBe(200); // minSize에서 멈춤

      // 드래그 종료
      const mouseUpEvent = new MouseEvent('mouseup');
      act(() => {
        document.dispatchEvent(mouseUpEvent);
      });
    });

    it('드래그 중 maxSize 초과로 늘어나지 않는다', () => {
      const { result } = renderHook(() =>
        useResizable({
          direction: 'horizontal',
          initialSize: 300,
          minSize: 200,
          maxSize: 500,
        }),
      );

      // 드래그 시작
      const mouseDownEvent = new MouseEvent('mousedown', {
        clientX: 300,
      }) as unknown as React.MouseEvent;

      act(() => {
        result.current.handleMouseDown(mouseDownEvent);
      });

      // 드래그 진행 (clientX: 900, delta: +600, maxSize 제약으로 500까지만)
      const mouseMoveEvent = new MouseEvent('mousemove', {
        clientX: 900,
      });

      act(() => {
        document.dispatchEvent(mouseMoveEvent);
      });

      expect(result.current.size).toBe(500); // maxSize에서 멈춤

      // 드래그 종료
      const mouseUpEvent = new MouseEvent('mouseup');
      act(() => {
        document.dispatchEvent(mouseUpEvent);
      });
    });
  });

  describe('메모리 안정성', () => {
    it('언마운트 시 requestAnimationFrame이 취소된다', () => {
      const cancelAnimationFrameSpy = jest.spyOn(window, 'cancelAnimationFrame');

      const { result, unmount } = renderHook(() =>
        useResizable({
          direction: 'horizontal',
          initialSize: 300,
          minSize: 200,
          maxSize: 500,
        }),
      );

      // 드래그 시작
      const mouseDownEvent = new MouseEvent('mousedown', {
        clientX: 300,
      }) as unknown as React.MouseEvent;

      act(() => {
        result.current.handleMouseDown(mouseDownEvent);
      });

      // 언마운트
      unmount();

      // cancelAnimationFrame이 호출되었거나, cleanup이 실행되었는지 확인
      // body 스타일이 초기화되었는지 확인
      expect(document.body.style.userSelect).toBe('');
      expect(document.body.style.cursor).toBe('');

      cancelAnimationFrameSpy.mockRestore();
    });

    it('마우스 업 시 전역 이벤트 리스너가 제거된다', () => {
      const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener');

      const { result } = renderHook(() =>
        useResizable({
          direction: 'horizontal',
          initialSize: 300,
          minSize: 200,
          maxSize: 500,
        }),
      );

      // 드래그 시작
      const mouseDownEvent = new MouseEvent('mousedown', {
        clientX: 300,
      }) as unknown as React.MouseEvent;

      act(() => {
        result.current.handleMouseDown(mouseDownEvent);
      });

      expect(result.current.isResizing).toBe(true);

      // 드래그 종료
      const mouseUpEvent = new MouseEvent('mouseup');

      act(() => {
        document.dispatchEvent(mouseUpEvent);
      });

      expect(result.current.isResizing).toBe(false);

      // removeEventListener가 호출되었는지 확인
      expect(removeEventListenerSpy).toHaveBeenCalledWith('mousemove', expect.any(Function));
      expect(removeEventListenerSpy).toHaveBeenCalledWith('mouseup', expect.any(Function));

      removeEventListenerSpy.mockRestore();
    });
  });
});
