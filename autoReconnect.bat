cd /d %~dp0

::提升为管理员
%1 %2
ver|find "5.">nul&&goto :Admin
mshta vbscript:createobject("shell.application").shellexecute("%~s0","goto :Admin","","runas",1)(window.close)&goto :eof
:Admin


python ./autoReconnect.py
@echo off

echo .
echo Script ending....
pause