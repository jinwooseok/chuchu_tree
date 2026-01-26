import type { AxiosError } from 'axios';

export interface ApiResponse<T = any> {
  status: number;
  message: string;
  data: T;
  error: ApiError;
}

export interface ApiError {
  error: {
    code?: string;
    message?: string;
  };
}

export type UseMutationCallback = {
  onSuccess?: () => void;
  onError?: (error: AxiosError<ApiError>) => void;
  onMutate?: () => void;
  onSettled?: () => void;
};
