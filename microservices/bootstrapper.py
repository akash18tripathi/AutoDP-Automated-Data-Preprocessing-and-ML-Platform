import subprocess
import os
import multiprocessing
import psutil


def start_service(service_name):
    try:
        subprocess.Popen(["python3", f"{service_name}.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
        print(f"=== Started {service_name}.py (PID: {os.getpid()}) ===")
    except Exception as e:
        print(f"Error starting {service_name}.py: {str(e)}")

def kill_processes_on_port(port):
    for process in psutil.process_iter(['pid', 'name']):
        try:
            connections = process.connections(kind='inet')
            for conn in connections:
                if conn.laddr.port == port:
                    print(f"Killing process {process.info()['pid']} ({process.info()['name']}) on port {port}")
                    process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


if __name__ == "__main__":
    # List of service scripts to start
    services_to_start = ["server","Data-Validation-Service/data_validation", "Data-Processing-Service/processing", "Model-Training-Service/training","Notification-Service/notification_service"]
    
    kill_processes_on_port(5000)
    kill_processes_on_port(5001)
    kill_processes_on_port(5002)
    kill_processes_on_port(5003)
    # Start each service in a separate process
    processes=[]
    for service in services_to_start:
        process = multiprocessing.Process(target=start_service, args=(service,))
        processes.append(process)
        process.start()
        # start_service(service)
    
    for process in processes:
        process.join()
