import { RecommendationAnswer, RecommendationButton } from '@/features/recommendation';

export default function BottomRecommend() {
  return (
    <div className="bg-innerground-white flex h-full items-center justify-between p-4">
      <RecommendationButton />
      <RecommendationAnswer />
    </div>
  );
}
