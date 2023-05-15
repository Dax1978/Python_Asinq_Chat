import subprocess

args = ['ping', 'google.com']
subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
for line in subproc_ping.stdout:
    # print(line)
    line = line.decode('cp866').encode('utf-8')
    print(line.decode('utf-8'))
