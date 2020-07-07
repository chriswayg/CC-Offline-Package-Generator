#!/usr/bin/osascript
set run_cmd to (POSIX path of ((path to me as text) & "::") & "ppackage") as text

if application "Terminal" is running then
	tell application "Terminal"
		# do script without "in window" will open a new window
		do script with command run_cmd
		activate
	end tell
else
	tell application "Terminal"
		# window 1 is guaranteed to be recently opened window
		do script with command run_cmd in window 1
		reopen
		activate
	end tell
end if
# from left, from top, to right, to bottom in px
tell application "Terminal" to set bounds of front window to {100, 23, 800, 850}
