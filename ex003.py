import telnetlib
import time


tn_connect = telnetlib.Telnet('10.0.0.1')

tn_connect.read_until(b'Username:')
tn_connect.write(b'user\n')

tn_connect.read_until(b'Password:')
tn_connect.write(b'pass\n')

time.sleep(5)
output = tn_connect.read_very_eager().decode('cp866').encode('utf-8')
print(output.decode('utf-8'))
