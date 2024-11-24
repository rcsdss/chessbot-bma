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
; Fügt die Hauptanwendung hinzu
Source: "C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\setup\chessbot.exe"; DestDir: "{app}"; Flags: ignoreversion

; Fügt die ausführbare Datei von Stockfish hinzu
Source: "C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\setup\stockfish-windows-x86-64-avx2.exe"; DestDir: "{app}\stockfish"; Flags: ignoreversion

; Fügt die Dokumentation hinzu
Source: "C:\Users\Robin Corbonnois\OneDrive - TBZ\Desktop\python\chessbot_project_2\github\setup\chessbot_BR_Schriftliche_Arbeit.docx"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
; Erstellt eine Verknüpfung auf dem Desktop
Name: "{commondesktop}\ChessBot"; Filename: "{app}\chessbot.exe"

[Run]
; Führt das Programm nach der Installation aus
Filename: "{app}\chessbot.exe"; Description: "ChessBot Br"; Flags: nowait postinstall skipifsilent

