The Project is a RCA (Root cause Analysis), specifically designed for Java Applications. It involves three Profiling scripts as of now. 

Required Installments - 
	
	1. Java
	2. jstack
	3. iotop - sudo yum install iotop (For CentOS)

Note - Runs only on Linux Machines. 

Usage -
	
	1. CPU_PROFILER 
           cd cpu_profiler
           sudo su - {name_of_user_running_java_process}
           python cpu.py *options*
        options are 
        	- --cutoff -> cutoff cpu percentage to monitor threads on. 

    2. IO_PROFILER 
    	   cd io_profiler
    	   sudo python ioc.py *options*
    	options are 
    		- --cutoff -> cutoff disk transfer speed in bytes/sec. 
    		- --user -> username under which java process is running. 

    3. NETWORK_PROFILER
    	   cd network_profiler
    	   sudo python network.py *options*
    	options are
    		- --number -> Maximum number of Network Consuming connections


Fields in JSON Outputs (All profilers give JSON output) -

	1. CPU_PROFILER - Json has following fields 
			- success -> true or false, depending upon script executed successfully. 
			- reason -> empty if executed successfully, else denotes the reason of script failure. 
			- total_time -> Time taken by script to run, 0 if script failed. 
			- consuming_threads -> Empty array if script fails, else an array of json objects (each json object is a thread with high cpu usage above cutoff), with fields as 
				- cpu -> cpu percentage usage by java thread
				- nid -> Kernel thread ID to which this java thread is mapped. 
				- pid -> process id of underlying java process
				- jstacks -> array of stack trace of java thread over a period of few seconds , to debug the underlying behaviour. 

	2. IO_PROFILER - Json has following fields
			- success -> true or false, depending upon script executed successfully. 
			- reason -> empty if executed successfully, else denotes the reason of script failure. 
			- consuming_threads -> Empty array if script fails, else an array of json objects (each json object is a thread with high disk I/O above cutoff speed), with fields as 
				- io -> Total disk I/O speed of thread, including reading and writing to the disk. 
				- nid -> Kernel thread ID to which this java thread is mapped. 
				- pid -> process id of underlying java process
				- jstacks -> array of stack trace of java thread over a period of few seconds , to debug the underlying behaviour. 

	3. NETWORK_PROFILER - Json has following fields - 
			- success -> true or false, depending upon script executed successfully. 
			- reason -> empty if executed successfully, else denotes the reason of script failure. 
			- ips -> Empty array if script fails, else an array of json objects (each json object is a network connection with high network usage), with fields as 
				- bytes -> Number of bytes sent/received over network. 
				- pid -> process id of the underlying java process of this connection.
				- remote_ip -> IP address(IPv4) of the remote server of connection.
				- remote_hostname -> Hostname of remote server of connection. 'Could not resolve' when hostname can not be resolved by script. 
				- remote_port -> port of the remote server of this connection.
				- local_port -> port of local machine which is used to establish this connection. 


