import subprocess

p = subprocess.Popen("echo 'foo' && sleep 60 && echo 'bar'", shell = True)
p.kill()