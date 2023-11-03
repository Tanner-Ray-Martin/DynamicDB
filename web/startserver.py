import subprocess
import webbrowser

command = "uvicorn main:app --reload"
webbrowser.open("http://127.0.0.1:8000/docs#/default/")
subprocess.run(command, shell=True)
