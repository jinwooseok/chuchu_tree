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
