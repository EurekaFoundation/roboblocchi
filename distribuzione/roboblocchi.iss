; Installer Windows di RoboBlocchi (Inno Setup 6.3 o successivo).
;
; Di solito non serve usarlo a mano: lo lancia distribuzione/costruisci.py dopo PyInstaller.
; A mano, dalla cartella principale del progetto:
;     iscc /DVersione=0.2.0 distribuzione\roboblocchi.iss

#ifndef Versione
  #define Versione "0.0.0"
#endif
#ifndef Suffisso
  #define Suffisso ""
#endif

[Setup]
; AppId identifica l'app per aggiornamenti e disinstallazione: non va mai cambiato
AppId={{8C69D161-E167-4798-902C-3FD656A990C0}
AppName=RoboBlocchi
AppVersion={#Versione}
AppVerName=RoboBlocchi {#Versione}
AppPublisher=Comunità RoboBlocchi
AppComments=Robotica didattica a blocchi con intelligenza artificiale locale
DefaultDirName={autopf}\RoboBlocchi
DefaultGroupName=RoboBlocchi
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=..\dist
OutputBaseFilename=RoboBlocchi-{#Versione}{#Suffisso}-installer-windows
SetupIconFile=icona.ico
UninstallDisplayIcon={app}\RoboBlocchi.exe
UninstallDisplayName=RoboBlocchi
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; Installabile anche senza diritti di amministratore (utile sui PC scolastici);
; con i diritti si può scegliere l'installazione per tutti gli utenti
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
VersionInfoVersion={#Versione}
VersionInfoProductName=RoboBlocchi

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\RoboBlocchi\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\RoboBlocchi"; Filename: "{app}\RoboBlocchi.exe"
Name: "{autodesktop}\RoboBlocchi"; Filename: "{app}\RoboBlocchi.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\RoboBlocchi.exe"; Description: "{cm:LaunchProgram,RoboBlocchi}"; Flags: nowait postinstall skipifsilent

[CustomMessages]
italian.WebView2Mancante=Su questo computer non risulta installato Microsoft Edge WebView2 Runtime, necessario per l'interfaccia di RoboBlocchi.%n%nÈ già presente in Windows 11 e nella maggior parte dei Windows 10 aggiornati. Se l'app non si apre, scaricalo gratuitamente dal sito di Microsoft cercando "WebView2 Runtime".%n%nVuoi continuare l'installazione?
english.WebView2Mancante=Microsoft Edge WebView2 Runtime, required by the RoboBlocchi interface, does not seem to be installed.%n%nIt is included in Windows 11 and most updated Windows 10 systems. If the app does not start, download it for free from Microsoft (search "WebView2 Runtime").%n%nDo you want to continue?

[Code]
const
  WebView2Id = '{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';

function WebView2Installato(): Boolean;
var
  Versione: String;
begin
  Result :=
    (RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\' + WebView2Id, 'pv', Versione) and (Versione <> '') and (Versione <> '0.0.0.0')) or
    (RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\' + WebView2Id, 'pv', Versione) and (Versione <> '') and (Versione <> '0.0.0.0')) or
    (RegQueryStringValue(HKCU, 'Software\Microsoft\EdgeUpdate\Clients\' + WebView2Id, 'pv', Versione) and (Versione <> '') and (Versione <> '0.0.0.0'));
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not WebView2Installato() then
    Result := MsgBox(CustomMessage('WebView2Mancante'), mbConfirmation, MB_YESNO) = IDYES;
end;
