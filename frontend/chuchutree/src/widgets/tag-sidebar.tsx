export default function TagSidebar() {
  return (
    <div className="flex h-full flex-col gap-4 overflow-y-auto p-4 text-sm">
      <div className="font-semibold">알고리즘 DashBoard</div>
      <div className="text-xs">정렬 기본, 이름, 마지막풀이, 등급</div>
      <div>검색창</div>
      <div>
        <div className="flex justify-between">
          <div>Imediated</div>
          <div>열림/닫힘 버튼</div>
        </div>
        <div className="flex flex-col text-xs">
          <div className="flex justify-between">
            <div>세그먼트트리</div>
            <div>advanced</div>
          </div>
          <div className="flex justify-between">
            <div>최대유량</div>
            <div>advanced</div>
          </div>
        </div>
      </div>
      <div>Advanced (동일한형태)</div>
      <div>Master (동일한형태)</div>
      <div>Locked (동일한형태)</div>
      <div>Excluded (동일한형태)</div>
    </div>
  );
}
