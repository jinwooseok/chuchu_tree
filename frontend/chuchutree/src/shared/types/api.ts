export interface ApiResponse<T = any> {
  status: number;
  message: string;
  data: T;
  error: ApiError;
}

export interface ApiError {
  code?: string;
  message?: string;
}

export type UseMutationCallback = {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  onMutate?: () => void;
  onSettled?: () => void;
};