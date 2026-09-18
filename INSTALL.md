# Installation Guide

Complete step-by-step guide to install and run OpenOSINT Pro.

## System Requirements

- **Python:** 3.10 or higher
- **OS:** Linux, macOS, or Windows
- **RAM:** 512 MB minimum (2 GB recommended)
- **Disk Space:** 500 MB for dependencies

## Quick Install (5 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/arvened/openosint-pro.git
cd openosint-pro
2. Create Virtual Environment

On Linux/macOS:
python3 -m venv venv
source venv/bin/activate
On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
On Windows (Command Prompt):
python -m venv venv
venv\Scripts\activate.bat
3. Install Dependencies
pip install --upgrade pip
pip install httpx pydantic redis pytest pytest-asyncio pytest-cov

4. Verify Installation
python -c "import httpx, pydantic; print('✓ Core dependencies installed')"
5. Run Tests
pytest -v
Expected output:
70+ tests passed
Coverage: 61%
Detailed Installation

Prerequisites

Python 3.10+

Check your Python version:
python --version
If you need to install Python:

Linux (Ubuntu/Debian):
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv python3-pip
macOS (Homebrew):
brew install python@3.10

Windows:
Download from python.org

Virtual Environment

Virtual environments isolate project dependencies. Always use them.
# Create
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Deactivate (all platforms)
deactivate
Step-by-Step Setup

Step 1: Clone Repository
git clone https://github.com/arvened/openosint-pro.git
cd openosint-pro
Verify you see these files:
README.md
CHANGELOG.md
LICENSE
scraping.py
whois.py
dns_recon.py
middleware.py
engine.py
redis_cache.py
test_*.py

Step 2: Python Virtual Environment
# Create environment
python3 -m venv venv

# Activate environment
source venv/bin/activate  # Linux/macOS
# OR
.\venv\Scripts\Activate.ps1  # Windows PowerShell

You should see (venv) in your terminal prompt.

Step 3: Upgrade pip
pip install --upgrade pip setuptools wheel
Step 4: Install Core Dependencies
pip install httpx>=0.24.0 pydantic>=2.0.0 redis>=4.5.0
Step 5: Install Testing Dependencies
pip install pytest>=7.4.0 pytest-asyncio>=0.21.0 pytest-cov>=4.1.0
Step 6: Install Optional Dependencies
pip install dnspython>=2.3.0 beautifulsoup4>=4.12.0
Step 7: Verify Installation
python -c "import httpx, pydantic, redis; print('✓ All imports successful')"
Step 8: Run Tests
# All tests
pytest -v

# With coverage
pytest -v --cov=. --cov-report=html

# Specific test file
pytest test_scraping.py -v

# Specific test function
pytest test_whois.py::TestWHOISLookup::test_lookup -v
Configuration

Environment Variables

Create .env file in project root:
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
API_PORT=8000
LOG_LEVEL=INFO
Redis Configuration (Optional)

Using Redis (Recommended)

Install Redis:

Linux (Ubuntu/Debian):
sudo apt-get install redis-server
sudo systemctl start redis-server
macOS (Homebrew):
brew install redis
brew services start redis
Windows:
Download from redis.io or use WSL

Test Redis connection:
redis-cli ping
# Should return: PONG
Without Redis (In-Memory Cache)

The system falls back to in-memory caching automatically if Redis is unavailable.

Starting Development

Basic Workflow

	1.	Activate virtual environment:
source venv/bin/activate  # Linux/macOS
2.	Run tests:
pytest -v
3.	Write code:
Edit Python files as needed
	4.	Run tests again:
pytest -v --cov=.
5.	Commit changes:
git add .
git commit -m "feat: your feature description"
git push origin main
Code Quality Tools

Format code:
pip install black
Type checking:
pip install mypy
mypy scraping.py whois.py dns_recon.py middleware.py engine.py redis_cache.py
Linting:
pip install flake8
flake8 .
Troubleshooting

Problem: ModuleNotFoundError: No module named 'httpx'

Solution: Make sure your virtual environment is activated

source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows PowerShell
Then reinstall dependencies:
pip install httpx pydantic redis
Problem: pytest: command not found

Solution: Install pytest in virtual environment
# Make sure venv is activated
pip install pytest pytest-asyncio pytest-cov
Problem: Connection refused when running tests

Solution: Redis is optional. Tests use in-memory fallback.
# Just run tests - they'll use in-memory cache
pytest -v
If you want Redis working:
redis-server  # Start Redis first
pytest -v     # Then run tests
Problem: Python 3.10+ not found

Solution: Install Python 3.10 or higher

Check installed versions:
python --version
python3 --version
python3.10 --version
Use specific version:
python3.10 -m venv venv
Problem: Tests failing on Windows

Solution: Use PowerShell instead of Command Prompt
.\venv\Scripts\Activate.ps1
pytest -v

Or


















black .




















































