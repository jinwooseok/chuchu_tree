'use client';

import { useState, useEffect } from 'react';

function getColumns(): number {
  if (typeof window === 'undefined') return 1;
  if (window.matchMedia('(min-width: 1280px)').matches) return 3;
  if (window.matchMedia('(min-width: 1024px)').matches) return 2;
  return 1;
}

export function useColumns(): number {
  // lazy initializer: 클라이언트에서는 최초 렌더 시 즉시 올바른 컬럼 수로 시작 (초기 flash 방지)
  const [columns, setColumns] = useState(getColumns);

  useEffect(() => {
    const xl = window.matchMedia('(min-width: 1280px)');
    const lg = window.matchMedia('(min-width: 1024px)');

    const update = () => setColumns(getColumns());

    xl.addEventListener('change', update);
    lg.addEventListener('change', update);

    return () => {
      xl.removeEventListener('change', update);
      lg.removeEventListener('change', update);
    };
  }, []);

  return columns;
}
