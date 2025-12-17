# Private AI CI

A secure, AI-driven CI/CD orchestrator that uses agents to scan, architect, and run tests in a sandboxed environment.

## Structure

- **app/**: Main application logic (Flask/FastAPI listener, config, utils).
- **security/**: Security modules for webhook validation (HMAC) and sandboxing (gVisor/Docker).
- **agents/**: AI agents for scanning repos, architecting tests, and running builds.
- **templates/**: System prompts for the AI agents.

## Setup

1. Copy `.env` and fill in your secrets.
2. Run `docker-compose up --build`.

## Workflow

1. GitHub Webhook triggers the `main.py` listener.
2. `hmac_check.py` validates the request.
3. `scanner.py` agent identifies the stack.
4. `architect.py` agent plans the build/test strategy.
5. `runner.py` executes the plan in a secure container via `sandbox.py`.
