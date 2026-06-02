#!/usr/bin/env python3
"""
KRCERT CTAS - 위협정보 공유 CSV 자동 다운로드 스크립트
매일 cron 등으로 실행하여 최신 CSV 파일을 자동 저장합니다.

사용법:
    python ctas_download.py
    python ctas_download.py --date 20240601   # 특정 날짜 지정
"""

import requests
import os
import sys
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# ─────────────────────────────────────────
#  설정 (본인 계정으로 수정하세요)
# ─────────────────────────────────────────
CONFIG = {
    "username": "jimin2977",      # ← CTAS 아이디
    "password": "fbwlals505!",        # ← CTAS 비밀번호
    "base_url": "https://ctas.krcert.or.kr",
    "login_page_url": "https://ctas.krcert.or.kr/index",
    "login_post_url": "https://ctas.krcert.or.kr/login",
    "download_dir": "./ctas_downloads",      # ← 저장 폴더 경로
    "days_back": 1,                          # 몇 일 전 파일까지 시도할지 (실패 시 재시도용)
}

# ─────────────────────────────────────────
#  로깅 설정
# ─────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG로 변경하여 더 자세한 정보 출력
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("ctas_download.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def create_session() -> requests.Session:
    """세션 생성 및 공통 헤더 설정"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": CONFIG["base_url"],
    })
    return session


def login(session: requests.Session) -> bool:
    """CTAS 로그인 수행"""
    log.info("로그인 시도 중...")

    # 1) 로그인 페이지에서 CSRF 토큰 등 쿠키 수집
    try:
        log.info(f"로그인 페이지 접근: {CONFIG['login_page_url']}")
        resp = session.get(CONFIG["login_page_url"], timeout=15, verify=False)
        log.info(f"로그인 페이지 응답: {resp.status_code}")
        resp.raise_for_status()
    except requests.RequestException as e:
        log.error(f"❌ 로그인 페이지 접근 실패: {e}")
        return False

    # 2) 로그인 POST
    payload = {
        "userId": CONFIG["username"],
        "userPassword": CONFIG["password"],
    }

    # CSRF 토큰이 있을 경우 자동으로 쿠키에 포함됨 (requests.Session이 처리)
    try:
        log.info(f"로그인 POST 시도: {CONFIG['login_post_url']}")
        resp = session.post(
            CONFIG["login_post_url"],
            data=payload,
            timeout=15,
            allow_redirects=True,
            verify=False,
        )
        log.info(f"로그인 응답 상태코드: {resp.status_code}")
        log.info(f"로그인 후 URL: {resp.url}")
        log.debug(f"응답 길이: {len(resp.text)} bytes")
        resp.raise_for_status()
    except requests.RequestException as e:
        log.error(f"❌ 로그인 POST 실패: {e}")
        return False

    # 로그인 성공 여부 확인 (URL 리다이렉트 또는 응답 내용으로 판별)
    if "logout" in resp.text.lower() or "로그아웃" in resp.text:
        log.info("✅ 로그인 성공")
        return True
    elif "login" in resp.url.lower():
        log.error("❌ 로그인 실패 — 아이디/비밀번호를 확인하세요")
        log.debug(f"응답 URL: {resp.url}")
        return False
    else:
        # 리다이렉트 후 대시보드 등으로 이동했으면 성공으로 간주
        log.info(f"✅ 로그인 완료 (현재 URL: {resp.url})")
        return True


def build_download_url(date_str: str) -> list[str]:
    """
    날짜 기반 다운로드 URL 후보 목록 반환.
    CTAS의 실제 엔드포인트 패턴에 맞게 수정하세요.
    """
    base = CONFIG["base_url"]
    return [
        # 패턴 1: 날짜 파라미터 방식
        f"{base}/threatnew/worker/sharesCombine/download?date={date_str}",
        # 패턴 2: 파일명 직접 방식
        f"{base}/threatnew/worker/sharesCombine/export/{date_str}.csv",
        # 패턴 3: 최신 파일 다운로드 (날짜 무관)
        f"{base}/threatnew/worker/sharesCombine/download/latest",
    ]


def download_csv(session: requests.Session, date_str: str) -> bool:
    """지정 날짜의 CSV 파일 다운로드"""
    save_dir = Path(CONFIG["download_dir"])
    save_dir.mkdir(parents=True, exist_ok=True)

    urls = build_download_url(date_str)

    for url in urls:
        log.info(f"다운로드 시도: {url}")
        try:
            resp = session.get(url, timeout=30, stream=True)

            # 200 OK + CSV 또는 octet-stream 응답인지 확인
            content_type = resp.headers.get("Content-Type", "")
            if resp.status_code == 200 and (
                "csv" in content_type
                or "octet-stream" in content_type
                or "text/" in content_type
            ):
                # Content-Disposition에서 파일명 추출 시도
                disposition = resp.headers.get("Content-Disposition", "")
                if "filename=" in disposition:
                    filename = disposition.split("filename=")[-1].strip().strip('"')
                else:
                    filename = f"ctas_{date_str}.csv"

                save_path = save_dir / filename
                with open(save_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)

                file_size = save_path.stat().st_size
                log.info(f"✅ 저장 완료: {save_path} ({file_size:,} bytes)")
                return True

            elif resp.status_code == 404:
                log.warning(f"파일 없음 (404): {url}")
            elif resp.status_code == 403:
                log.warning(f"접근 거부 (403) — 로그인 세션 만료 가능성: {url}")
            else:
                log.warning(f"예상치 못한 응답 {resp.status_code}: {url}")

        except requests.RequestException as e:
            log.warning(f"요청 오류: {e}")

    log.error(f"❌ {date_str} 날짜의 CSV 다운로드 실패 — 모든 URL 시도 소진")
    return False


def main():
    parser = argparse.ArgumentParser(description="KRCERT CTAS CSV 자동 다운로드")
    parser.add_argument(
        "--date",
        help="다운로드 날짜 (YYYYMMDD 형식). 기본값: 오늘",
        default=None,
    )
    args = parser.parse_args()

    # 날짜 결정
    if args.date:
        target_date = datetime.strptime(args.date, "%Y%m%d")
    else:
        target_date = datetime.now() - timedelta(days=CONFIG["days_back"] - 1)

    date_str = target_date.strftime("%Y%m%d")
    log.info(f"=== CTAS CSV 다운로드 시작 | 대상 날짜: {date_str} ===")

    # 세션 생성 및 로그인
    session = create_session()
    if not login(session):
        log.error("로그인에 실패하여 종료합니다.")
        sys.exit(1)

    # CSV 다운로드
    success = download_csv(session, date_str)

    if success:
        log.info("=== 완료 ===")
        sys.exit(0)
    else:
        log.error("=== 다운로드 실패 ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
