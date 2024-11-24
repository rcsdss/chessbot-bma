[Setup]
AppName=ChessBot
AppVersion=1.0
DefaultDirName={pf}\ChessBot
DefaultGroupName=ChessBot
OutputBaseFilename=ChessBotInstaller
OutputDir=C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\setup
Compression=lzma
SolidCompression=yes

[Files]
; F�gt die Hauptanwendung hinzu
Source: "C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\setup\chessbot.exe"; DestDir: "{app}"; Flags: ignoreversion

; F�gt die ausf�hrbare Datei von Stockfish hinzu
Source: "C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\setup\stockfish-windows-x86-64-avx2.exe"; DestDir: "{app}\stockfish"; Flags: ignoreversion

; F�gt die Dokumentation hinzu
Source: "C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\setup\chessbot_BR_Schriftliche_Arbeit.docx"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
; Erstellt eine Verkn�pfung auf dem Desktop
Name: "{commondesktop}\ChessBot"; Filename: "{app}\chessbot.exe"

[Run]
; F�hrt das Programm nach der Installation aus
Filename: "{app}\chessbot.exe"; Description: "ChessBot Br"; Flags: nowait postinstall skipifsilent

