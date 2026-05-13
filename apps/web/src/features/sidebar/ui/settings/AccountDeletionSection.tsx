'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Input } from '@/components/ui/input';

export default function AccountDeletionSection({ isLanding = false }: { isLanding?: boolean }) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [checks, setChecks] = useState({
    dataLoss: false,
    irreversible: false,
    understand: false,
  });

  const handleCheckChange = (key: keyof typeof checks) => {
    setChecks((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const isConfirmValid = confirmText === '계정삭제' && checks.dataLoss && checks.irreversible && checks.understand;

  const handleDialogOpen = () => {
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    // 다이얼로그 닫을 때 상태 초기화
    setConfirmText('');
    setChecks({ dataLoss: false, irreversible: false, understand: false });
  };

  const handleAccountDeletion = () => {
    // 백엔드 OAuth 재인증 플로우 시작
    // 브라우저가 직접 백엔드 URL로 이동 (소셜 로그인과 동일한 방식)
    const API_URL = process.env.NEXT_PUBLIC_API_URL || '';
    const baseUrl = API_URL ? `${API_URL}/api/v1` : '/api/v1';

    // local 환경에서만 redirectUrl 파라미터 추가
    const redirectUrl = process.env.NODE_ENV === 'development' ? '?redirectUrl=http://localhost:3000' : '';

    // 백엔드로 이동 → 소셜 재로그인 → callback → 계정 삭제 → 홈 리다이렉트
    window.location.href = `${baseUrl}/auth/withdraw${redirectUrl}`;
  };

  return (
    <>
      <div className="space-y-6">
        <div>
          <h3 className="text-destructive text-sm font-semibold">위험 영역</h3>
          <p className="text-muted-foreground text-xs">계정을 삭제하면 모든 데이터가 영구적으로 삭제됩니다.</p>
        </div>

        <div className="rounded-lg border-2 p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium">계정 삭제</div>
              <div className="text-muted-foreground text-xs">모든 활동 기록과 개인 정보가 삭제됩니다.</div>
            </div>
            <Button variant="destructive" onClick={handleDialogOpen} disabled={isLanding}>
              계정 삭제
            </Button>
          </div>
        </div>
      </div>

      <AlertDialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <AlertDialogContent className="sm:max-w-md">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-destructive">계정 삭제</AlertDialogTitle>
            <AlertDialogDescription>이 작업은 되돌릴 수 없습니다. 계속하기 전에 다음 사항을 확인해주세요.</AlertDialogDescription>
          </AlertDialogHeader>

          <div className="space-y-4 py-4">
            {/* 체크박스 목록 */}
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  id="dataLoss"
                  checked={checks.dataLoss}
                  onChange={() => handleCheckChange('dataLoss')}
                  className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                />
                <label htmlFor="dataLoss" className="text-sm leading-tight">
                  모든 활동 기록이 영구적으로 삭제됨을 이해했습니다.
                </label>
              </div>

              <div className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  id="irreversible"
                  checked={checks.irreversible}
                  onChange={() => handleCheckChange('irreversible')}
                  className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                />
                <label htmlFor="irreversible" className="text-sm leading-tight">
                  모든 개인 정보가 삭제되며 복구할 수 없음을 이해했습니다.
                </label>
              </div>

              <div className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  id="understand"
                  checked={checks.understand}
                  onChange={() => handleCheckChange('understand')}
                  className="checked:bg-primary checked:border-primary border-muted-foreground h-4 w-4 cursor-pointer appearance-none rounded border-2"
                />
                <label htmlFor="understand" className="text-sm leading-tight">
                  이 작업은 되돌릴 수 없음을 이해했습니다.
                </label>
              </div>
            </div>

            {/* 확인 텍스트 입력 */}
            <div className="space-y-2">
              <label htmlFor="confirmText" className="text-muted-foreground text-sm font-medium">
                계속하려면 <span className="text-destructive font-bold">계정삭제</span>를 입력하세요
              </label>
              <Input id="confirmText" value={confirmText} onChange={(e) => setConfirmText(e.target.value)} placeholder="계정삭제" className="font-medium" />
            </div>
          </div>

          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleDialogClose}>취소</AlertDialogCancel>
            <AlertDialogAction onClick={handleAccountDeletion} disabled={!isConfirmValid} className="bg-destructive hover:bg-destructive/90">
              계정 삭제
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
