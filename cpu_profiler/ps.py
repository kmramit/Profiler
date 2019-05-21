import psutil
import time
import subprocess
current_milli_time = lambda: int(round(time.time() * 1000))

def getListOfProcessSortedByCPU():
    listOfProcObjects = []
    # Iterate over the list
    for proc in psutil.process_iter():
       try:
           
           pinfo = proc.as_dict(attrs=['pid', 'name'])
           process = psutil.Process(pinfo['pid'])
           process.cpu_percent(interval=None)
           pinfo['cpu'] = process.cpu_percent(interval=None)
           listOfProcObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
           pass
 
    listOfProcObjects = sorted(listOfProcObjects, key=lambda procObj: procObj['cpu'], reverse=True)
 
    return listOfProcObjects[0]
 
def main():
 
    global_system_cpu = psutil.cpu_percent(interval=0.1)
    start_time = current_milli_time()
    top_process = getListOfProcessSortedByCPU()
    end_time = current_milli_time()
    Pid = top_process['pid']
    print(end_time-start_time)

    #option 1 
    start_time = current_milli_time()
    bashCommand ="ps -p 7859 -L -o pid,lwp,pcpu | sort -n -k 3"
    output,error = subprocess.Popen(bashCommand, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    
    split = output.split('\n')
    last = split[len(split)-2]
    fields = last.split()
    end_time = current_milli_time()
    print(end_time-start_time)
    tid = fields[1]
    percent = fields[2]
    print(percent)
    
    
if __name__ == '__main__':
   main()