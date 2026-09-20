# Installation

Tested with Python 3.12.
git clone https://github.com/arvened/openosint-pro.git
cd openosint-pro
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest -q

The full test run takes several minutes. See README.md for the current project status and known limitations.