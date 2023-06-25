import logging

from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from authlib.integrations.starlette_client import OAuth

from config import settings


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

app = FastAPI()

origins = [
    'http://localhost:8000',
    'http://127.0.0.1:8000'
]

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'])

app.add_middleware(SessionMiddleware, secret_key=settings.OIDC_CLIENT_SECRET)

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

oauth = OAuth()

oauth.register(
    name='keycloak',
    client_id=settings.OIDC_CLIENT_ID,
    client_secret=settings.OIDC_CLIENT_SECRET.get_secret_value(),
    server_metadata_url=settings.OIDC_METADATA_URL,
    client_kwargs={
        'scope': settings.OIDC_SCOPE,
    }
)


@app.get('/login/')
async def login(request: Request):
    redirect_uri = f'{settings.BASE_URL}/auth/'
    return await oauth.keycloak.authorize_redirect(request, redirect_uri)


@app.get('/auth/', response_class=RedirectResponse)
async def auth(request: Request):
    token = await oauth.keycloak.authorize_access_token(request)

    user = token.get('userinfo')
    request.session['user'] = user

    return RedirectResponse('/')


@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get('user', None)
    if user is not None:
        return templates.TemplateResponse('home.html', {'request': request, 'user': dict(user)})
    else:
        return RedirectResponse(f'{settings.BASE_URL}/login/')
