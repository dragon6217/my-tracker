from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- [DB 설정] ---
# 도커 컴포즈에서 설정한 db 서비스 이름과 계정 정보를 사용합니다.
DATABASE_URL = "postgresql://user:pass@db:5432/dbname"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- [데이터 모델링] ---
# 엑셀 시트의 컬럼을 정의한다고 생각하세요.
class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)

# 서버 시작 시 테이블이 없으면 자동으로 생성합니다.
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# DB 세션 주입 함수 (FastAPI의 Depends 기능 활용)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- [Routes] ---

# 1. 메인 화면: DB에서 저장된 모든 이슈를 읽어서 보여줍니다.
@app.get("/", response_class=HTMLResponse)
async def list_issues(request: Request, db: Session = Depends(get_db)):
    issues = db.query(Issue).all()
    return templates.TemplateResponse("index.html", {"request": request, "issues": issues})

# 2. 이슈 추가: 사용자가 입력한 제목을 DB에 저장합니다.
@app.post("/add-issue", response_class=HTMLResponse)
async def add_issue(issue_title: str = Form(...), db: Session = Depends(get_db)):
    # DB에 저장
    new_issue = Issue(title=issue_title)
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    
    # htmx를 위해 '새로 추가된 항목'의 HTML 조각만 리턴합니다.
    # ID를 동적으로 넣어 삭제 버튼이 특정 이슈를 지칭하게 합니다.
    return f"""
    <div id="issue-{new_issue.id}" class="flex justify-between items-center bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500 mb-2">
        <span class="text-gray-700 font-medium">{new_issue.title}</span>
        <button class="text-red-500 hover:text-red-700 text-sm font-bold"
                hx-delete="/delete-issue/{new_issue.id}" 
                hx-target="#issue-{new_issue.id}" 
                hx-swap="outerHTML">
            삭제
        </button>
    </div>
    """

# 3. 이슈 삭제: 특정 ID를 가진 데이터를 DB에서 지웁니다.
@app.delete("/delete-issue/{issue_id}", response_class=HTMLResponse)
async def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if issue:
        db.delete(issue)
        db.commit()
    return ""  # 화면에서 삭제하기 위해 빈 문자열 리턴