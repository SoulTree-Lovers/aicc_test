# KB 재색인 운영 체크리스트

## 사전 점검
- 입력 경로(`data/kb` 또는 지정 경로)에 PDF/HTML/CSV 파일이 준비되어 있는지 확인한다.
- 개인정보 마스킹 대상(전화번호/주민번호/계좌번호) 샘플 문서를 준비해 마스킹 결과를 검증한다.
- 메타데이터 필수 필드(`category`, `effective_date`, `policy_version`, `source_url`, `last_verified_at`)가 누락되지 않도록 소스 정책을 점검한다.

## 실행
1. `scripts/reindex_kb.sh` 실행
2. 출력된 `Indexed chunks: N` 확인
3. 실패 시 입력 포맷 및 의존성(`pypdf`, `beautifulsoup4`) 설치 여부 확인

## 사후 검증
- 벡터 인덱스 샘플 조회로 FAQ/매뉴얼/공지 문서가 검색되는지 확인한다.
- 마스킹 토큰(`[MASKED_PHONE]`, `[MASKED_RRN]`, `[MASKED_ACCOUNT]`)이 적용되었는지 랜덤 샘플을 검토한다.
- `effective_date`, `policy_version`, `last_verified_at` 값이 최신 운영 기준과 일치하는지 확인한다.
- 재색인 일시, 대상 데이터셋, 검증 결과를 운영 로그에 기록한다.
