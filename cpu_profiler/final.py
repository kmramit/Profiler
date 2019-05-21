import psutil
import time
import subprocess
import argparse
import json 
current_milli_time = lambda: int(round(time.time() * 1000))

def print_and_exit(error=None,stats=None,threads=None):

  if  error is not None:
    result = {}
    result['success'] = 'false'
    result['reason'] = error
    result['consuming_threads'] = []
    result['total_cpu'] = 0.0
    result['total_time'] = 0
    print(json.dumps(result))
    exit(1)

  else:
    result = {}
    result['success'] = 'true'
    result['reason'] = ''
    result['consuming_threads'] = threads
    result['total_cpu'] = stats['total_cpu']
    result['total_time'] = stats['total_time']
    print(json.dumps(result))
    exit(1)


def get_list_of_process_sorted_by_cpu():
  
    list_of_proc_objects = []
    # Iterate over the list
    for proc in psutil.process_iter():
       try:
           
           pinfo = proc.as_dict(attrs=['pid', 'name'])
           if pinfo['name'].find('java') == -1 :
            continue
           process = psutil.Process(pinfo['pid'])
           process.cpu_percent(interval=None)
           pinfo['cpu'] = process.cpu_percent(interval=None)
           
           list_of_proc_objects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
           pass
 
    list_of_proc_objects = sorted(list_of_proc_objects, key=lambda procObj: procObj['cpu'], reverse=True)
 
    if (len(list_of_proc_objects) == 0):
      final_error = "No Running Java Process"
      print_and_exit(error=final_error)

    return list_of_proc_objects[0]
 
def main(cutoff):
 
    global_system_cpu = psutil.cpu_percent(interval=0.1)
    start_time = current_milli_time()
    top_process = get_list_of_process_sorted_by_cpu()
    
    Pid = top_process['pid'] 

    bash_command ="top -b -H -n1"
    output,error = subprocess.Popen(bash_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
  
    if (error != ''):
      print_and_exit(error=error)

    split = output.split('\n')

    main_thread_id = []
    cpu_array = []
    flag = 0

    for i in range(len(split)-1):
      temp = split[i].split()
      
      if flag == 0:
        if len(temp) > 0 and temp[0] == 'PID':
          flag = 1
        continue
      else:

        if len(temp) < 12:
          continue
        elif float(temp[8]) < cutoff:
          break
        elif temp[11] != 'java':
          continue
        else:
          main_thread_id.append(int(temp[0]))
          cpu_array.append(float(temp[8]))

    if len(main_thread_id) == 0:
      print_and_exit(error="No Java thread above cutoff !")

    jstack_command = "jstack -l "+str(Pid)
    output,error = subprocess.Popen(jstack_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    if (error != ''):
      print_and_exit(error=error)

    consuming_threads = []

    for i in range(len(main_thread_id)):

      nid = "nid="+hex(main_thread_id[i])
      nid_index = output.find(nid)

      thread_info = {}
      thread_info['pid'] = Pid 
      thread_info['nid'] = main_thread_id[i]
      thread_info['cpu'] = cpu_array[i]

      if nid_index == -1:
        thread_info['live'] = 'false'
        thread_info['stack'] = ''
        consuming_threads.append(thread_info)
        continue
      else:

        start_string = output[0:nid_index]
        end_string = output[nid_index:] 
        start_index = start_string.rfind('\n')
        end_index = end_string.find("\n\"")+nid_index
        thread_info['live'] = 'true'
        thread_info['stack'] = output[start_index:end_index]
        consuming_threads.append(thread_info)

    end_time = current_milli_time()
    stats = {}
    stats['total_time'] = end_time-start_time
    stats['total_cpu'] = sum(cpu_array)
    print_and_exit(stats=stats,threads=consuming_threads)

if __name__ == '__main__':

  ap = argparse.ArgumentParser()
  ap.add_argument("-c", "--cutoff",help="Percentage CPU cutoff")
  args = vars(ap.parse_args())

  if args["cutoff"] is None:
      args["cutoff"] = 10.0
  cutoff = float(args['cutoff'])
  main(cutoff)