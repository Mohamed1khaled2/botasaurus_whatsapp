; 🚀 Rocket Sender Installer (Standalone Version)
[Setup]
AppName=Rocket Sender
AppVersion=2.0
AppPublisher=Rocket Team
AppPublisherURL=https://rocket-sender.app
DefaultDirName={autopf}\Rocket Sender
DefaultGroupName=Rocket Sender
UninstallDisplayIcon={app}\Rocket Sender.exe
OutputDir=.
OutputBaseFilename=Rocket_Sender_Installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=rocket.ico
DisableDirPage=no
DisableProgramGroupPage=no

[Files]
; انسخ كل ملفات النسخة المستقلة اللي عملها Nuitka
Source: "main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; شورتكوت في Start Menu
Name: "{autoprograms}\Rocket Sender"; Filename: "{app}\Rocket Sender.exe"; IconFilename: "{app}\rocket.ico"
; شورتكوت على سطح المكتب
Name: "{commondesktop}\Rocket Sender"; Filename: "{app}\Rocket Sender.exe"; IconFilename: "{app}\rocket.ico"

[Run]
; تشغيل البرنامج بعد التثبيت
Filename: "{app}\Rocket Sender.exe"; Description: "تشغيل Rocket Sender"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; حذف كل الملفات عدا مجلد database
Type: filesandordirs; Name: "{app}"

[Code]
function ShouldDelete(): Boolean;
begin
  if DirExists(ExpandConstant('{app}\database')) then
  begin
    Log('Skipping deletion of database folder.');
    DelTree(ExpandConstant('{app}'), True, True, True);
    Result := False;
  end
  else
    Result := True;
end;
