@echo off
rem Joins the two European ROMs (Ages first) into the file the BPS patches apply to.
set AGES=Legend of Zelda, The - Oracle of Ages (Europe) (En,Fr,De,Es,It).gbc
set SEASONS=Legend of Zelda, The - Oracle of Seasons (Europe) (En,Fr,De,Es,It).gbc
if not exist "%AGES%" (echo Missing: %AGES% & pause & exit /b 1)
if not exist "%SEASONS%" (echo Missing: %SEASONS% & pause & exit /b 1)
copy /b "%AGES%" + "%SEASONS%" "Oracles (Ages+Seasons).gbc" >nul
echo Created "Oracles (Ages+Seasons).gbc" - now apply the BPS patch of your language to it.
pause
