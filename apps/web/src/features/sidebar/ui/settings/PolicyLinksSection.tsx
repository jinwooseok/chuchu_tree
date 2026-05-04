'use client';

import { FileText, Shield, ExternalLink } from 'lucide-react';

export default function PolicyLinksSection() {
  const handleTermsClick = () => {
    window.open('/policies/terms-of-service', '_blank');
  };

  const handlePrivacyClick = () => {
    window.open('/policies/privacy', '_blank');
  };

  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-sm font-semibold">약관 및 정책</h3>
      </div>

      <div className="space-y-2 rounded-lg border p-4">
        <button
          onClick={handleTermsClick}
          className="hover:bg-accent flex w-full items-center justify-between rounded-lg p-3 transition-colors"
        >
          <div className="flex items-center gap-3">
            <FileText className="h-5 w-5" />
            <span className="text-sm">이용약관</span>
          </div>
          <ExternalLink className="text-muted-foreground h-4 w-4" />
        </button>

        <button
          onClick={handlePrivacyClick}
          className="hover:bg-accent flex w-full items-center justify-between rounded-lg p-3 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Shield className="h-5 w-5" />
            <span className="text-sm">개인정보처리방침</span>
          </div>
          <ExternalLink className="text-muted-foreground h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
