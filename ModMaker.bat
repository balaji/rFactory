@echo off
cls
echo rFactor 2 ModMaker V1.9

setlocal

rem if '%2' == 'ModManager.exe' then this was called from that program and shouldn't pause
echo %time% > c:\temp\debug
echo %1 %2 >> c:\temp\debug
echo debug1 >> c:\temp\debug

rem Default path, can be overridden in mod file
rem rf2dir=[path to rF2 install]
set rf2dir=%ProgramFiles(x86)%\Steam\steamapps\common\rFactor 2
set SteamCmd=%ProgramFiles(x86)%/Steam/steam.exe
set modfile=%~dpnx1
if '%modfile%' == '' goto helpNoModfile
if not exist %modfile% goto helpNoModfile
echo Using %modfile%
set verbose=0
set dryrun=0
rem Parse the modfile
for /f "eol=# tokens=1,2* delims==" %%i in (%modfile%) do (
 if /i '%%i' == 'Name' set modset=%%j
 if /i '%%i' == 'rf2dir' set rf2dir=%%j
 if /i '%%i' == 'SteamCmd' set SteamCmd=%%j
 if /i '%%i' == 'temporary_copy' set temporary_copy=%%j
 if /i '%%i' == 'verbose' set verbose=%%j
 if /i '%%i' == 'dryrun' set dryrun=%%j
 )
set temporary_copy=%rf2dir%\UserData\temporary_copy
if %verbose% GTR 0 echo Full path: %modfile%

if '%modset%' == '' goto helpNoName

:::::::::::::::::::::::::::::::::::::::::::::::::
rem OK, ready to go
echo Name: %modset%
echo rf2dir: %rf2dir%
echo temporary_copy: %temporary_copy%
if %verbose% GTR 0 echo verbose: %verbose%
if %dryrun% GTR 0 echo dryrun ON
if %verbose% GTR 2 echo on
echo.

:::::::::::::::::::::::::::::::::::::::::::::::::
rem Check if Steam running
Set "MyProcess=Steam.exe"
tasklist /NH /FI "imagename eq %MyProcess%" 2>nul |find /i "%MyProcess%">nul
if not errorlevel 1 (
  Echo "%MyProcess%" is running
  goto :SteamRunning )

rem start it if not
echo Starting "%MyProcess%"
start "" /min "%SteamCmd%"
Set "MySubProcess=SteamService.exe"
:loop
  timeout 1 > nul
  tasklist /NH /FI "imagename eq %MySubProcess%" 2>nul |find /i "%MySubProcess%">nul
  if errorlevel 1 goto loop
echo Steam takes some time to get going, allowing it to load...
timeout 15
echo "%MyProcess%" running

:SteamRunning
:::::::::::::::::::::::::::::::::::::::::::::::::

rem Create a folder for the mod

pushd "%rf2dir%"
if errorlevel 1 goto no_rf2dir
md "%temporary_copy%\%modset%"
if not exist "%temporary_copy%\%modset%" goto temporary_copy_error
pushd "%temporary_copy%\%modset%"
if errorlevel 1 goto temporary_copy_error
set _modfolder=%cd%
if %verbose% GTR 1 ( 
  echo temporary_copy: "%temporary_copy%"
  echo modset: "%modset%"
  echo _modfolder: "%_modfolder%"
  )
echo Creating rFactor copy in %_modfolder%
echo.

:::::::::::::::::::::::::::::::::::::::::::::::::
rem Symlinks (actually "Junctions" which do not require admin rights)
rem back to the main install
for %%d in (Bin
Bin32
Bin64
Core
Launcher
LOG
Manifests
ModDev
PluginData
steamapps
steam_shader_cache
Support
Templates
Updates
UserData
_CommonRedist ) do if %verbose%==0 (
  mklink /j "%%d" "%rf2dir%\%%d" > nul
  ) else (
  mklink /j "%%d" "%rf2dir%\%%d"
  )

:::::::::::::::::::::::::::::::::::::::::::::::::
rem Symlinks to for the Installed folder, less Locations & Vehicles
md Installed
cd Installed
for %%d in (Commentary
HUD
Nations
rFm
Showroom
Sounds
Talent
UIData ) do if %verbose%==0 (
  mklink /j "%%d" "%rf2dir%\Installed\%%d" > nul
  ) else (
  mklink /j "%%d" "%rf2dir%\Installed\%%d"
  )

:::::::::::::::::::::::::::::::::::::::::::::::::
rem Symlinks to selected Locations & Vehicles
md Locations
cd Locations

rem Parse the modfile for Locations
for /f "eol=# tokens=1,2* delims==" %%i in (%modfile%) do if /i '%%i' == 'Location' (
  if exist "%rf2dir%\Installed\Locations\%%j" (
    if %verbose% GTR 1 (
      mklink /j "%%j" "%rf2dir%\Installed\Locations\%%j"
      ) else (
      mklink /j "%%j" "%rf2dir%\Installed\Locations\%%j" > nul
      echo Added Location %%j
      )
    ) else echo "Locations\%%j" not found
  )
cd..

:::::::::::::::::::::::::::::::::::::::::::::::::
md Vehicles
cd Vehicles

rem Parse the modfile for Vehicles
for /f "eol=# tokens=1,2* delims==" %%i in (%modfile%) do if /i '%%i' == 'Vehicle' (
  if exist "%rf2dir%\Installed\Vehicles\%%j" (
    if %verbose% GTR 1 (
      mklink /j "%%j" "%rf2dir%\Installed\Vehicles\%%j"
      ) else (
      mklink /j "%%j" "%rf2dir%\Installed\Vehicles\%%j" > nul
      echo Added Vehicle %%j
      )
    ) else echo "Vehicles\%%j" not found
  )

:::::::::::::::::::::::::::::::::::::::::::::::::
popd
echo.

echo debug2 >> c:\temp\debug
if %verbose% GTR 1 dir /b Bin64\plugins\*.dll > c:\temp\dlls
echo debug3 >> c:\temp\debug
@echo Starting rFactor 2 singleplayer...

if %dryrun%==0 (
  Bin64\rFactor2.exe  +singleplayer +path="%temporary_copy%\%modset%"
  ) else (
  echo      DRY RUN.  rFactor has now exited
  if not '%2' == 'ModManager.exe' pause
  )

echo.
if %verbose% == 0 goto deleteCopy
  if '%2' == 'ModManager.exe' goto deleteCopy
  set /p _delete=Enter K if you want to KEEP the temporary rFactor copy "%modset%":
  if /I '%_delete%' == 'k' goto :pauseExit

:deleteCopy
rmdir /s /q "%_modfolder%"
rem Delete the temporary_copy folder if there was nothing else in it.
rmdir %temporary_copy% > nul 2>&1
echo %_modfolder% deleted.

if '%2' == 'ModManager.exe' Exit
goto :pauseExit

:::::::::::::::::::::::::::::::::::::::::::::::::

:helpNoModfile
@echo off
echo Usage: %0 ^<Modfile^>
echo (or you can drop ^<Modfile^> on %0)
echo.

:helpNoName
@echo off
echo The Modfile must have
echo NAME=^<Name for the mod^> (preferably one word)
echo LOCATION=^<Track folder name^>
echo repeat as required
echo VEHICLE=^<Vehicle folder name^>
echo repeat as required
echo.
echo For example
echo name=1960s_F1_UK
echo Location=CRYSTAL PALACE 1969
echo Location=Silverstone90s
echo Location=BrandsHatch
echo etc.
echo Vehicle=Brabham_1966
echo Vehicle=Ferrari_312_67
echo Vehicle=Historic Challenge_EVE_1968
echo.
echo Anything on a line after # is a comment
echo.
echo If your rFactor is installed somewhere other than
echo %ProgramFiles(x86)%\Steam\steamapps\common\rFactor 2
echo then you can add a line like this
echo rf2dir=d:\games\Steam\steamapps\common\rFactor 2
echo.
echo Similarly for the command to start Steam
echo SteamCmd=%ProgramFiles(x86)%\Steam\Steam
echo.
echo Advanced options
echo temporary_copy=^<path^>  to put the shadow copy somewhere other than
echo        %rf2dir%\UserData\temporary_copy
echo verbose=0,1 or 2       for extra progress messages
echo dryrun=1               run %0 but don't start rFactor
echo.
goto pauseExit

:temporary_copy_error
echo.
echo ERROR
echo.
echo Could not create temp folder "%temporary_copy%\%modset%"
echo in %rf2dir%
echo.
echo One answer is to add this to %1
echo temporary_copy=^<path^>  
echo to put the shadow copy somewhere else
goto pauseExit

:no_rf2dir
echo.
echo ERROR
echo.
echo Could not find rFactor 2 folder "%rf2dir%"

:pauseExit
echo.
pause


