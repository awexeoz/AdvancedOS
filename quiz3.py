import os
import platform
import psutil
import time
import socket
import matplotlib.pyplot as plt

def get_os_info():
    try:
        # Retrieve OS name and version
        os_name = platform.system()
        os_version = platform.version()
        
        # Retrieve processor information
        processor_info = platform.processor()
        
        # Retrieve memory in GB
        memory_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
        
        # Retrieve available disk space in GB
        disk_space_gb = round(psutil.disk_usage('/').free / (1024 ** 3), 2)
        
        # Retrieve current user
        current_user = os.getlogin()
        
        # Retrieve IP address
        ip_address = socket.gethostbyname(socket.gethostname())
        
        # Retrieve system uptime in seconds
        uptime_seconds = round(time.time() - psutil.boot_time())
        
        # Retrieve CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Retrieve running processes (with a limit of 10)
        running_processes = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'memory_percent'])
                running_processes.append(pinfo)
                if len(running_processes) >= 10:
                    break
            except psutil.NoSuchProcess:
                pass
        
        # Retrieve disk partitions
        disk_partitions = psutil.disk_partitions()
        
        # Retrieve system architecture
        system_architecture = platform.architecture()[0]
        
        # Retrieve environment variables (limit to 5)
        environment_variables = {k: os.environ[k] for k in list(os.environ)[:5]}
        
        return os_name, os_version, processor_info, memory_gb, disk_space_gb, current_user, ip_address, uptime_seconds, cpu_usage, running_processes, disk_partitions, system_architecture, environment_variables
    except PermissionError as e:
        print(f"Permission denied: {e}")
        return None
    except Exception as e:
        print(f"Error occurred while retrieving OS information: {e}")
        return None

def collect_data(duration_minutes):
    data = []  # List to store collected data
    end_time = time.time() + duration_minutes * 60  # Calculate end time
    
    while time.time() < end_time:
        os_info = get_os_info()  # Retrieve OS parameters
        if os_info:
            running_processes = os_info[9]  # Retrieve running processes
            process_memory = {}  # Dictionary to store memory usage for each process
            
            # Calculate memory usage for each process
            for proc in running_processes:
                pid = proc['pid']
                memory_percent = proc['memory_percent']
                if pid in process_memory:
                    process_memory[pid].append(memory_percent)
                else:
                    process_memory[pid] = [memory_percent]
            
            # Calculate average memory usage for each process
            avg_memory_usage = {pid: sum(memory) / len(memory) for pid, memory in process_memory.items()}
            
            data.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "cpu_usage": os_info[8],  # CPU usage
                "memory_usage": sum(proc['memory_percent'] for proc in running_processes),  # Total memory usage of running processes
                "disk_space_gb": os_info[4],  # Available disk space
                "running_processes": running_processes,  # Running processes
                "avg_memory_usage": avg_memory_usage  # Average memory usage for each process
            })
        time.sleep(60)  # Wait for 1 minute
    
    return data


def analyze_data(data):
    # Extract timestamps and CPU usage
    timestamps = [entry["timestamp"] for entry in data]
    cpu_usage = [entry["cpu_usage"] for entry in data]
    
    # Plot CPU usage over time
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, cpu_usage, marker='o', linestyle='-')
    plt.title('CPU Usage Over Time')
    plt.xlabel('Time')
    plt.ylabel('CPU Usage (%)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # Calculate average memory usage of each process
    processes_memory = {}
    for entry in data:
        for proc in entry["running_processes"]:
            pid = proc['pid']
            name = proc['name']
            memory_percent = proc['memory_percent']
            if pid in processes_memory:
                processes_memory[pid].append(memory_percent)
            else:
                processes_memory[pid] = [memory_percent]
    
    avg_memory_usage = {pid: sum(memory) / len(memory) for pid, memory in processes_memory.items()}
    max_memory_pid = max(avg_memory_usage, key=avg_memory_usage.get)
    
    # Find the process with the highest average memory usage
    max_memory_process = ""
    for entry in data:
        for proc in entry["running_processes"]:
            if proc['pid'] == max_memory_pid:
                max_memory_process = proc['name']
                break
        if max_memory_process:
            break
    
    # Extract timestamps and disk space
    disk_space_gb = [entry["disk_space_gb"] for entry in data]
    
    # Plot available disk space over time
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, disk_space_gb, marker='o', linestyle='-')
    plt.title('Available Disk Space Over Time')
    plt.xlabel('Time')
    plt.ylabel('Available Disk Space (GB)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # Print analysis results
    print("\nAnalysis Results:")
    print("=" * 30)
    print(f"Peak CPU Usage: {max(cpu_usage)}%")
    print(f"Process with Highest Average Memory Usage: {max_memory_process} (PID: {max_memory_pid})")
    print(f"Average Available Disk Space: {sum(disk_space_gb) / len(disk_space_gb)} GB")


def main():
    duration_minutes = 10 
    collected_data = collect_data(duration_minutes)
    
    if collected_data:
        analyze_data(collected_data)

if __name__ == "__main__":
    main()
