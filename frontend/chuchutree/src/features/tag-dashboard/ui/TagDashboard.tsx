import TagCard from '@/features/tag-dashboard/ui/TagCard';
import mockData from '@/features/tag-dashboard/mockdata/mock_tag_dashboard_data.json';
import { TagDetail } from '@/shared/types/tagDashboard';

export default function TagDashboard() {
  // mock 데이터에서 태그 목록 가져오기
  const tags = mockData.data.tags as TagDetail[];

  // LOCKED와 EXCLUDED를 제외한 태그만 표시 (또는 전체 표시 가능)
  const displayTags = tags.filter((tag) => !tag.locked_yn && !tag.excluded_yn);

  return (
    <div className="grid h-full w-full grid-cols-2 content-start gap-4 overflow-y-auto lg:grid-cols-3">
      {tags.map((tag) => (
        <TagCard key={tag.tagId} tag={tag} />
      ))}
    </div>
  );
}
