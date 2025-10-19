; 🚀 Rocket Sender Installer (Standalone Version)
[Setup]
AppName=Rocket Sender
AppVersion=1.0
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
Source: "main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; شورتكوت في Start Menu
Name: "{autoprograms}\Rocket Sender"; Filename: "{app}\Rocket Sender.exe"; IconFilename: "{app}\rocket.ico"
; شورتكوت على سطح المكتب للمستخدم الحالي
Name: "{userdesktop}\Rocket Sender"; Filename: "{app}\Rocket Sender.exe"; IconFilename: "{app}\rocket.ico"

[Run]
Filename: "{app}\Rocket Sender.exe"; Description: "تشغيل Rocket Sender"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
