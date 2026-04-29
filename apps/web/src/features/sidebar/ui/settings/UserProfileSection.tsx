'use client';

import { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { User2 } from 'lucide-react';
import Image from 'next/image';
import { useUser, usePostProfileImage, useDeleteProfileImage } from '@/entities/user';
import { toast } from '@/lib/utils/toast';

export default function UserProfileSection({
  currentBjAccountId,
  currentUserCode,
  currentProfileImageUrl,
}: {
  currentBjAccountId: string;
  currentUserCode: string;
  currentProfileImageUrl: string | null;
}) {
  const { data: user } = useUser();
  const liveProfileImageUrl = user?.userAccount.profileImageUrl ?? currentProfileImageUrl;

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { mutate: postProfileImage, isPending: isUploading } = usePostProfileImage({
    onSuccess: () => {
      toast.success('프로필 사진이 변경되었습니다.');
      setSelectedFile(null);
      setPreviewUrl(null);
    },
    onError: () => {
      toast.error('프로필 사진 변경에 실패했습니다.');
    },
  });

  const { mutate: deleteProfileImage, isPending: isDeleting } = useDeleteProfileImage({
    onSuccess: () => {
      toast.success('프로필 사진이 삭제되었습니다.');
    },
    onError: () => {
      toast.error('프로필 사진 삭제에 실패했습니다.');
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      toast.error('파일 크기는 5MB 이하여야 합니다.');
      return;
    }
    if (!['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)) {
      toast.error('jpeg, png, gif, webp 형식만 지원합니다.');
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    e.target.value = '';
  };

  const handleUpload = () => {
    if (!selectedFile) return;
    postProfileImage(selectedFile);
  };

  const isPending = isUploading || isDeleting;
  const displayImageUrl = previewUrl ?? liveProfileImageUrl;

  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-sm font-semibold">프로필 변경</h3>
        <p className="text-muted-foreground text-xs">프로필 사진을 변경합니다.</p>
      </div>

      <div className="space-y-3 rounded-lg border p-4">
        <div className="flex items-center gap-4">
          <div className="bg-muted flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-full border">
            {/* 프로필사진 */}
            {displayImageUrl ? (
              <Image src={displayImageUrl} alt="프로필" width={64} height={64} className="h-full w-full object-cover" unoptimized />
            ) : (
              <User2 className="text-muted-foreground h-8 w-8" />
            )}
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-sm font-medium">
              {currentBjAccountId}#{currentUserCode}
            </span>
            <p className="text-muted-foreground text-xs">최대 5MB · jpeg / png / gif / webp</p>
          </div>
        </div>

        <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/gif,image/webp" className="hidden" onChange={handleFileChange} />

        <div className="flex justify-between">
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => fileInputRef.current?.click()} disabled={isPending}>
              사진 선택
            </Button>
            {(liveProfileImageUrl || previewUrl) && !selectedFile && (
              <Button variant="destructive" size="sm" onClick={() => deleteProfileImage()} disabled={isPending}>
                {isDeleting ? '삭제 중...' : '사진 삭제'}
              </Button>
            )}
          </div>
          {selectedFile && (
            <Button size="sm" onClick={handleUpload} disabled={isPending}>
              {isUploading ? '업로드 중...' : '저장'}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
