# Contributing to OpenOSINT Pro

OpenOSINT Pro is an early-stage prototype. Small, focused contributions are welcome.

## Setup

Tested with Python 3.12.

```bash
git clone https://github.com/YOUR_USERNAME/openosint-pro.git
cd openosint-pro
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest -q -m "not slow"
```

Tests marked `slow` need a running Redis server.

## Making changes

1. Fork the repository and create a branch from main.
2. Keep changes small and focused. Add or update tests for what you change.
3. Tests must not depend on live network services. Use mocks.
4. Follow PEP 8.
5. Use clear commit messages, for example feat:, fix:, docs:, test:, refactor:, ci:.
6. Open a pull request against main. The GitHub Actions tests must pass.

## Use of generative AI

AI coding assistants are allowed, but you must understand and be able to explain everything you submit. If a commit adds AI-generated code, say so in the commit message: name the model (and version) and summarise the prompt, for example:

    test: add WHOIS parser tests for .de domains

    Generated with Claude (claude-opus-5-5). Prompt: "Write pytest tests
    for the WHOIS parser using sample .de responses."
    Reviewed and corrected by hand.

## Responsible use

Do not commit personal data collected with these tools, and do not add features whose main purpose is profiling individuals.

## Reporting issues

Use GitHub Issues. For security problems, please do not open a public issue; contact the maintainer at hello@arvend.io.
