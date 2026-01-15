'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { SidebarProvider } from '@/components/ui/sidebar';
import { useState } from 'react';
import { Toaster } from '@/components/ui/sonner';
import { ModalProvider } from './providers/modal-provider';

export default function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 60 * 1000, // 60분
            gcTime: 60 * 60 * 1000, // 60분
            refetchOnWindowFocus: false,
            retry: 1,
          },
          mutations: {
            retry: 0,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ModalProvider>
        <Toaster />
        <SidebarProvider>{children}</SidebarProvider>
        <ReactQueryDevtools initialIsOpen={false} />
      </ModalProvider>
    </QueryClientProvider>
  );
}
