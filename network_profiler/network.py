import time
import subprocess
import argparse
import json 
import operator
import socket

current_milli_time = lambda: int(round(time.time() * 1000))
size = {}
size['K'] = 1024
size['M'] = 1024*1024
size['G'] = 1024*1024*1024
size['T'] = 1024*1024*1024*1024
reverse = {}

def print_and_exit(error=None,ips=None):

  if  error is not None:
    result = {}
    result['success'] = 'false'
    result['reason'] = error
    result['ips'] = []
    print(json.dumps(result))
    exit(1)

  else:
    result = {}
    result['success'] = 'true'
    result['reason'] = ''
    result['ips'] = ips
    print(json.dumps(result))
    exit(1)

def tcp_parser(sockets_to_be_monitored):

    tcp_types = ['tcp','tcp6']

    for option in tcp_types:      

      tcp_command = "cat /proc/net/"+option

      tcp_output,error =  subprocess.Popen(tcp_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
      if error != '':
        print_and_exit(error)

      tcp_output = tcp_output.split('\n')[1:]
      for connection in tcp_output:
        for key in sockets_to_be_monitored:
          if connection.find(key) != -1:
            connection = connection.split()
            remote_addr = connection[2].split(':')
            local_addr = connection[1].split(':')
            remote_port = str(int(remote_addr[1],16))
            local_port = str(int(local_addr[1],16))


            remote_command = "ss -t | grep "+local_port
            remote_output,error = subprocess.Popen(remote_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

            if error!='':
              
              break


            remote_output = remote_output.split()
            
            if len(remote_output) < 5:
              
              break

            temp_ip = remote_output[4].split(':')
            remote_ip = temp_ip[len(temp_ip)-2]

            sockets_to_be_monitored[key]['local_port'] = local_port
            sockets_to_be_monitored[key]['remote_port'] = remote_port
            sockets_to_be_monitored[key]['remote_ip'] = remote_ip
            sockets_to_be_monitored[key]['success'] = 1
            reverse[local_port] = key
            
            break

    return sockets_to_be_monitored

def view_iptable(sockets_to_be_monitored,index):

  view_command = "iptables -n -L INPUT -v"
  view_output, error = subprocess.Popen(view_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate() 

  if error!='':
    print_and_exit(error)

  
  view_output = (view_output.split('\n'))[2:]
  for packet in view_output:
    packet = packet.split()
    

    if len(packet) < 10:
      continue
    bytes_rec = 0
    try:
      bytes_rec = int(packet[1])
    except:
      global size
      large_byte = packet[1]
      c_size = size[large_byte[-1]]
      large_byte = int(large_byte[:len(large_byte)-1])
      bytes_rec = large_byte*c_size

    
    socket = (packet[9].split(':')[1])

    if socket in reverse:
      sockets_to_be_monitored[reverse[socket]][index] = bytes_rec


def main(number):

  ps_command = "ps -ef | grep java"

  sockets_to_be_monitored = {}

  output,error = subprocess.Popen(ps_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
  if error != '':
    print_and_exit(error)

  output = output.split('\n')
  for process in output:
    temp = process.split()

    if len(temp)<2:
      continue

    pid = int(temp[1])
    

    ls_command = "ls -l /proc/"+temp[1]+"/fd"

    ls_output,error = subprocess.Popen(ls_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if error != '':
      continue

    
    ls_output = ls_output.split('\n')[1:]
    
    for fd in ls_output:
      
      fd_fields = fd.split()

      if len(fd_fields) < 11:
        continue
      socket_info = fd_fields[10].split(':')
      
      if socket_info[0] == 'socket':
        socket_number_string = socket_info[1]
        socket_number = (socket_number_string[1:len(socket_number_string)-1])
        sockets_to_be_monitored[socket_number] = {}
        sockets_to_be_monitored[socket_number]['pid'] = pid
        sockets_to_be_monitored[socket_number]['success'] = 0
        
  #print(sockets_to_be_monitored)
  sockets_to_be_monitored = tcp_parser(sockets_to_be_monitored)
  #print(sockets_to_be_monitored)

  for key in sockets_to_be_monitored:

    if sockets_to_be_monitored[key]['success'] == 1:
      iptable_command = 'iptables -A INPUT -p tcp --dport '+sockets_to_be_monitored[key]['local_port']
      iptable_output,error = subprocess.Popen(iptable_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
      if error!='':
        continue


  view_iptable(sockets_to_be_monitored,'initial_bytes')

  time.sleep(10)

  view_iptable(sockets_to_be_monitored,'final_bytes')

  stats = {}

  #print(sockets_to_be_monitored)
  for key in sockets_to_be_monitored:
    if 'initial_bytes' in sockets_to_be_monitored[key] and 'final_bytes' in sockets_to_be_monitored[key]:
      stats[key] = sockets_to_be_monitored[key]['final_bytes'] - sockets_to_be_monitored[key]['initial_bytes']

  sorted_bytes = sorted(stats.items(), key=operator.itemgetter(1),reverse=True)
  consuming_threads = []
  for j in range(min(len(sorted_bytes),number)):
    temp = {}
    temp['bytes'] = sorted_bytes[j][1]
    temp_socket = sorted_bytes[j][0]
    temp['pid'] = sockets_to_be_monitored[temp_socket]['pid']
    temp['remote_ip'] = sockets_to_be_monitored[temp_socket]['remote_ip']
    try:
      temp['remote_hostname'] = socket.gethostbyaddr(temp['remote_ip'])[0]
    except:
      temp['remote_hostname'] = 'Could not resolve'
    temp['remote_port'] = sockets_to_be_monitored[temp_socket]['remote_port']
    temp['local_port'] = sockets_to_be_monitored[temp_socket]['local_port']
    consuming_threads.append(temp)

  clean_command = "iptables -F INPUT"
  clean_output,error = subprocess.Popen(clean_command, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

  print_and_exit(ips=consuming_threads)


if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument("-n", "--number",help="Maximum number of Network Consuming connections")
  args = vars(ap.parse_args())

  if args["number"] is None:
      args["number"] = 3

  number = int(args['number'])
  main(number)

