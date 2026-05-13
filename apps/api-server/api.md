# 부동산/토지 공공 API 정리

---

## 1. 용도별건물속성조회

| 항목 | 내용 |
|------|------|
| 제공기관 | 국가중점데이터API (공간융합 개방데이터) |
| 요청주소 | `https://api.vworld.kr/ned/data/getBuildingUse` |
| 설명 | 용도, 필지고유번호를 통해 건물의 주요용도, 세부용도, 건물용도분류 등을 조회 |
| 트래픽 | 999,999,999/일 |

### 요청변수

| 파라미터 | 필수 | 설명 | 샘플 |
|----------|------|------|------|
| pnu | 필수 | 고유번호(8자리 이상) | 1111017400 |
| mainPrposCode | 옵션 | 주요용도코드 | 02000 |
| detailPrposCode | 옵션 | 세부용도코드 | 02001 |
| format | 옵션 | 응답 형식 (xml/json) | xml |
| numOfRows | 옵션 | 검색건수 (최대 1000) | 10 |
| pageNo | 옵션 | 페이지 번호 | 1 |
| key | 필수 | 발급받은 API key | - |
| domain | 옵션 | API KEY 발급 시 입력한 URL | - |

### 출력결과

| 필드 | 설명 | 샘플 |
|------|------|------|
| gisIdntfcNo | GIS건물통합식별번호 | 2005197355104560323100000000 |
| pnu | 고유번호 | 1111018300101970001 |
| ldCode | 법정동코드 | 1111018300 |
| ldCodeNm | 법정동명 | 서울특별시 종로구 평창동 |
| regstrSeCode | 특수지구분코드 | 1 |
| regstrSeCodeNm | 특수지구분명 | 일반 |
| mnnmSlno | 지번 | 197-1 |
| buldIdntfcNo | 건물식별번호 | 14652 |
| agbldgSeCode | 집합건물구분코드 | 1 |
| agbldgSeCodeNm | 집합건물구분 | 일반건축물 |
| buldKndCode | 대장종류코드 | 2 |
| buldKndCodeNm | 대장종류 | 일반건축물대장 |
| buldNm | 건물명 | (주)길륭평창동사옥 |
| buldDongNm | 건물동명 | (주)길륭평창동사옥 |
| buldMainAtachSeCode | 건물주부구분코드 | 0 |
| buldMainAtachSeCodeNm | 건물주부구분명 | 주건축물 |
| buldPlotAr | 건물대지면적(㎡) | 453 |
| buldBildngAr | 건물건축면적(㎡) | 233.3 |
| buldTotar | 건물연면적(㎡) | 1154.16 |
| measrmtRt | 용적율(%) | 198.45 |
| btlRt | 건폐율(%) | 51.5 |
| strctCode | 건축물구조코드 | 21 |
| strctCodeNm | 건축물구조명 | 철근콘크리트구조 |
| mainPrposCode | 주요용도코드 | 04000 |
| mainPrposCodeNm | 주요용도명 | 제2종근린생활시설 |
| detailPrposCode | 세부용도코드 | 04001 |
| detailPrposCodeNm | 세부용도명 | 일반음식점 |
| buldPrposClCode | 건물용도분류코드 | 2 |
| buldPrposClCodeNm | 건물용도분류명 | 상업용 |
| buldHg | 건물높이(m) | 17.75 |
| groundFloorCo | 지상층수 | 5 |
| undgrndFloorCo | 지하층수 | 1 |
| prmisnDe | 허가일자 | 2004-11-30 |
| useConfmDe | 사용승인일자 | 2005-07-19 |
| lastUpdtDt | 데이터기준일자 | 2017-08-11 |

---

## 2. 토지소유정보속성조회

| 항목 | 내용 |
|------|------|
| 제공기관 | 국가중점데이터API (국가공간 개방데이터) |
| 요청주소 | `https://api.vworld.kr/ned/data/getPossessionAttr` |
| 설명 | 토지대장부에 등록된 토지의 상태 및 소유상태에 대한 속성정보를 조회 |
| 트래픽 | 999,999,999/일 |

### 요청변수

| 파라미터 | 필수 | 설명 | 샘플 |
|----------|------|------|------|
| pnu | 필수 | 고유번호(8자리 이상) | 1111011000100010001 |
| format | 옵션 | 응답 형식 (xml/json) | xml |
| numOfRows | 옵션 | 검색건수 (최대 1000) | 10 |
| pageNo | 옵션 | 페이지 번호 | 1 |
| key | 필수 | 발급받은 API key | - |
| domain | 옵션 | API KEY 발급 시 입력한 URL | - |

### 출력결과

| 필드 | 설명 | 샘플 |
|------|------|------|
| pnu | 고유번호 | 1165010800113320000 |
| ldCode | 법정동코드 | 1165010800 |
| ldCodeNm | 법정동명 | 서울특별시 서초구 서초동 |
| regstrSeCode | 대장구분코드 | 1 |
| regstrSeCodeNm | 대장구분명 | 토지대장 |
| mnnmSlno | 지번 | 1332-11 |
| agbldgSn | 집합건물일련번호 | 5091 |
| buldDongNm | 건물동명 | 202 |
| buldFloorNm | 건물층명 | 17 |
| buldHoNm | 건물호명 | 1702 |
| buldRoomNm | 건물실명 | 5 |
| cnrsPsnSn | 공유인일련번호 | 000001 |
| stdrYm | 기준연월 | 2016-08 |
| lndcgrCode | 지목코드 | 08 |
| lndcgrCodeNm | 지목 | 대 |
| lndpclAr | 토지면적(㎡) | 122 |
| pblntfPclnd | 공시지가(원/㎡) | 1544000 |
| posesnSeCode | 소유구분코드 | 04 |
| posesnSeCodeNm | 소유구분 | 시, 도유지 |
| resdncSeCode | 거주지구분코드 | ZZ |
| resdncSeCodeNm | 거주지구분 | 구분없음 |
| nationInsttSeCode | 국가기관구분코드 | 02 |
| nationInsttSeCodeNm | 국가기관구분 | 지자체 |
| ownshipChgCauseCode | 소유권변동원인코드 | 05 |
| ownshipChgCauseCodeNm | 소유권변동원인 | 성명(명칭)변경 |
| ownshipChgDe | 소유권변동일자 | 1993-04-21 |
| cnrsPsnCo | 공유인수 | 0 |
| lastUpdtDt | 데이터기준일자 | 2016-08-15 |

---

## 3. 개별공시지가속성조회

| 항목 | 내용 |
|------|------|
| 제공기관 | 국가중점데이터API (국가공간 개방데이터) |
| 요청주소 | `https://api.vworld.kr/ned/data/getIndvdLandPriceAttr` |
| 설명 | 개별토지의 단위면적당 가격정보에 대한 속성정보를 조회 |
| 트래픽 | 999,999,999/일 |

### 요청변수

| 파라미터 | 필수 | 설명 | 샘플 |
|----------|------|------|------|
| pnu | 필수 | 고유번호(8자리 이상) | 1111017700102110000 |
| stdrYear | 옵션 | 기준연도(YYYY: 4자리) | 2015 |
| format | 옵션 | 응답 형식 (xml/json) | xml |
| numOfRows | 옵션 | 검색건수 (최대 1000) | 10 |
| pageNo | 옵션 | 페이지 번호 | 1 |
| key | 필수 | 발급받은 API key | - |
| domain | 옵션 | API KEY 발급 시 입력한 URL | - |

### 출력결과

| 필드 | 설명 | 샘플 |
|------|------|------|
| pnu | 고유번호 | 1165010800113320000 |
| ldCode | 법정동코드 | 1165010800 |
| ldCodeNm | 법정동명 | 서울특별시 서초구 서초동 |
| regstrSeCode | 특수지구분코드 | 1 |
| regstrSeCodeNm | 특수지구분명 | 일반 |
| mnnmSlno | 지번 | 1332-0 |
| stdrYear | 기준연도 | 2016 |
| stdrMt | 기준월 | 08 |
| pblntfPclnd | 공시지가(원/㎡) | 399000 |
| pblntfDe | 공시일자 | 2016-08-15 |
| stdLandAt | 표준지여부 | Y 또는 N |
| lastUpdtDt | 데이터기준일자 | 2016-08-15 |

---

## 4. 실시간 주소정보 조회 (검색API)

| 항목 | 내용 |
|------|------|
| 제공기관 | 행정안전부 |
| 설명 | 도로명주소 DB 구축 없이 실시간으로 주소 검색 기능 구현 |
| 특징 | 개발언어/플랫폼 제약없음, DB 구축 불필요, 신청 즉시 이용 가능, 1시스템 1승인키 |

### 입력 파라미터

| 파라미터 | 설명 |
|----------|------|
| confmKey | 신청 시 발급받은 승인키 |
| currentPage | 현재 페이지 번호 |
| countPerPage | 페이지당 출력할 결과 Row 수 |
| keyword | 주소 검색어 |
| resultType | 검색결과 형식 (xml/json) |
| hstryIncludeYn | 변동된 주소정보 포함 여부 |
| firstSort | 정렬 (none: 정확도순, road: 도로명 우선, location: 지번 우선) |
| addInfoYn | 추가항목(hstryYn, relJibun, hemdNm) 제공 여부 |

### 출력 파라미터

| 필드 | 설명 |
|------|------|
| roadAddr | 전체 도로명주소 |
| roadAddrPart1 | 도로명주소 (참고항목 제외) |
| roadAddrPart2 | 도로명주소 참고항목 |
| jibunAddr | 지번주소 |
| engAddr | 도로명주소 (영문) |
| zipNo | 우편번호 |
| admCd | 행정구역코드 |
| rnMgtSn | 도로명코드 |
| bdMgtSn | 건물관리번호 |
| detBdNmList | 상세건물명 |
| bdNm | 건물명 |
| bdKdcd | 공동주택여부 (1: 공동주택, 0: 비공동주택) |
| siNm | 시도명 |
| sggNm | 시군구명 |
| emdNm | 읍면동명 |
| liNm | 법정리명 |
| rn | 도로명 |
| udrtYn | 지하여부 (0: 지상, 1: 지하) |
| buldMnnm | 건물본번 |
| buldSlno | 건물부번 |
| mtYn | 산여부 (0: 대지, 1: 산) |
| lnbrMnnm | 지번본번(번지) |
| lnbrSlno | 지번부번(호) |
| emdNo | 읍면동일련번호 |
| hstryYn | 변동이력여부 (0: 현행, 1: 변동된 주소에서 검색된 정보) |
| relJibun | 관련지번 |
| hemdNm | 관할주민센터 |

---

## 5. 토지이용규제 법령정보서비스

| 항목 | 내용 |
|------|------|
| 제공기관 | 국토교통부 (도시정책과) |
| Base URL | `apis.data.go.kr/1613000/LuLawInfoService` |
| 설명 | 시군구별/지역지구별 토지이용규제 법령정보 조회 |
| API 유형 | REST / XML |
| 비용 | 무료 |
| 트래픽 | 개발: 1,000 / 운영: 활용사례 등록 시 증가 가능 |
| 심의 | 자동승인 |

### API 목록

#### GET /DTluLawInfo - 토지이용규제 법령정보

**요청변수**

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| serviceKey | 필수 | 공공데이터포털 인증키 |
| areaCd | 필수 | 시군구코드 |
| ucodeList | 필수 | 지역지구코드 |

**출력결과**

| 필드 | 설명 |
|------|------|
| UCODE | 지역지구코드 |
| UNAME | 지역지구명 |
| LAW_CONTENTS | 법령 내용 |
| LAW_LEVEL | 법령 내용 표기 순서 (0:조, 1:항, 2:호, 3:목) |
| LAW_FULL_CD | 법령 내용 코드 |

### Request
```
areaCd: 11110 // 시군구코드
ucodeList: UQA123 // 지역지구코드
```

### Response
```
This XML file does not appear to have any style information associated with it. The document tree is shown below.
<response>
<div id="in-page-channel-node-id" data-channel-name="in_page_channel_igYoAT"/>
<header>
<resultCode>0</resultCode>
<resultMsg>OK</resultMsg>
</header>
<body>
<items>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>제94조(2 이상의 용도지역·용도지구·용도구역에 걸치는 토지에 대한 적용기준) 법 제84조제1항 각 호 외의 부분 본문 및 같은 조 제3항 본문에서 "대통령령으로 정하는 규모"라 함은 330제곱미터를 말한다. 다만, 도로변에 띠 모양으로 지정된 상업지역에 걸쳐 있는 토지의 경우에는 660제곱미터를 말한다. <개정 2004.1.20, 2012.4.10></LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>00000000009419000940000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>제84조(둘 이상의 용도지역ㆍ용도지구ㆍ용도구역에 걸치는 대지에 대한 적용 기준)</LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>00000000009294000840000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>제56조(개발행위의 허가) </LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>00000000009294000560000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>제83조(도시지역에서의 다른 법률의 적용 배제) 도시지역에 대하여는 다음 각 호의 법률 규정을 적용하지 아니한다. <개정 2011.4.14., 2014.1.14.></LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>00000000009294000830000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>제93조(기존의 건축물에 대한 특례) </LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>00000000009419000930000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>제71조(용도지역안에서의 건축제한) </LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>00000000009419000710000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>제51조(개발행위허가의 대상) </LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>00000000009419000510000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>제83조(용도지역ㆍ용도지구 및 용도구역안에서의 건축제한의 예외 등) </LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>00000000009419000830000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>제83조(용도지역ㆍ용도지구 및 용도구역안에서의 건축제한의 예외 등) </LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>00000000009419000830000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>제83조(용도지역ㆍ용도지구 및 용도구역안에서의 건축제한의 예외 등) </LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>00000000009419000830000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>[별표 6] <개정 2023. 5. 15.> 제3종일반주거지역안에서 건축할 수 있는 건축물(제71조제1항제5호관련)</LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>00000000009419100060000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>제33조(용도지역 안에서의 건축제한) 용도지역 안에서의 건축물의 용도ㆍ종류 및 규모 등의 제한(이하 "건축제한"이라 한다)은 다음 각호와 같다.</LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>11000002000719000330000000000000</LAW_FULL_CD>
</item>
<item>
<UCODE>UQA123</UCODE>
<UNAME>제3종일반주거지역</UNAME>
<LAW_CONTENTS>[별표 6]제3종일반주거지역 안에서 건축할 수 있는 건축물(제33조제5호 관련) 제3종일반주거지역 안에서는 영 별표 6 제1호의 각 목의 건축물과 영 별표 6 제2호에 따라 다음 각 호의 건축물을 건축할 수 있다. </LAW_CONTENTS>
<LAW_LEVEL>1</LAW_LEVEL>
<LAW_FULL_CD>11000002000719100060000000000000</LAW_FULL_CD>
</item>
</items>
<totalCount>13</totalCount>
</body>
</response>
```
---

## 6. 토지이용규제정보서비스 (행위제한)

| 항목 | 내용 |
|------|------|
| 제공기관 | 국토교통부 (도시정책과) |
| Base URL | `apis.data.go.kr/1613000/arLandUseInfoService` |
| 설명 | 시군구별/지역지구별 토지이용행위 규제 내용(행위 + 가능여부) 조회 |
| API 유형 | REST / XML |
| 비용 | 무료 |
| 트래픽 | 개발: 1,000 / 운영: 활용사례 등록 시 증가 가능 |
| 심의 | 자동승인 |

### API 목록

#### GET /DTarLandUseInfo - 토지이용규제 행위제한정보

**요청변수**

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| serviceKey | 필수 | 공공데이터포털 인증키 |
| areaCd | 필수 | 시군구코드 |
| ucodeList | 필수 | 지역지구코드 |

**출력결과**

| 필드 | 설명 |
|------|------|
| UNAME | 지역지구명 |
| UCODE_REF_LAW_CD | 지역지구코드 |
| UCODE | 지역지구 법령코드 |
| actRegList | 행위제한내용 목록 |
| actRegList.ACT_NM | 행위 |
| actRegList.REG_NM | 가능여부 |
| actRegList.QNODE_CONDS | 조건제한 예외사항 |
| luInfoList | 토지이용정보 목록 |
| luInfoList.NODE_DESC | 토지이용명 |
| luInfoList.LU_REF_LAW_NM1 | 참조 법령조항1 |
| luInfoList.LU_REF_LAW_NM2 | 참조 법령조항2 |
| luInfoList.LU_REF_LAW_NM3 | 참조 법령조항3 |
| luInfoList.DEF_REF | 정의 및 참조사항 |

#### Request
```
serviceKey	// 공공데이터포털에서 받은 인증키
areaCd:11110 // 시군구코드
ucodeList:UQA123 // 지역지구코드
landUseNm:창고 // 토지이용행위명
```

#### Response
```
This XML file does not appear to have any style information associated with it. The document tree is shown below.
<response>
<div id="in-page-channel-node-id" data-channel-name="in_page_channel_EtbnxT"/>
<header>
<resultCode>0</resultCode>
<resultMsg>OK</resultMsg>
</header>
<body>
<items>
<item>
<UNAME>제3종일반주거지역</UNAME>
<UCODE_REF_LAW_CD>00000000009419000300000001002003</UCODE_REF_LAW_CD>
<UCODE>UQA123</UCODE>
<actRegList>
<ACT_NM>건축</ACT_NM>
<REG_NM>가능</REG_NM>
<QNODE_CONDS>
<RNUM>32603</RNUM>
</QNODE_CONDS>
<luInfoList>
<NODE_DESC>창고</NODE_DESC>
<LU_REF_LAW_NM1>건축법 시행령 별표 1 제18호가목</LU_REF_LAW_NM1>
<DEF_REF>- 물품저장시설로서 「물류정책기본법」에 따른 일반창고와 냉장 및 냉동 창고를 포함, - 제2종 근린생활시설에 해당하는 것과 위험물 저장 및 처리 시설 또는 그 부속용도에 해당하는 것은 제외</DEF_REF>
</luInfoList>
</actRegList>
<actRegList>
<ACT_NM>건축</ACT_NM>
<REG_NM>금지</REG_NM>
<luInfoList>
<NODE_DESC>가축용 창고</NODE_DESC>
<LU_REF_LAW_NM1>건축법 시행령 별표 1 제21호나목</LU_REF_LAW_NM1>
<DEF_REF>가축용 창고</DEF_REF>
</luInfoList>
</actRegList>
</item>
<QnodeCond>
<QNODE_DESC>해당 용도에 쓰이는 바닥면적의 합계가 2천제곱미터 미만인 것에 한한다.</QNODE_DESC>
<RNUM>32603</RNUM>
</QnodeCond>
</items>
<totalCount>1</totalCount>
</body>
</response>
```

#### GET /DTsearchLunCd - 토지이용행위 조회

**출력결과**

| 필드 | 설명 |
|------|------|
| LUN_NM | 토지이용행위명 |
| LUN_CD | 토지이용행위코드 |

---

## 7. 토지이용계획속성조회

| 항목 | 내용 |
|------|------|
| 제공기관 | 국가중점데이터API (국가공간 개방데이터) |
| 요청주소 | `https://api.vworld.kr/ned/data/getLandUseAttr` |
| 설명 | 계획구역 내의 토지의 이용계획에 대한 속성정보를 조회 (pnu → UCODE 매핑의 핵심 API) |
| 트래픽 | 999,999,999/일 |

### 요청변수

| 파라미터 | 필수 | 설명 | 샘플 |
|----------|------|------|------|
| pnu | 필수 | 고유번호(8자리 이상) | 116501080011332 |
| cnflcAt | 옵션 | 저촉여부코드 (1:포함, 2:저촉, 3:접합) | 1 |
| prposAreaDstrcCodeNm | 옵션 | 용도지역지구명 | 아파트지구 |
| format | 옵션 | 응답 형식 (xml/json) | xml |
| numOfRows | 옵션 | 검색건수 (최대 1000) | 10 |
| pageNo | 옵션 | 페이지 번호 | 1 |
| key | 필수 | 발급받은 API key | - |
| domain | 옵션 | API KEY 발급 시 입력한 URL | - |

### 출력결과

| 필드 | 설명 | 샘플 |
|------|------|------|
| pnu | 고유번호 | 1165010800113320002 |
| ldCode | 법정동코드 | 1165010800 |
| ldCodeNm | 법정동명 | 서울특별시 서초구 서초동 |
| regstrSeCode | 대장구분코드 | 1 |
| regstrSeCodeNm | 대장구분명 | 토지대장 |
| mnnmSlno | 지번 | 1332-2 |
| manageNo | 도면번호 | 150000011650000000000UQP1100008008 |
| cnflcAt | 저촉여부코드 | 1 |
| cnflcAtNm | 저촉여부 | 포함 |
| prposAreaDstrcCode | 용도지역지구코드 (=UCODE) | UQP110 |
| prposAreaDstrcCodeNm | 용도지역지구명 | 아파트지구 |
| registDt | 등록일자 | 2016-08-15 |
| lastUpdtDt | 데이터기준일자 | 2016-08-15 |

> **핵심**: 이 API가 pnu → UCODE 변환을 담당. 한 필지에 여러 지역지구가 중첩될 수 있어 결과가 N건 반환됨.
> 여기서 얻은 `prposAreaDstrcCode`(=UCODE)와 pnu 앞 5자리(=areaCd)로 API 5, 6 호출 가능.

---

## 공통 오류코드 (vworld API)

| 코드 | 레벨 | 메세지 |
|------|------|--------|
| URL_TYPE | 1 | 잘못된 URL 입니다. |
| PARAM_REQUIRED | 1 | 필수 파라미터인 <%S1>가 없어서 요청을 처리할수 없습니다. |
| INVALID_TYPE | 1 | <%S1> 파라미터 타입이 유효하지 않습니다. |
| INVALID_RANGE | 1 | <%S1> 파라미터의 값이 유효한 범위를 넘었습니다. |
| INVALID_KEY | 2 | 등록되지 않은 인증키입니다. |
| INCORRECT_KEY | 2 | 인증키 정보가 올바르지 않습니다. |
| UNAVAILABLE_KEY | 2 | 임시로 인증키를 사용할 수 없는 상태입니다. |
| OVER_REQUEST_LIMIT | 2 | 일일 제한량 초과 |
| SYSTEM_ERROR | 3 | 시스템 에러 |
| UNKNOWN_ERROR | 3 | 알 수 없는 에러 |

---

## 참고 사이트 - API 매핑

| 사이트 | URL | 매핑 API |
|--------|-----|----------|
| 소유자 | https://www.vworld.kr/dtmk/dtmk_ntads_s002.do?svcCde=NA&dsId=12 | **API 2. 토지소유정보속성조회** (`getPossessionAttr`) |
| 공시지가 | https://www.vworld.kr/dtna/dtna_apiSvcFc_s001.do?apiNum=25 | **API 3. 개별공시지가속성조회** (`getIndvdLandPriceAttr`) |
| 이용계획 | https://www.vworld.kr/dtna/dtna_apiSvcFc_s001.do?apiNum=51 | **API 7. 토지이용계획속성조회** (`getLandUseAttr`) |
| 규제 | https://www.data.go.kr/data/15058410/openapi.do | **API 6. 토지이용규제정보서비스** (`arLandUseInfoService`) |
| 규제법령 | https://www.data.go.kr/data/15057174/openapi.do | **API 5. 토지이용규제법령정보서비스** (`LuLawInfoService`) |

> **참고**: API 1(용도별건물속성조회)과 API 4(주소검색)는 별도 사이트 없이 vworld/행정안전부에서 직접 제공

---

## 데이터 조합으로 생성 가능한 테이블

### 공통 조인 키
- **`pnu` (필지고유번호)**: API 1, 2, 3, 7의 공통 키 - 필지 단위로 건물/소유/가격/이용계획 통합 가능
- **`ldCode` (법정동코드)**: API 1, 2, 3 출력에 포함 - 지역 단위 집계 가능
- **`prposAreaDstrcCode` (용도지역지구코드 = UCODE)**: API 7 출력 → API 5, 6의 요청 키로 사용
- **`areaCd` (시군구코드)**: API 5, 6의 요청 키 - pnu 앞 5자리에서 추출
- **`bdMgtSn` (건물관리번호)**: API 4 출력 - pnu와 매핑하여 주소↔필지 연결

---

### 테이블 1: 필지 종합 정보 (pnu 기준 통합)

> API 1 + API 2 + API 3 조인

| 컬럼 | 출처 | 설명 |
|------|------|------|
| pnu | 공통 | 필지고유번호 (PK) |
| ldCodeNm | API 1,2,3 | 법정동명 |
| mnnmSlno | API 1,2,3 | 지번 |
| lndcgrCodeNm | API 2 | 지목 (대, 전, 답 등) |
| lndpclAr | API 2 | 토지면적(㎡) |
| pblntfPclnd | API 3 | 공시지가(원/㎡) |
| stdrYear | API 3 | 공시지가 기준연도 |
| posesnSeCodeNm | API 2 | 소유구분 (개인, 국유지 등) |
| ownshipChgDe | API 2 | 소유권변동일자 |
| buldNm | API 1 | 건물명 |
| mainPrposCodeNm | API 1 | 주요용도명 |
| buldTotar | API 1 | 건물연면적(㎡) |

**활용**: 특정 필지의 토지+건물+소유+가격을 한눈에 조회

---

### 테이블 2: 건물 상세 정보 (건물 단위)

> API 1 단독 (pnu 1개에 건물 N개 가능)

| 컬럼 | 설명 |
|------|------|
| pnu | 필지고유번호 (FK) |
| gisIdntfcNo | GIS건물통합식별번호 (PK) |
| buldIdntfcNo | 건물식별번호 |
| buldNm | 건물명 |
| mainPrposCodeNm | 주요용도명 |
| detailPrposCodeNm | 세부용도명 |
| buldPrposClCodeNm | 건물용도분류명 (주거용, 상업용 등) |
| strctCodeNm | 건축물구조명 |
| buldPlotAr | 건물대지면적(㎡) |
| buldBildngAr | 건물건축면적(㎡) |
| buldTotar | 건물연면적(㎡) |
| measrmtRt | 용적율(%) |
| btlRt | 건폐율(%) |
| buldHg | 건물높이(m) |
| groundFloorCo | 지상층수 |
| undgrndFloorCo | 지하층수 |
| prmisnDe | 허가일자 |
| useConfmDe | 사용승인일자 |

**활용**: 건물별 물리적 속성, 용도, 규모 분석

---

### 테이블 3: 토지 가치 이력 (연도별 공시지가 추적)

> API 3 (stdrYear 파라미터로 연도별 반복 조회)

| 컬럼 | 설명 |
|------|------|
| pnu | 필지고유번호 (PK) |
| stdrYear | 기준연도 (PK) |
| pblntfPclnd | 공시지가(원/㎡) |
| pblntfDe | 공시일자 |
| stdLandAt | 표준지여부 |

**활용**: 특정 필지의 연도별 지가 변동 추이 분석, 투자 가치 판단

---

### 테이블 4: 주소-필지 매핑 (주소 검색 결과)

> API 4 → pnu 변환 → API 1,2,3 연계

| 컬럼 | 출처 | 설명 |
|------|------|------|
| bdMgtSn | API 4 | 건물관리번호 (PK) |
| roadAddr | API 4 | 전체 도로명주소 |
| jibunAddr | API 4 | 지번주소 |
| zipNo | API 4 | 우편번호 |
| siNm | API 4 | 시도명 |
| sggNm | API 4 | 시군구명 |
| emdNm | API 4 | 읍면동명 |
| bdNm | API 4 | 건물명 |
| pnu | 변환 | 필지고유번호 (admCd + 산여부 + 지번본번 + 지번부번으로 조합) |

**활용**: 사용자가 주소로 검색 → pnu 변환 → 나머지 API로 상세 정보 조회

---

### 테이블 5: 토지이용규제 통합 (지역지구별 규제+법령)

> API 5 + API 6 조인 (areaCd + UCODE 기준)

| 컬럼 | 출처 | 설명 |
|------|------|------|
| areaCd | 공통 | 시군구코드 (PK) |
| UCODE | 공통 | 지역지구코드 (PK) |
| UNAME | API 5,6 | 지역지구명 |
| LAW_CONTENTS | API 5 | 규제 법령 내용 |
| LAW_LEVEL | API 5 | 법령 표기 순서 (조/항/호/목) |
| LAW_FULL_CD | API 5 | 법령 내용 코드 |
| UCODE_REF_LAW_CD | API 6 | 지역지구 법령코드 |
| ACT_NM | API 6 | 행위명 |
| REG_NM | API 6 | 가능여부 |
| NODE_DESC | API 6 | 토지이용명 |
| LU_REF_LAW_NM1 | API 6 | 참조 법령조항 |

**활용**: 특정 지역의 어떤 행위가 가능한지, 근거 법령은 무엇인지 통합 조회

---

### 테이블 6: 필지별 규제 현황 (전체 통합)

> 테이블 1 + 테이블 5 (ldCode → areaCd 매핑 + 토지이용계획 API로 해당 필지의 지역지구 확인)

| 컬럼 | 출처 | 설명 |
|------|------|------|
| pnu | 테이블 1 | 필지고유번호 (PK) |
| ldCodeNm | 테이블 1 | 법정동명 |
| lndpclAr | 테이블 1 | 토지면적(㎡) |
| pblntfPclnd | 테이블 1 | 공시지가(원/㎡) |
| posesnSeCodeNm | 테이블 1 | 소유구분 |
| UNAME | 테이블 5 | 적용 지역지구명 |
| 허용행위 목록 | 테이블 5 | 해당 지역지구의 가능한 행위 |
| 규제법령 | 테이블 5 | 근거 법령 |
| mainPrposCodeNm | 테이블 1 | 건물 주요용도 |


**관련 규제 정보와 시군구코드, 지역지구코드 매핑**
pnu - 앞 5자리로 areaCd 추출 가능 OR 복원 가능
pnu → 토지이용계획확인원 API로 해당 필지의 UCODE 목록 확보
areaCd + UCODE → API 5,6 호출

---

## 규제 중첩 처리 (구현 시 주의사항)

### 하나의 필지에 지역지구가 여러 개 중첩됨

API 7로 pnu를 조회하면 하나의 필지에 여러 UCODE가 반환될 수 있다.

```
필지 A (pnu: 1165010800113320000)
├── UQA123  제3종일반주거지역     ← 용도지역
├── UBA100  자연경관지구          ← 용도지구
├── UGD100  도시자연공원구역      ← 용도구역
└── UEA205  학교환경정화구역      ← 다른법령 구역
```

### 각 UCODE마다 별도로 규제를 조회해야 함

UCODE별로 API 5(법령), API 6(행위제한)을 각각 호출 → 결과를 모두 수집

### 최종 판단: 가장 제한적인 규제가 적용됨

중첩된 모든 지역지구의 규제를 교차 비교하여 **가장 엄격한 것**이 해당 필지의 실제 규제가 된다.

```
예시: "창고 건축" 가능 여부

제3종일반주거지역  → 창고 건축: 가능 (바닥면적 2000㎡ 미만)
자연경관지구      → 창고 건축: 조건부허용
학교환경정화구역   → 창고 건축: 금지

→ 최종 결과: 금지 (가장 제한적인 것이 적용)
```

### 구현 필요 사항

1. **UCODE 전체 수집**: API 7로 필지의 모든 지역지구 목록 확보
2. **규제 개별 조회**: 각 UCODE마다 API 5, 6 호출하여 법령/행위제한 수집
3. **교차 판단 로직**: 동일 행위(ACT_NM)에 대해 모든 UCODE의 가능여부(REG_NM)를 비교하여 가장 제한적인 결과 도출
   - 금지 > 조건부허용 > 허용 (금지가 하나라도 있으면 금지)
   - 조건부허용의 경우 QNODE_CONDS(조건제한 예외사항)도 함께 고려
4. **결과 표시**: 최종 가능여부 + 근거 지역지구명 + 근거 법령 조항을 함께 제공