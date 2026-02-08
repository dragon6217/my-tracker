# # 1. 파이썬 3.12 슬림 버전 사용
# FROM python:3.12-slim

# # 2. uv 설치 (가장 빠른 패키지 관리자)
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ENV UV_SYSTEM_PYTHON=1

# # 3. 작업 디렉토리 설정
# WORKDIR /app

# # 4. 의존성 파일 복사 및 설치 (캐싱 활용으로 빌드 속도 향상)
# COPY pyproject.toml uv.lock ./
# RUN uv sync --frozen --no-cache --no-install-project

# # 5. 소스 코드 전체 복사
# # COPY . .

# # 6. FastAPI 실행 (요청하신 9998 포트)
# # --reload: 코드 수정 시 실시간 반영
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9998", "--reload"]


FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# [핵심 1] 가상환경을 만들지 않고 시스템 파이썬(/usr/local/bin)에 직접 설치합니다.
ENV UV_SYSTEM_PYTHON=1

WORKDIR /setup
COPY pyproject.toml uv.lock ./

# [핵심 2] uv pip를 사용하여 시스템 전체에 패키지를 깝니다. 
# 이렇게 하면 /app 폴더를 마운트로 덮어씌워도 uvicorn은 시스템 영역에 살아남습니다.
RUN uv pip install .

# 실제 코드가 돌아갈 곳
WORKDIR /app

# 이제 uvicorn은 /usr/local/bin/uvicorn 에 안전하게 존재합니다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9998", "--reload"]