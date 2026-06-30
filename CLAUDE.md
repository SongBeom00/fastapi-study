# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트

FastAPI 학습용 프로젝트. PostgreSQL(asyncpg) 기반의 비동기 API이며 Redis 캐싱을 사용한다. 패키지 매니저는 **uv**, Python >= 3.12.

## 명령어

```bash
uv sync                              # pyproject.toml / uv.lock 기준으로 의존성 설치
uv run uvicorn app.main:app --reload # 개발 서버 실행 (http://127.0.0.1:8000, 문서 /docs)
uv run python -m app.main            # 대체 실행 (진입점 app/main.py, host 0.0.0.0)
uv run python -c "from app.main import app"  # 빠른 스모크 테스트: 앱 + 전체 라우터 import 검증
```

테스트 스위트, 린터, 마이그레이션 도구는 설정되어 있지 않다. `test_main.http`는 JetBrains HTTP 클라이언트용 수동 요청 몇 개일 뿐 자동화 테스트가 아니다.

## 환경 변수

- `.env` (git에서 제외, `app/db/database.py`에서 python-dotenv로 로드)에 `DATABASE_CONN`을 반드시 정의해야 한다 — SQLAlchemy **async** URL (예: `postgresql+asyncpg://...`). 미설정 시 import 단계에서 `RuntimeError` 발생.
- Redis는 `redis://localhost:6379/0`로 접근 가능해야 한다 (`app/main.py`의 `lifespan` 핸들러에 하드코딩됨).

## 아키텍처

`app/` 아래 3계층 구조이며, 리소스별로 모듈이 나뉜다 (`board`, `user`):

- **`routes/`** — `APIRouter` (HTTP 관심사 전담). DB 커넥션은 `Depends(database.context_get_conn)`로, Redis는 `request.app.state.redis`로 받는다. `app/main.py`에서 `app.include_router(...)`로 등록한다.
- **`services/`** — 비즈니스 로직 + **원시 SQL** (`sqlalchemy.text()`). **ORM 모델은 없다.** 직접 작성한 SQL과 바인드 파라미터로 테이블에 접근하고, 컬럼명 기준으로 스키마에 매핑한다. DB 테이블(`board`, `users`)은 이미 존재한다고 가정하며 이 저장소 외부에서 관리된다 — 컬럼이 불명확한 곳은 현재 코드가 임의로 가정하고 있으니(예: `users`에 `id, name, email, tier, created_at`) 실제 DB와 대조해 확인할 것.
- **`schemas/`** — Pydantic 모델. 리소스별 컨벤션: 요청·응답용 `Create` / `Update` / `Delete` / `Response` 모델을 분리하고, 내부용 `*Data` 모델을 둔다 (`BoardData`는 Pydantic `@dataclass`).

`db/database.py`가 공유 `AsyncEngine` 하나를 소유한다 (pool_size=10, pool_recycle=300). `context_get_conn`은 요청마다 커넥션을 yield하는 async-generator 의존성이며, `async with engine.connect()`가 정리를 담당하므로 수동으로 close하지 말 것.

### 따라야 할 컨벤션

- **트랜잭션:** 쓰기 작업은 쿼리를 `async with conn.begin():`로 감싸 커밋을 보장한다. 읽기는 `conn.execute`를 직접 호출하며 별도 트랜잭션을 두지 않는다.
- **에러 처리:** 서비스는 DB 작업을 `try/except SQLAlchemyError`로 감싸 `HTTPException(503)`로 재발생시킨다. 조회 결과가 없으면 `HTTPException(404)`. 이 예외들은 라우트가 아니라 서비스 계층에서 raise한다.
- **Redis 캐싱 (`routes/user.py` 참고):** 읽기 경로는 먼저 `user:profile:{id}`를 확인하고(캐시 히트 → 파싱한 JSON 반환), 없으면 DB로 폴백한 뒤 `rd.set(..., ex=CACHE_TTL)`로 저장한다. 쓰기 경로(`update`)는 `rd.delete(...)`로 키를 **무효화**해 다음 읽기 때 다시 캐싱되게 한다 — 변경(mutation) 기능을 추가할 때 이 읽기/쓰기 캐시 계약을 유지할 것.

`python_basic/`은 앱과 무관한 학습/연습용 코드다.
