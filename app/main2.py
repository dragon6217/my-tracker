from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form

app = FastAPI()

# templates 폴더 위치 지정
templates = Jinja2Templates(directory="templates")





@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    # 여기서 context에 담긴 데이터가 HTML의 {{ }} 안으로 들어갑니다.
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"message": "Tailwind + htmx 세상에 오신 걸 환영합니다!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"}
    )





@app.get("/hello", response_class=HTMLResponse)
async def hello():
    # 전체 HTML이 아니라 딱 이 한 줄만 보냅니다.
    return "<span>서버에서 보낸 새로운 메시지입니다!</span>"





@app.post("/add-issue", response_class=HTMLResponse)
async def add_issue(issue_title: str = Form(...)):
    # div에 'issue-item'이라는 클래스를 추가해서 타겟팅하기 쉽게 만듭니다.
    return f"""
    <div class="issue-item flex justify-between items-center bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500 mb-2">
        <span class="text-gray-700 font-medium">{issue_title}</span>
        <button class="text-red-500 hover:text-red-700 text-sm font-bold"
                hx-delete="/delete-issue" 
                hx-target="closest .issue-item" 
                hx-swap="outerHTML">
            삭제
        </button>
    </div>
    """

@app.delete("/delete-issue", response_class=HTMLResponse)
async def delete_issue():
    # 서버에서 실제로 DB를 지웠다고 가정하고, 
    # 브라우저에는 '빈 문자열'을 보냅니다. 
    # 빈 문자열이 전달되면 htmx는 타겟 요소를 '아무것도 없는 것'으로 갈아끼워 버립니다. (즉, 사라짐)
    return ""










