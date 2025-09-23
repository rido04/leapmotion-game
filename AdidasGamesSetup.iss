; Inno Setup Script for Adidas Interactive Games
; Save as: AdidasGamesSetup.iss

[Setup]
; Basic app info
AppName=Adidas Interactive Games
AppVersion=1.0
AppPublisher=Your Company Name
AppPublisherURL=https://yourwebsite.com
AppSupportURL=https://yourwebsite.com/support
AppUpdatesURL=https://yourwebsite.com/updates

; Installation settings
DefaultDirName={autopf}\Adidas Interactive Games
DefaultGroupName=Adidas Interactive Games
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=AdidasGamesSetup
SetupIconFile=3-foil.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; System requirements
MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Start automatically with Windows (Kiosk Mode)"; GroupDescription: "Retail Options"; Flags: unchecked

[Files]
; Main executable (dari PyInstaller --onefile)
Source: "C:\laragon\www\game\main.exe"; DestDir: "{app}"; Flags: ignoreversion

; Assets folder
Source: "C:\laragon\www\game\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Games folder  
Source: "C:\laragon\www\game\games\*"; DestDir: "{app}\games"; Flags: ignoreversion recursesubdirs createallsubdirs

; Core folder
Source: "C:\laragon\www\game\core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "C:\laragon\www\game\README.md"; DestDir: "{app}"; Flags: ignoreversion; Check: CheckFileExists('C:\laragon\www\game\README.md')
Source: "C:\laragon\www\game\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion; Check: CheckFileExists('C:\laragon\www\game\requirements.txt')

; Game images/icons
Source: "C:\laragon\www\game\3-foil.png"; DestDir: "{app}"; Flags: ignoreversion; Check: CheckFileExists('C:\laragon\www\game\3-foil.png')
Source: "C:\laragon\www\game\3-stripes.png"; DestDir: "{app}"; Flags: ignoreversion; Check: CheckFileExists('C:\laragon\www\game\3-stripes.png')
Source: "C:\laragon\www\game\bata-putih.jpg"; DestDir: "{app}"; Flags: ignoreversion; Check: CheckFileExists('C:\laragon\www\game\bata-putih.jpg')

; App icon untuk installer
Source: "C:\laragon\www\game\3-foil.ico"; DestDir: "{app}"; Flags: ignoreversion; Check: CheckFileExists('C:\laragon\www\game\3-foil.ico')

[Icons]
; Desktop shortcut
Name: "{autodesktop}\Adidas Interactive Games"; Filename: "{app}\main.exe"; IconFilename: "{app}\3-foil.ico"; Tasks: desktopicon; Comment: "Launch Adidas Interactive Games"

; Start menu
Name: "{autoprograms}\{groupname}\Adidas Interactive Games"; Filename: "{app}\main.exe"; IconFilename: "{app}\3-foil.ico"; Comment: "Launch Adidas Interactive Games"
Name: "{autoprograms}\{groupname}\Uninstall Adidas Interactive Games"; Filename: "{uninstallexe}"

; Quick launch (deprecated in newer Windows, but kept for compatibility)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Adidas Interactive Games"; Filename: "{app}\main.exe"; Tasks: quicklaunchicon

; Auto-start (untuk kiosk mode)
Name: "{userstartup}\Adidas Interactive Games"; Filename: "{app}\main.exe"; Tasks: autostart; Comment: "Adidas Interactive Games - Kiosk Mode"

[Run]
; Install Leap Motion SDK dulu (jika ada)
Filename: "{tmp}\LeapSDK\LeapSDK-Setup.exe"; Parameters: "/S"; StatusMsg: "Installing Leap Motion SDK..."; Flags: waituntilterminated; Check: CheckFileExists('{tmp}\LeapSDK\LeapSDK-Setup.exe')

; Launch app setelah install
Filename: "{app}\main.exe"; Description: "{cm:LaunchProgram,Adidas Interactive Games}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// Custom function untuk validasi file
function CheckFileExists(FileName: String): Boolean;
begin
  Result := FileExists(ExpandConstant(FileName));
end;

// Custom page untuk retail options
var
  RetailOptionsPage: TInputOptionWizardPage;
  
procedure InitializeWizard;
begin
  // Create custom page untuk retail-specific options
  RetailOptionsPage := CreateInputOptionPage(wpSelectTasks,
    'Retail Deployment Options', 'Configure for retail environment',
    'Please select the deployment options for retail/kiosk use:',
    True, False);
    
  RetailOptionsPage.Add('Enable Kiosk Mode (Fullscreen, hide cursor)');
  RetailOptionsPage.Add('Disable Windows key and Alt+Tab');
  RetailOptionsPage.Add('Install Windows service for auto-restart');
  
  // Default selections untuk retail
  RetailOptionsPage.Values[0] := True;
  RetailOptionsPage.Values[1] := False;
  RetailOptionsPage.Values[2] := False;
end;

// Apply retail configurations
procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: String;
  ConfigContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    ConfigFile := ExpandConstant('{app}\config.ini');
    
    // Write config based on selections
    if RetailOptionsPage.Values[0] then
    begin
      ConfigContent := '[DISPLAY]' + #13#10 + 'kiosk_mode=true' + #13#10 + 'fullscreen=true' + #13#10;
      SaveStringToFile(ConfigFile, ConfigContent, False);
    end;
    
    // Additional retail configurations bisa ditambah disini...
  end;
end;