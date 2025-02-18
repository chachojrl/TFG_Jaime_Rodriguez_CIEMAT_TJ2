@echo off
echo Creating Conda environment from environment.yml...
conda env create -f environment.yml

if %errorlevel% neq 0 (
    echo ERROR: Could not create the environment. Make sure Conda is installed and environment.yml exists.
    exit /b %errorlevel%
)

echo Environment created successfully!
echo To activate the environment, run: conda activate tfg_env
