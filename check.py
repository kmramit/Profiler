import subprocess 

bash_command ="ls /proc/25376/task"
output,error = subprocess.Popen(bash_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

check_command = "cat /proc/25376/net/tcp"
check,error = subprocess.Popen(check_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
if (error != ''):
  print("error")
  exit(1)

output = output.split()
for tid in output:
	cat_command = "cat /proc/25376/task/"+tid+"/net/tcp"
	out,error = subprocess.Popen(cat_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate() 
	if out != check:
		print(out)
		print("good")
		print(check)
		exit(1)