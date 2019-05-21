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
           if pinfo['name'].find('java') == -1 :
            continue
           process = psutil.Process(pinfo['pid'])
           process.cpu_percent(interval=None)
           pinfo['cpu'] = process.cpu_percent(interval=None)
           print(pinfo['cpu'])
           listOfProcObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
           pass
 
    listOfProcObjects = sorted(listOfProcObjects, key=lambda procObj: procObj['cpu'], reverse=True)
 
    if (len(listOfProcObjects) == 0):
      print("No java process")
      exit()
    return listOfProcObjects[0]
 
def main():
 
    global_system_cpu = psutil.cpu_percent(interval=0.1)
    start_time = current_milli_time()
    top_process = getListOfProcessSortedByCPU()
    
    Pid = top_process['pid']

    #option 1 

    start_time = current_milli_time()
    bashCommand ="ps -p " + str(Pid) + " -L -o pid,lwp,pcpu"
    output,error = subprocess.Popen(bashCommand, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    
    if (error != ''):
      print(error)
      exit(1)
    split = output.split('\n')
    listofThreads = []

    total_cpu_percent = 0.0
    for i in range(1,len(split)-1):
      temp = split[i].split()
      thread = {}
      thread['tid'] = temp[1]
      thread['cpu'] = temp[2]
      total_cpu_percent +=float(thread['cpu'])
      listofThreads.append(thread)

    listofThreads = sorted(listofThreads, key=lambda Obj: Obj['cpu'], reverse=True)
    print(total_cpu_percent)
    print(top_process['cpu'])
    print("Top thread ids are")
    for i in range(5):
      print("Tid is %s and cpu is %s",str(listofThreads[i]['tid']),str(listofThreads[i]['cpu']))

    mian_thread_id = int(listofThreads[0]['tid'])

    jstack_command = "jstack -l "+str(Pid)
    
    output,error = subprocess.Popen(jstack_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    if (error != ''):
      print("Error in jstack")
      print(error)
      exit(1)
    nid = "nid="+hex(mian_thread_id)
    nid_index = output.find(nid)

    if nid_index == -1:
      print("Not found the hexadecimal TID")
      exit(1)
    #print(output)
    
    start_string = output[0:nid_index]
    end_string = output[nid_index:] 
    start_index = start_string.rfind('\n')
    end_index = end_string.find("\n\"")+nid_index

    end_time = current_milli_time()
    print(end_time-start_time)
    print(output[start_index:end_index])
if __name__ == '__main__':
   main()