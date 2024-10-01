@echo off

setlocal enabledelayedexpansion

set folder1="Impedance reports"
set folder2="Length reports"
set folder3="Spacing reports"

:: 提示使用者輸入要加入的字元
set /p projectName="Project Name: "
set /p ver="Version: "
set projectName=%projectName%_
set ver=%ver%_
set zipfilename=%projectName%%ver%CMGR_reports.zip

:: 重新命名 %folder1% 內的檔案
cd /d %folder1%
ren *_report.txt impedance_constraint_report.txt
for %%f in (impedance_constraint_report.txt) do (
    ren "%%f" %projectName%%ver%%%f 
    7z a ..\%zipfilename% %projectName%%ver%%%f
)

:: 重新命名 %folder2% 內的檔案
cd ..
cd /d %folder2%
ren *_report.txt length_constraint_report.txt
for %%f in (length_constraint_report.txt) do (
    ren "%%f" %projectName%%ver%%%f
    7z a ..\%zipfilename% %projectName%%ver%%%f
)

:: 重新命名 %folder3% 內的檔案
cd ..
cd /d %folder3%
ren *_report.txt spacing_constraint_report.txt
for %%f in (spacing_constraint_report.txt) do (
    ren "%%f" %projectName%%ver%%%f
    7z a ..\%zipfilename% %projectName%%ver%%%f
)

echo Finish!
pause