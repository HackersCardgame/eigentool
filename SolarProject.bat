set filepath=%0

for /F "delims=" %%i in (%filepath%) do set dirname="%%~dpi" 

"%dirname%\SolarProject.py" %1
