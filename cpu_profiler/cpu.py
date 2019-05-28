import time
import subprocess
import argparse
import json 
import operator
current_milli_time = lambda: int(round(time.time() * 1000))

def get_jstacks(jstacks,pid,nid):
  jstacks_array = []
  output_jstack = ''
  k_nid = ''

  for j in range(len(jstacks)):
    if pid in jstacks[j]:

      output_jstack = jstacks[j][pid]
      k_nid = "nid="+hex(nid)
      nid_index = output_jstack.find(k_nid)
      if nid_index == -1:
        if output_jstack == "Error in Jstack":
          jstacks_array.append("Error in jstack")
        else:
          jstacks_array.append("Thread died!")
      else:
        start_string = output_jstack[0:nid_index]
        end_string = output_jstack[nid_index:] 
        start_index = start_string.rfind('\n')
        end_index = end_string.find("\n\"")+nid_index
        jstacks_array.append(output_jstack[start_index+1:end_index])

  return jstacks_array

def print_and_exit(error=None,stats=None,threads=None):

  if  error is not None:
    result = {}
    result['success'] = 'false'
    result['reason'] = error
    result['consuming_threads'] = []
    result['total_time'] = 0
    print(json.dumps(result))
    exit(1)

  else:
    result = {}
    result['success'] = 'true'
    result['reason'] = ''
    result['consuming_threads'] = threads
    result['total_time'] = stats['total_time']
    print(json.dumps(result))
    exit(1)

 
def main(cutoff):

    ranks = {}
    jstacks = []
    pid_dict = {}
    bash_command ="top -b -H -n1"

    start_time = current_milli_time()

    for j in range(10):
      jstacks.append({})
      output,error = subprocess.Popen(bash_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
  
      if (error != ''):
        print_and_exit(error=error)

      split = output.split('\n')
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
            tid = int(temp[0])
            if tid not in ranks:
              ranks[tid] = []
              ranks[tid].append(float(temp[8]))
            else:
              ranks[tid].append(float(temp[8]))

            if tid in pid_dict:
              pid = pid_dict[tid]
            else:
              get_pid_command = "cat /proc/"+str(tid)+"/status"
              output,error = subprocess.Popen(get_pid_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
              if error != '':
                pid_dict[tid] = -1
                continue

              output = output.split('\n')
              for line in output:
                temp = line.split()
                if temp[0] == 'Tgid:':
                  pid = int(temp[1])
                  pid_dict[tid] = pid
                  break

            if pid not in jstacks[j]:

              jstack_command = 'jstack -l '+str(pid)
              jstack_output,error = subprocess.Popen(jstack_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
              if error == '':
    
                jstacks[j][pid] = jstack_output

      time.sleep(1)



    refined_ranks = {}

    for key in ranks:
      if (len(ranks[key]) > 1) and pid_dict[key] != -1 :
        refined_ranks[key] = sum(ranks[key])/len(ranks[key])

    sorted_ranks = sorted(refined_ranks.items(), key=operator.itemgetter(1),reverse=True)

    consuming_threads = []
    for j in range(min(len(sorted_ranks),3)):
      temp = {}
      temp['cpu'] = sorted_ranks[j][1]
      temp['nid'] = sorted_ranks[j][0]
      temp['pid'] = pid_dict[temp['nid']]
      temp['jstacks'] = get_jstacks(jstacks,temp['pid'],temp['nid'])
      consuming_threads.append(temp)

    end_time = current_milli_time()
    stats = {}
    stats['total_time'] = end_time-start_time
    print_and_exit(stats=stats,threads=consuming_threads)

if __name__ == '__main__':

  ap = argparse.ArgumentParser()
  ap.add_argument("-c", "--cutoff",help="Percentage CPU cutoff")
  args = vars(ap.parse_args())

  if args["cutoff"] is None:
      args["cutoff"] = 10.0
  cutoff = float(args['cutoff'])
  main(cutoff)