; Inno Setup Script for Adidas Interactive Games
; Multi-Desktop Version - 5 separate shortcuts
; Save as: AdidasGamesSetup_MultiDesktop.iss

[Setup]
AppName=Adidas Interactive Games
AppVersion=1.0
AppPublisher=MCMMediaNetworks
AppPublisherURL=https://medialoger.com

DefaultDirName={autopf}\Adidas Interactive Games
DefaultGroupName=Adidas Interactive Games
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=AdidasGamesSetup_MultiDesktop
SetupIconFile=3-foil.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicons"; Description: "Create desktop shortcuts for all games"; GroupDescription: "Desktop Shortcuts"; Flags: checkedonce

[Files]
; Core files
Source: "main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "core\*"; DestDir: "{app}\core"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "3-foil.ico"; DestDir: "{app}"; Flags: ignoreversion

; Logos & assets
Source: "3-foil-w.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "3-stripes-w.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "bata-3.jpg"; DestDir: "{app}"; Flags: ignoreversion

; ALL Games (install semua untuk demo)
Source: "games\tic_tac_toe.py"; DestDir: "{app}\games"; Flags: ignoreversion
Source: "games\memory_game.py"; DestDir: "{app}\games"; Flags: ignoreversion
Source: "games\balloon_pop.py"; DestDir: "{app}\games"; Flags: ignoreversion
Source: "games\fruit_ninja_game.py"; DestDir: "{app}\games"; Flags: ignoreversion
Source: "games\object_catcher_game.py"; DestDir: "{app}\games"; Flags: ignoreversion
Source: "games\base_game.py"; DestDir: "{app}\games"; Flags: ignoreversion
Source: "games\__init__.py"; DestDir: "{app}\games"; Flags: ignoreversion

; ALL Assets (install semua)
Source: "assets\icon\*"; DestDir: "{app}\assets\icon"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "assets\tic-tac-toe\*"; DestDir: "{app}\assets\tic-tac-toe"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "assets\cards\*"; DestDir: "{app}\assets\cards"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "assets\balloons\*"; DestDir: "{app}\assets\balloons"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "assets\fruits\*"; DestDir: "{app}\assets\fruits"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "assets\object-catcher\*"; DestDir: "{app}\assets\object-catcher"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
; Start Menu shortcuts (semua game)
Name: "{group}\Adidas - Tic Tac Toe"; Filename: "{app}\main.exe"; Parameters: "config_tictactoe.ini"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"
Name: "{group}\Adidas - Memory Game"; Filename: "{app}\main.exe"; Parameters: "config_memory.ini"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"
Name: "{group}\Adidas - Balloon Pop"; Filename: "{app}\main.exe"; Parameters: "config_balloon.ini"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"
Name: "{group}\Adidas - Fruit Ninja"; Filename: "{app}\main.exe"; Parameters: "config_fruitninja.ini"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"
Name: "{group}\Adidas - Object Catcher"; Filename: "{app}\main.exe"; Parameters: "config_catcher.ini"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"

; Desktop shortcuts (5 game berbeda)
Name: "{commondesktop}\Adidas - Tic Tac Toe"; Filename: "{app}\main.exe"; Parameters: "config_tictactoe.ini"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"; Tasks: desktopicons
Name: "{commondesktop}\Adidas - Memory Game"; Filename: "{app}\main.exe"; Parameters: "config_memory.ini"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"; Tasks: desktopicons
Name: "{commondesktop}\Adidas - Balloon Pop"; Filename: "{app}\main.exe"; Parameters: "config_balloon.ini"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"; Tasks: desktopicons
Name: "{commondesktop}\Adidas - Fruit Ninja"; Filename: "{app}\main.exe"; Parameters: "config_fruitninja.ini"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"; Tasks: desktopicons
Name: "{commondesktop}\Adidas - Object Catcher"; Filename: "{app}\main.exe"; Parameters: "config_catcher.ini"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"; Tasks: desktopicons

[Run]
Filename: "{app}\main.exe"; Parameters: "config_tictactoe.ini"; Description: "Launch Tic Tac Toe"; Flags: postinstall skipifsilent nowait

[Code]
var
  RetailOptionsPage: TInputOptionWizardPage;

procedure InitializeWizard;
begin
  RetailOptionsPage := CreateInputOptionPage(wpSelectTasks,
    'Display Options', 'Configure display settings for all games',
    'These settings will apply to all 5 games:',
    True, False);
  RetailOptionsPage.Add('Enable Fullscreen Mode');
  RetailOptionsPage.Add('Enable Kiosk Mode (hide cursor, disable ESC)');
  
  // Set default values
  RetailOptionsPage.Values[0] := True;  // Fullscreen default ON
  RetailOptionsPage.Values[1] := False; // Kiosk mode default OFF
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigContent: String;
  FullscreenValue, KioskValue: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Determine config values
    if RetailOptionsPage.Values[0] then
      FullscreenValue := 'true'
    else
      FullscreenValue := 'false';
      
    if RetailOptionsPage.Values[1] then
      KioskValue := 'true'
    else
      KioskValue := 'false';

    // Create 5 config files with same display settings but different games
    
    // 1. Tic Tac Toe
    ConfigContent := '[GAME]' + #13#10 + 'selected_game=tic_tac_toe' + #13#10#13#10;
    ConfigContent := ConfigContent + '[DISPLAY]' + #13#10;
    ConfigContent := ConfigContent + 'fullscreen=' + FullscreenValue + #13#10;
    ConfigContent := ConfigContent + 'kiosk_mode=' + KioskValue + #13#10;
    SaveStringToFile(ExpandConstant('{app}\config_tictactoe.ini'), ConfigContent, False);

    // 2. Memory Game
    ConfigContent := '[GAME]' + #13#10 + 'selected_game=memory_game' + #13#10#13#10;
    ConfigContent := ConfigContent + '[DISPLAY]' + #13#10;
    ConfigContent := ConfigContent + 'fullscreen=' + FullscreenValue + #13#10;
    ConfigContent := ConfigContent + 'kiosk_mode=' + KioskValue + #13#10;
    SaveStringToFile(ExpandConstant('{app}\config_memory.ini'), ConfigContent, False);

    // 3. Balloon Pop
    ConfigContent := '[GAME]' + #13#10 + 'selected_game=balloon_pop' + #13#10#13#10;
    ConfigContent := ConfigContent + '[DISPLAY]' + #13#10;
    ConfigContent := ConfigContent + 'fullscreen=' + FullscreenValue + #13#10;
    ConfigContent := ConfigContent + 'kiosk_mode=' + KioskValue + #13#10;
    SaveStringToFile(ExpandConstant('{app}\config_balloon.ini'), ConfigContent, False);

    // 4. Fruit Ninja
    ConfigContent := '[GAME]' + #13#10 + 'selected_game=fruit_ninja' + #13#10#13#10;
    ConfigContent := ConfigContent + '[DISPLAY]' + #13#10;
    ConfigContent := ConfigContent + 'fullscreen=' + FullscreenValue + #13#10;
    ConfigContent := ConfigContent + 'kiosk_mode=' + KioskValue + #13#10;
    SaveStringToFile(ExpandConstant('{app}\config_fruitninja.ini'), ConfigContent, False);

    // 5. Object Catcher
    ConfigContent := '[GAME]' + #13#10 + 'selected_game=object_catcher' + #13#10#13#10;
    ConfigContent := ConfigContent + '[DISPLAY]' + #13#10;
    ConfigContent := ConfigContent + 'fullscreen=' + FullscreenValue + #13#10;
    ConfigContent := ConfigContent + 'kiosk_mode=' + KioskValue + #13#10;
    SaveStringToFile(ExpandConstant('{app}\config_catcher.ini'), ConfigContent, False);
  end;
end;