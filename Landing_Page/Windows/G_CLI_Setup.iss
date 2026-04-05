; G CLI - Inno Setup Script
; This script generates a professional .exe installer for Windows.

[Setup]
AppName=G CLI
AppVersion=3.0.0
DefaultDirName={autopf}\G-CLI
DefaultGroupName=G CLI
OutputDir=..\
OutputBaseFilename=G_CLI_Windows_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\..\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\G CLI"; Filename: "{app}\gcli.py"

[Code]
var
  APIKeyPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  { Create a custom wizard page for API keys }
  APIKeyPage := CreateInputQueryPage(wpSelectDir,
    'AI Brain Configuration', 'Connect your frontier models',
    'Please enter your API keys below. You can leave these blank and configure them later using "g config".');

  APIKeyPage.Add('Anthropic (Claude) API Key:', False);
  APIKeyPage.Add('Google (Gemini) API Key:', False);
  APIKeyPage.Add('OpenAI (Codex) API Key:', False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    { Generate the .env file based on user input }
    EnvContent := 'ANTHROPIC_API_KEY=' + APIKeyPage.Values[0] + #13#10 +
                  'GEMINI_API_KEY=' + APIKeyPage.Values[1] + #13#10 +
                  'OPENAI_API_KEY=' + APIKeyPage.Values[2] + #13#10;
    
    SaveStringToFile(ExpandConstant('{app}\.env'), EnvContent, False);
  end;
end;

[Run]
Filename: "powershell.exe"; Parameters: "-Command ""& {pip install typer rich requests openai google-generativeai python-dotenv watchdog psutil pydantic anthropic langchain-core --user}"""; StatusMsg: "Installing AI dependencies..."; Flags: runhidden
