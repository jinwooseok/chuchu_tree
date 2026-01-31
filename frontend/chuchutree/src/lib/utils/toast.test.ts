/**
 * Toast 알림 유틸리티 함수 테스트
 */

import { toast } from './toast';
import { toast as sonnerToast } from 'sonner';

jest.mock('sonner');

describe('toast', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('success 메시지를 표시한다', () => {
    toast.success('성공 메시지');
    expect(sonnerToast.success).toHaveBeenCalledWith('성공 메시지', { position: 'top-center' });
  });

  it('error 메시지를 표시한다', () => {
    toast.error('에러 메시지');
    expect(sonnerToast.error).toHaveBeenCalledWith('에러 메시지', { position: 'top-center' });
  });

  it('info 메시지를 표시한다', () => {
    toast.info('정보 메시지');
    expect(sonnerToast.info).toHaveBeenCalledWith('정보 메시지', { position: 'top-center' });
  });

  it('warning 메시지를 표시한다', () => {
    toast.warning('경고 메시지');
    expect(sonnerToast.warning).toHaveBeenCalledWith('경고 메시지', { position: 'top-center' });
  });

  it('모든 toast 함수가 position: top-center 옵션을 포함한다', () => {
    toast.success('테스트');
    toast.error('테스트');
    toast.info('테스트');
    toast.warning('테스트');

    expect(sonnerToast.success).toHaveBeenCalledWith('테스트', { position: 'top-center' });
    expect(sonnerToast.error).toHaveBeenCalledWith('테스트', { position: 'top-center' });
    expect(sonnerToast.info).toHaveBeenCalledWith('테스트', { position: 'top-center' });
    expect(sonnerToast.warning).toHaveBeenCalledWith('테스트', { position: 'top-center' });
  });
});
