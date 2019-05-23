import subprocess 

bash_command ="sar 1 3"
output,error = subprocess.Popen(bash_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

if (error != ''):
  print_and_exit(error=error)

