import '@tanstack/react-query';
import type { AxiosError } from 'axios';
import type { ApiError } from './api';

declare module '@tanstack/react-query' {
  interface Register {
    defaultError: AxiosError<ApiError>;
  }
}
