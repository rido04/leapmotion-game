; Inno Setup Script for Adidas Interactive Games
; Save as: AdidasGamesSetup.iss

[Setup]
AppName=Adidas Interactive Games
AppVersion=1.0
AppPublisher=MCMMediaNetworks
AppPublisherURL=https://medialoger.com

DefaultDirName={autopf}\Adidas Interactive Games
DefaultGroupName=Adidas Interactive Games
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=AdidasGamesSetup
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
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Start automatically with Windows (Kiosk Mode)"; GroupDescription: "Retail Options"; Flags: unchecked

[Files]
; Core files
Source: "main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "core\*"; DestDir: "{app}\core"; Flags: recursesubdirs createallsubdirs
Source: "3-foil.ico"; DestDir: "{app}"; Flags: ignoreversion

; Logos & assets
Source: "3-foil-w.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "3-stripes-w.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "bata-3.jpg"; DestDir: "{app}"; Flags: ignoreversion

; Games
Source: "games\tic_tac_toe.py"; DestDir: "{app}\games"; Check: IsGameSelected('tic_tac_toe')
Source: "games\memory_game.py"; DestDir: "{app}\games"; Check: IsGameSelected('memory_game')  
Source: "games\balloon_pop.py"; DestDir: "{app}\games"; Check: IsGameSelected('balloon_pop')
Source: "games\fruit_ninja_game.py"; DestDir: "{app}\games"; Check: IsGameSelected('fruit_ninja')
Source: "games\base_game.py"; DestDir: "{app}\games"; Flags: ignoreversion
Source: "games\__init__.py"; DestDir: "{app}\games"; Flags: ignoreversion

; Shared assets
Source: "assets\icon\*"; DestDir: "{app}\assets\icon"; Flags: recursesubdirs createallsubdirs
Source: "assets\tic-tac-toe\*"; DestDir: "{app}\assets\tic-tac-toe"; Check: IsGameSelected('tic_tac_toe'); Flags: recursesubdirs
Source: "assets\cards\*"; DestDir: "{app}\assets\cards"; Check: IsGameSelected('memory_game'); Flags: recursesubdirs
Source: "assets\balloons\*"; DestDir: "{app}\assets\balloons"; Check: IsGameSelected('balloon_pop'); Flags: recursesubdirs
Source: "assets\fruits\*"; DestDir: "{app}\assets\fruits"; Check: IsGameSelected('fruit_ninja'); Flags: recursesubdirs

[Icons]
; Start Menu shortcut
Name: "{group}\Adidas Interactive Games"; Filename: "{app}\main.exe"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"

; Desktop shortcut (optional, via Tasks)
Name: "{commondesktop}\Adidas Interactive Games"; Filename: "{app}\main.exe"; WorkingDir: "{app}"; IconFilename: "{app}\3-foil.ico"; Tasks: desktopicon

[Code]
var
  RetailOptionsPage: TInputOptionWizardPage;
  GameSelectionPage: TWizardPage;
  RadioTicTacToe: TNewRadioButton;
  RadioMemoryGame: TNewRadioButton;
  RadioBalloonPop: TNewRadioButton;
  RadioFruitNinja: TNewRadioButton;

procedure InitializeWizard;
begin
  RetailOptionsPage := CreateInputOptionPage(wpSelectTasks,
    'Retail Deployment Options', 'Configure for retail environment',
    'Please select the deployment options for retail/kiosk use:',
    True, False);
  RetailOptionsPage.Add('Enable Kiosk Mode (Fullscreen, hide cursor)');
  RetailOptionsPage.Add('Disable Windows key and Alt+Tab');

  GameSelectionPage := CreateCustomPage(RetailOptionsPage.ID,
    'Game Selection', 'Choose which game to install');

  with TNewStaticText.Create(GameSelectionPage) do
  begin
    Parent := GameSelectionPage.Surface;
    Caption := 'Select ONE game for this outlet installation:';
    Left := 0; Top := 0; Width := GameSelectionPage.SurfaceWidth;
  end;

  RadioTicTacToe := TNewRadioButton.Create(GameSelectionPage);
  with RadioTicTacToe do
  begin
    Parent := GameSelectionPage.Surface;
    Caption := 'Tic Tac Toe - Strategic thinking game';
    Left := 0; Top := 30; Width := GameSelectionPage.SurfaceWidth;
    Checked := True;
  end;

  RadioMemoryGame := TNewRadioButton.Create(GameSelectionPage);
  with RadioMemoryGame do
  begin
    Parent := GameSelectionPage.Surface;
    Caption := 'Memory Game - Card matching challenge';
    Left := 0; Top := 55; Width := GameSelectionPage.SurfaceWidth;
  end;

  RadioBalloonPop := TNewRadioButton.Create(GameSelectionPage);
  with RadioBalloonPop do
  begin
    Parent := GameSelectionPage.Surface;
    Caption := 'Balloon Pop - Action reaction game';
    Left := 0; Top := 80; Width := GameSelectionPage.SurfaceWidth;
  end;

  RadioFruitNinja := TNewRadioButton.Create(GameSelectionPage);
  with RadioFruitNinja do
  begin
    Parent := GameSelectionPage.Surface;
    Caption := 'Shoe Slash - Ninja slicing action';
    Left := 0; Top := 105; Width := GameSelectionPage.SurfaceWidth;
  end;
end;

function IsGameSelected(GameName: String): Boolean;
begin
  if GameName = 'tic_tac_toe' then Result := RadioTicTacToe.Checked
  else if GameName = 'memory_game' then Result := RadioMemoryGame.Checked
  else if GameName = 'balloon_pop' then Result := RadioBalloonPop.Checked
  else if GameName = 'fruit_ninja' then Result := RadioFruitNinja.Checked
  else Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile, ConfigContent, SelectedGame: String;
begin
  if CurStep = ssPostInstall then
  begin
    ConfigFile := ExpandConstant('{app}\game_config.ini');

    if RadioTicTacToe.Checked then SelectedGame := 'tic_tac_toe'
    else if RadioMemoryGame.Checked then SelectedGame := 'memory_game'
    else if RadioBalloonPop.Checked then SelectedGame := 'balloon_pop'
    else if RadioFruitNinja.Checked then SelectedGame := 'fruit_ninja';

    ConfigContent := '[GAME]' + #13#10 + 'selected_game=' + SelectedGame + #13#10#13#10;
    ConfigContent := ConfigContent + '[DISPLAY]' + #13#10 + 'fullscreen=true' + #13#10;

    if RetailOptionsPage.Values[0] then ConfigContent := ConfigContent + 'kiosk_mode=true' + #13#10;
    if RetailOptionsPage.Values[1] then ConfigContent := ConfigContent + 'disable_windows_key=true' + #13#10;

    SaveStringToFile(ConfigFile, ConfigContent, False);
  end;
end;
