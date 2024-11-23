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
; Ajoute l'exécutable généré par PyInstaller
Source: "C:\Users\Robin Corbonnois\dist\platteform chessbot.exe"; DestDir: "{app}"; Flags: ignoreversion

; Ajoute l'exécutable de Stockfish
Source: "C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\code\test exe 1\stockfish-windows-x86-64-avx2.exe"; DestDir: "{app}\stockfish"; Flags: ignoreversion

[Icons]
; Crée un raccourci sur le bureau
Name: "{commondesktop}\ChessBot"; Filename: "{app}\platteform chessbot.exe"

[Run]
; Exécute le programme après l'installation
Filename: "{app}\platteform chessbot.exe"; Description: "{cm:LaunchProgram,ChessBot}"; Flags: nowait postinstall skipifsilent
