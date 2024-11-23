[Setup]
AppName=ChessBot
AppVersion=1.0
DefaultDirName={pf}\ChessBot
DefaultGroupName=ChessBot
OutputBaseFilename=ChessBotInstaller
OutputDir=C:\Users\Robin Corbonnois\Bureau\ChessBotInstaller
Compression=lzma
SolidCompression=yes

[Files]
; Ajoute l'ex�cutable g�n�r� par PyInstaller
Source: "C:\Users\Robin Corbonnois\dist\platteform chessbot.exe"; DestDir: "{app}"; Flags: ignoreversion

; Ajoute l'ex�cutable de Stockfish
Source: "C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\code\test exe 1\stockfish-windows-x86-64-avx2.exe"; DestDir: "{app}\stockfish"; Flags: ignoreversion

[Icons]
; Cr�e un raccourci sur le bureau
Name: "{commondesktop}\ChessBot"; Filename: "{app}\platteform chessbot.exe"

[Run]
; Ex�cute le programme apr�s l'installation
Filename: "{app}\platteform chessbot.exe"; Description: "{cm:LaunchProgram,ChessBot}"; Flags: nowait postinstall skipifsilent
