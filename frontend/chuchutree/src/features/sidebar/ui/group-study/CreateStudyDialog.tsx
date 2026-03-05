'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { toast } from '@/lib/utils/toast';
import { User } from '@/entities/user';
import { useState, useEffect } from 'react';
import { X, Loader2, Search, CheckCircle2, XCircle } from 'lucide-react';
import { useValidateStudyName, useSearchUsers, useCreateStudy, SearchedUser } from '@/entities/study';

interface props {
  user?: User;
  onClose: () => void;
}

type TabType = 'create' | 'join';

interface SearchedStudy {
  studyId: number;
  studyName: string;
  ownerName: string;
  memberCount: number;
  maxMemberCount: number;
}

export function CreateStudyDialog({ user, onClose }: props) {
  const [activeTab, setActiveTab] = useState<TabType>('create');

  // --- 생성 탭 state ---
  const bjAccountId = user?.bjAccount?.bjAccountId;
  const userCode = user?.userAccount?.userCode;
  const studyNamePlaceholder = bjAccountId ? (userCode ? `${bjAccountId}#${userCode}의 스터디` : `${bjAccountId}의 스터디`) : '스터디명을 입력하세요';

  const [studyName, setStudyName] = useState('');
  const [description, setDescription] = useState('');
  const [maxMembers, setMaxMembers] = useState(10);
  const [userSearchKeyword, setUserSearchKeyword] = useState('');
  const [debouncedUserKeyword, setDebouncedUserKeyword] = useState('');
  const [invitedUsers, setInvitedUsers] = useState<SearchedUser[]>([]);

  // --- 이름 중복검증 state ---
  const [nameValidated, setNameValidated] = useState<boolean | null>(null); // null=미검증, true=사용가능, false=중복

  // --- 가입 탭 state ---
  const [studySearchKeyword, setStudySearchKeyword] = useState('');
  const [debouncedStudyKeyword, setDebouncedStudyKeyword] = useState('');
  const [appliedStudyIds, setAppliedStudyIds] = useState<Set<number>>(new Set());

  // 사용자 검색 debounce
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedUserKeyword(userSearchKeyword), 400);
    return () => clearTimeout(timer);
  }, [userSearchKeyword]);

  // 스터디 검색 debounce
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedStudyKeyword(studySearchKeyword), 400);
    return () => clearTimeout(timer);
  }, [studySearchKeyword]);

  const { mutate: validateName, isPending: isValidating } = useValidateStudyName();
  const { data: userSearchResults = [], isLoading: isSearchingUsers } = useSearchUsers(debouncedUserKeyword);
  const { mutate: createStudy, isPending: isCreatingStudy } = useCreateStudy({
    onSuccess: () => {
      toast.success(`${studyName} 스터디가 생성되었습니다.`);
      onClose();
    },
    onError: () => {
      toast.error('스터디 생성에 실패했습니다.');
    },
  });

  const studySearchResults: SearchedStudy[] = [];
  const isSearchingStudies = false;

  const handleValidateName = () => {
    if (!studyName.trim()) return;
    validateName(studyName.trim(), {
      onSuccess: (result) => setNameValidated(result.available),
      onError: () => toast.error('스터디명 검증에 실패했습니다.'),
    });
  };

  const handleAddInvitedUser = (searched: SearchedUser) => {
    if (!invitedUsers.some((u) => u.userAccountId === searched.userAccountId)) {
      setInvitedUsers((prev) => [...prev, searched]);
    }
    setUserSearchKeyword('');
  };

  const handleRemoveInvitedUser = (userAccountId: number) => {
    setInvitedUsers((prev) => prev.filter((u) => u.userAccountId !== userAccountId));
  };

  const handleCreateStudy = () => {
    if (!studyName.trim()) {
      toast.error('스터디명을 입력해주세요.');
      return;
    }
    if (nameValidated === null) {
      toast.error('스터디명 중복 검증을 해주세요.');
      return;
    }
    if (nameValidated === false) {
      toast.error('이미 사용 중인 스터디명입니다.');
      return;
    }
    createStudy({
      studyName: studyName.trim(),
      description: description.trim(),
      maxMembers,
      inviteeUserAccountIds: invitedUsers.map((u) => u.userAccountId),
    });
  };

  const handleToggleApply = (study: SearchedStudy) => {
    setAppliedStudyIds((prev) => {
      const next = new Set(prev);
      if (next.has(study.studyId)) {
        next.delete(study.studyId);
      } else {
        next.add(study.studyId);
      }
      return next;
    });
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="flex max-h-[90vh] max-w-2xl flex-col">
        <DialogHeader>
          <DialogTitle>스터디</DialogTitle>
          <DialogDescription>스터디를 생성하거나 기존 스터디에 가입 신청할 수 있습니다.</DialogDescription>
        </DialogHeader>

        {/* 탭 전환 */}
        <div className="flex border-b">
          <button
            className={`flex-1 py-2 text-sm font-medium transition-colors ${activeTab === 'create' ? 'border-primary text-foreground border-b-2' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('create')}
          >
            생성
          </button>
          <button
            className={`flex-1 py-2 text-sm font-medium transition-colors ${activeTab === 'join' ? 'border-primary text-foreground border-b-2' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('join')}
          >
            가입 신청
          </button>
        </div>

        {activeTab === 'create' ? (
          /* ───────────── 생성 탭 ───────────── */
          <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto pr-1">
            {/* 스터디명 + 중복검증 */}
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium">스터디명</label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Input
                    value={studyName}
                    onChange={(e) => {
                      setStudyName(e.target.value);
                      setNameValidated(null);
                    }}
                    placeholder={studyNamePlaceholder}
                    onBlur={handleValidateName}
                    onKeyDown={(e) => e.key === 'Enter' && handleValidateName()}
                  />
                  {nameValidated !== null && (
                    <span className="absolute top-1/2 right-2 -translate-y-1/2">
                      {nameValidated ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <XCircle className="text-destructive h-4 w-4" />}
                    </span>
                  )}
                </div>
                <Button variant="outline" size="sm" onClick={handleValidateName} disabled={!studyName.trim() || isValidating} className="shrink-0">
                  {isValidating ? <Loader2 className="h-4 w-4 animate-spin" /> : '중복확인'}
                </Button>
              </div>
              {nameValidated === false && <p className="text-destructive text-xs">이미 사용 중인 스터디명입니다.</p>}
              {nameValidated === true && <p className="text-xs text-green-500">사용 가능한 스터디명입니다.</p>}
            </div>

            {/* 설명 */}
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium">설명</label>
              <Textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="스터디 설명을 입력하세요" className="resize-none" rows={3} />
            </div>

            {/* 최대 인원 */}
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium">최대 인원</label>
              <Input type="number" min={2} max={50} value={maxMembers} onChange={(e) => setMaxMembers(Math.max(2, Math.min(50, Number(e.target.value))))} className="w-24" />
            </div>

            {/* 사용자 검색 */}
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium">멤버 초대</label>
              <div className="relative">
                <Search className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
                <Input value={userSearchKeyword} onChange={(e) => setUserSearchKeyword(e.target.value)} placeholder="백준 아이디 또는 코드로 검색" className="pl-9" />
              </div>

              {debouncedUserKeyword && (
                <div className="bg-background overflow-hidden rounded-lg border">
                  {isSearchingUsers ? (
                    <div className="flex items-center justify-center py-4">
                      <Loader2 className="text-muted-foreground h-4 w-4 animate-spin" />
                    </div>
                  ) : userSearchResults.length > 0 ? (
                    userSearchResults.map((u) => (
                      <button key={u.userAccountId} className="hover:bg-muted flex w-full items-center justify-between px-3 py-2 text-sm transition-colors" onClick={() => handleAddInvitedUser(u)}>
                        <span className="font-medium">{u.bjAccountId}</span>
                        <span className="text-muted-foreground">#{u.userCode}</span>
                      </button>
                    ))
                  ) : (
                    <p className="text-muted-foreground py-4 text-center text-sm">검색 결과가 없습니다.</p>
                  )}
                </div>
              )}
            </div>

            {/* 초대 목록 */}
            {invitedUsers.length > 0 && (
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium">초대 목록 ({invitedUsers.length}명)</label>
                <div className="flex flex-wrap gap-1.5">
                  {invitedUsers.map((u) => (
                    <div key={u.userAccountId} className="bg-muted flex items-center gap-1.5 rounded-full px-3 py-1 text-sm">
                      <span>{u.bjAccountId}</span>
                      <span className="text-muted-foreground">#{u.userCode}</span>
                      <button onClick={() => handleRemoveInvitedUser(u.userAccountId)} className="text-muted-foreground hover:text-foreground">
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-auto flex shrink-0 justify-end gap-2 pt-2">
              <Button variant="outline" onClick={onClose}>
                취소
              </Button>
              <Button onClick={handleCreateStudy} disabled={isCreatingStudy}>
                {isCreatingStudy && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                스터디 생성
              </Button>
            </div>
          </div>
        ) : (
          /* ───────────── 가입 신청 탭 ───────────── */
          <div className="flex min-h-0 flex-1 flex-col gap-4">
            <div className="relative">
              <Search className="text-muted-foreground absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2" />
              <Input value={studySearchKeyword} onChange={(e) => setStudySearchKeyword(e.target.value)} placeholder="스터디명, 방장 아이디 또는 코드로 검색" className="pl-9" />
            </div>

            {debouncedStudyKeyword ? (
              isSearchingStudies ? (
                <div className="flex min-h-40 items-center justify-center">
                  <Loader2 className="text-muted-foreground h-6 w-6 animate-spin" />
                </div>
              ) : studySearchResults.length > 0 ? (
                <div className="min-h-0 flex-1 overflow-y-auto pr-1">
                  <div className="space-y-2">
                    {studySearchResults.map((study) => (
                      <div key={study.studyId} className="flex items-center justify-between rounded-lg border p-3">
                        <div className="flex flex-col gap-0.5">
                          <span className="font-medium">{study.studyName}</span>
                          <div className="text-muted-foreground flex items-center gap-2 text-sm">
                            <span>방장: {study.ownerName}</span>
                            <span>·</span>
                            <span>
                              {study.memberCount}/{study.maxMemberCount}명
                            </span>
                          </div>
                        </div>
                        <Button variant={appliedStudyIds.has(study.studyId) ? 'secondary' : 'default'} size="sm" onClick={() => handleToggleApply(study)} className="ml-2 shrink-0">
                          {appliedStudyIds.has(study.studyId) ? '취소하기' : '가입 신청'}
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="flex min-h-40 flex-col items-center justify-center">
                  <p className="text-muted-foreground text-sm">검색 결과가 없습니다.</p>
                </div>
              )
            ) : (
              <div className="flex min-h-40 flex-col items-center justify-center">
                <p className="text-muted-foreground text-sm">스터디명, 방장 아이디 또는 코드로 검색하세요.</p>
              </div>
            )}

            <div className="flex shrink-0 justify-end gap-2 pt-2">
              <Button variant="outline" onClick={onClose}>
                닫기
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
