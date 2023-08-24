import os
import time
import csv
import pickle
import threading
import multiprocessing
from queue import Queue

def process_workspace(workspace_path):
    thread_id = threading.current_thread().name
    process_id = os.getpid()
    workspace_name = workspace_path.split('/')[-1]
    created_time = time.ctime(os.path.getctime(workspace_path))
    accessed_time = time.ctime(os.path.getatime(workspace_path))
    size_on_disk = os.path.getsize(workspace_path) // (1024 * 1024)  # in MB
    provisioned_space = os.statvfs(workspace_path).f_blocks * os.statvfs(workspace_path).f_frsize // (1024 * 1024)  # in MB

    workspace_info.append({
        'Thread': thread_id,
        'Process ID': process_id,
        'Folder': workspace_name,
        'Created Time': created_time,
        'Last Accessed Time': accessed_time,
        'Size on Disk (MB)': size_on_disk,
        'Provisioned Space (MB)': provisioned_space
    })
# add a comment again
    print(f"Thread: {thread_id}, PID: {process_id}, Processed: {workspace_path}")

def worker():
    while True:
        workspace_path = workspace_queue.get()
        if workspace_path is None:
            break
        process_workspace(workspace_path)
        workspace_queue.task_done()

def get_workspace_info(root_dir, checkpoint_file):
    global workspace_info
    workspace_info = []

    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'rb') as checkpoint:
            last_processed = pickle.load(checkpoint)
    else:
        last_processed = None

    for root, dirs, files in os.walk(root_dir):
        for dir_name in dirs:
            if dir_name.startswith(('j07', 'j04')):
                workspace_path = os.path.join(root, dir_name)

                if last_processed and workspace_path <= last_processed:
                    continue  # Skip directories already processed

                workspace_queue.put(workspace_path)

    with open(checkpoint_file, 'wb') as checkpoint:
        pickle.dump(workspace_path, checkpoint)

def write_to_file(workspace_info, output_file):
    with open(output_file, 'w', newline='') as f:
        fieldnames = ['Thread', 'Process ID', 'Folder', 'Created Time', 'Last Accessed Time', 'Size on Disk (MB)', 'Provisioned Space (MB)']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for info in workspace_info:
            writer.writerow(info)

if __name__ == "__main__":
    root_directory = "/gws"  # Change this to your root directory
    output_filename = "workspace_info.csv"
    checkpoint_filename = "checkpoint.pkl"
    max_threads = 6

    workspace_queue = Queue()
    threads = []

    for _ in range(max_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    get_workspace_info(root_directory, checkpoint_filename)

    for _ in range(max_threads):
        workspace_queue.put(None)

    for t in threads:
        t.join()

    write_to_file(workspace_info, output_filename)
    print(f"Workspace information has been written to {output_filename}")
