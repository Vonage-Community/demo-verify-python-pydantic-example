from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from vonage import Auth, Vonage
from vonage_verify import EmailChannel, VerifyRequest
from config import settings

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Store request_id in memory
verify_sessions = {}

client = Vonage(
    Auth(
        application_id=settings.vonage_application_id,
        private_key=settings.vonage_private_key_path,
    )
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.post("/send-code", response_class=HTMLResponse)
async def send_code(request: Request, email: str = Form(...)):
    verify_request = VerifyRequest(
        brand=settings.verify_brand_name,
        workflow=[
            EmailChannel(to=email),
        ],
        channel_timeout=60,
        code_length=5,
    )
    response = client.verify.start_verification(verify_request)
    # Store the request_id against the email
    verify_sessions[email] = response.request_id

    return templates.TemplateResponse(
        request, "verify.html", {"request": request, "email": email}
    )


@app.post("/check-code", response_class=HTMLResponse)
async def check_code(request: Request, email: str = Form(...), code: str = Form(...)):
    request_id = verify_sessions.get(email)

    if not request_id:
        return templates.TemplateResponse(
            request,
            "verify.html",
            {
                "request": request,
                "email": email,
                "error": "Session expired. Please try again.",
            },
        )

    try:
        client.verify.check_code(request_id=request_id, code=code)
        # Clean up session
        del verify_sessions[email]
        return templates.TemplateResponse(request, "success.html", {"request": request})
    except Exception as e:
        return templates.TemplateResponse(
            request,
            "verify.html",
            {
                "request": request,
                "email": email,
                "error": "Invalid code. Please try again.",
            },
        )
