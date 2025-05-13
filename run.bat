@echo off
echo Checking Python installation...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python could not be found. Please install Python 3.
    exit /b 1
)

echo Checking for virtual environment...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing uv...
pip install uv

echo Installing cuda-python
uv pip install cuda-python>=12.3

echo Installing PyTorch with CUDA support...
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

echo Installing dependencies...
uv pip install -r requirements.txt

echo Starting the application...
python app.py

pause 