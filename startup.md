
# Open WebUI Local Startup Guide

This guide starts the Open WebUI backend and frontend locally for development and
testing, including university email OTP authentication.

## Prerequisites

- macOS or Linux
- Python 3.11 or 3.12
- Node.js and npm
- `uv`
- An Open WebUI `.env` file

Run all commands from the repository root:

```bash
cd /Users/shaguntembhurne/owui/open-webui
```

## First-time backend setup

Open WebUI requires Python 3.11 or 3.12. Check the active version:

```bash
python3 --version
```

If needed, install Python 3.12 through `uv`:

```bash
uv python install 3.12
```

Create the project virtual environment:

```bash
uv venv --python 3.12
```

Install the Python dependencies without installing the local project package:

```bash
uv sync --dev --python 3.12 --no-install-project
```

The `--no-install-project` option is intentional. The local package build hook
also runs the full frontend production build, which is not required for local
development.

Activate the environment:

```bash
source .venv/bin/activate
```

Verify that the virtual environment is active:

```bash
python --version
which python
```

The Python path should be inside:

```text
/Users/shaguntembhurne/owui/open-webui/.venv/
```

## First-time frontend setup

From the repository root:

```bash
npm install
```

Run this only when frontend dependencies are missing or `package.json` changes.

## Environment configuration

Create a local environment file if one does not already exist:

```bash
cp .env.example .env
```

Never commit `.env` or share its contents.

For OTP sign-in, configure the SMTP and university-domain values in `.env`.
Use a Gmail App Password rather than your normal Gmail password:

```dotenv
OTP_AUTH_ENABLED=true
OTP_SMTP_HOST=smtp.gmail.com
OTP_SMTP_PORT=587
OTP_SMTP_USERNAME=your-email@gmail.com
OTP_SMTP_PASSWORD=your-gmail-app-password
OTP_EMAIL_FROM=your-email@gmail.com
OTP_SMTP_USE_TLS=true

OTP_LENGTH=6
OTP_EXPIRY_SECONDS=300
OTP_MAX_ATTEMPTS=5
OTP_RESEND_COOLDOWN_SECONDS=60

OTP_ALLOWED_EMAIL_DOMAINS=students.mituniversity.edu.in,mituniversity.edu.in
```

To allow OTP to create a new Open WebUI account during local testing, also set:

```dotenv
ENABLE_SIGNUP=true
```

After changing `.env`, restart the backend. Existing accounts can use OTP
without creating a new account. New OTP accounts receive the standard `user`
role; OTP cannot grant administrator privileges.

## Start the backend

Use Terminal 1:

```bash
cd /Users/shaguntembhurne/owui/open-webui
source .venv/bin/activate
cd backend
./dev.sh
```

If the script is not executable:

```bash
cd /Users/shaguntembhurne/owui/open-webui
source .venv/bin/activate
cd backend
bash dev.sh
```

The backend runs at:

```text
http://localhost:8080
```

The development script starts Uvicorn with reload enabled and applies the
database startup/migration logic used by the application.

Check backend health from another terminal:

```bash
curl http://localhost:8080/health
```

Check whether OTP is enabled:

```bash
curl http://localhost:8080/api/v1/auths/otp/config
```

## Start the frontend

Use Terminal 2:

```bash
cd /Users/shaguntembhurne/owui/open-webui
npm run dev
```

The frontend normally runs at:

```text
http://localhost:5173
```

Open the login page:

```text
http://localhost:5173/auth
```

The Vite development proxy forwards backend requests to
`http://localhost:8080`.

## Test login

### Password login

1. Open `http://localhost:5173/auth`.
2. Sign in with an existing email and password.
3. Confirm that the application, chat history, protected requests, and
   navigation work.

### University email OTP login

1. Select the university email OTP sign-in option.
2. Enter an email whose domain is listed in `OTP_ALLOWED_EMAIL_DOMAINS`.
3. Select **Send sign-in code**.
4. Enter the code received by email.
5. Select **Verify and sign in**.
6. Confirm that the normal Open WebUI application opens.
7. Test a protected action, chat request, and logout.

For a new account, `ENABLE_SIGNUP=true` must be enabled. If it is disabled,
the backend returns `Account registration is disabled.` for unknown email
addresses. Existing users are not affected by this setting.

## Stop the services

In each terminal running a service, press:

```text
Ctrl+C
```

## Troubleshooting

### `uv sync` appears stuck at `Building open-webui`

Use the development installation command instead:

```bash
uv sync --dev --python 3.12 --no-install-project
```

Running `uv sync --dev` without `--no-install-project` invokes the package build
hook, which runs `npm install --force` and `npm run build`.

### Backend import or dependency errors

Confirm the virtual environment is active:

```bash
source .venv/bin/activate
which python
python --version
```

Then synchronize dependencies:

```bash
uv sync --dev --python 3.12 --no-install-project
```

### Port 8080 is already in use

Check the process:

```bash
lsof -nP -iTCP:8080 -sTCP:LISTEN
```

Start the backend on another port:

```bash
cd /Users/shaguntembhurne/owui/open-webui
source .venv/bin/activate
cd backend
PORT=8081 ./dev.sh
```

Start the frontend with the matching backend URL:

```bash
cd /Users/shaguntembhurne/owui/open-webui
WEBUI_BACKEND_URL=http://localhost:8081 npm run dev
```

### OTP email is not received

Check the backend terminal for SMTP errors. Common causes include:

- Gmail 2-Step Verification is not enabled.
- An App Password was not created.
- The normal Gmail password was used instead of an App Password.
- The SMTP sender and username do not match.
- The recipient domain is not in `OTP_ALLOWED_EMAIL_DOMAINS`.
- The resend cooldown has not elapsed.

Do not log or paste SMTP passwords, OTP values, or `.env` contents.


### changes done in Backend
/owui/open-webui/backend/open_webui/models/otp.py
/owui/open-webui/backend/open_webui/routers/auths.py
/owui/open-webui/backend/open_webui/migrations/versions/otp_challenge_table.py
/owui/open-webui/backend/open_webui/test/test_otp_auth.py
/owui/open-webui/backend/open_webui/env.py (it is mentioned there properly basically as uni email otp auth named)
/owui/open-webui/.env.example

### changes done in Frontend
/owui/open-webui/src/lib/apis/auths/index.ts
/owui/open-webui/src/routes/auth/+page.svelte