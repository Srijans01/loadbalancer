from dataclasses import dataclass
import http.server
import socketserver
import tkinter as tk
import threading
import requests


# Define the allowed client IP addresses
allowed_ips = [
    '127.0.0.1',  # Example: localhost
    '192.168.0.1'  # Add more IP addresses as needed
]

# Define the backend servers
backend_servers = [
    ('localhost', 9000),
    # Add more backend servers if needed
]

# Counter to keep track of the next backend server
current_server = 0

# Request counts dictionary to track request counts per backend server
request_counts = {}


# Define the request handler
class LoadBalancerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        if client_ip not in allowed_ips:
            self.send_error(403, "Forbidden")
            return
        self.proxy_request()

    def proxy_request(self):
        global current_server
        backend_server = backend_servers[current_server]
        current_server = (current_server + 1) % len(backend_servers)

        # Update request counts for the backend server
        if backend_server in request_counts:
            request_counts[backend_server] += 1
        else:
            request_counts[backend_server] = 1

        # Modify the request URL to include the '/api/list' path
        request_url = f"http://{backend_server[0]}:{backend_server[1]}/api/list"

        # Send the request to the backend server and receive the response
        response = requests.get(request_url)
        data = response.content

        # Send the backend server's response back to the client
        self.send_response(200)
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

        # Update the request counts in the UI
        update_request_counts()


# Function to add a backend server
def add_backend_server():
    server = entry_server.get()
    port = int(entry_port.get())
    backend_servers.append((server, port))
    entry_server.delete(0, tk.END)
    entry_port.delete(0, tk.END)
    update_backend_server_list()


# Function to remove a backend server
def remove_backend_server():
    selection = backend_listbox.curselection()
    if selection:
        index = selection[0]
        backend_servers.pop(index)
        update_backend_server_list()


# Function to update the backend server list
def update_backend_server_list():
    backend_listbox.delete(0, tk.END)
    for server, port in backend_servers:
        backend_listbox.insert(tk.END, f"{server}:{port}")


# Function to update the request counts in the UI
def update_request_counts():
    request_counts_text.delete('1.0', tk.END)
    for server in request_counts:
        count = request_counts[server]
        request_counts_text.insert(tk.END, f"Server: {server} - Request Count: {count}\n")


# Function to start the Load Balancer server
def start_load_balancer():
    load_balancer_server = socketserver.TCPServer(('localhost', 8000), LoadBalancerHandler)
    load_balancer_server.serve_forever()


# Create the Tkinter GUI
root = tk.Tk()
root.title("Load Balancer Configuration")

# Backend Server List
backend_frame = tk.Frame(root)
backend_frame.pack(pady=10)

backend_label = tk.Label(backend_frame, text="Backend Servers:")
backend_label.pack()

backend_listbox = tk.Listbox(backend_frame, width=40)
backend_listbox.pack(pady=5)

backend_scrollbar = tk.Scrollbar(backend_frame)
backend_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

backend_listbox.config(yscrollcommand=backend_scrollbar.set)
backend_scrollbar.config(command=backend_listbox.yview)

update_backend_server_list()

# Add Backend Server Form
add_backend_frame = tk.Frame(root)
add_backend_frame.pack(pady=10)

add_backend_label = tk.Label(add_backend_frame, text="Add Backend Server:")
add_backend_label.grid(row=0, column=0)

entry_server = tk.Entry(add_backend_frame, width=20)
entry_server.grid(row=0, column=1)

entry_port = tk.Entry(add_backend_frame, width=8)
entry_port.grid(row=0, column=2)

add_button = tk.Button(add_backend_frame, text="Add", command=add_backend_server)
add_button.grid(row=0, column=3, padx=10)

remove_button = tk.Button(add_backend_frame, text="Remove", command=remove_backend_server)
remove_button.grid(row=0, column=4)


# Request Counts
request_counts_frame = tk.Frame(root)
request_counts_frame.pack(pady=10)

request_counts_label = tk.Label(request_counts_frame, text="Request Counts:")
request_counts_label.pack()

request_counts_text = tk.Text(request_counts_frame, width=40, height=10)
request_counts_text.pack()

# Start the Load Balancer server in a separate thread
load_balancer_thread = threading.Thread(target=start_load_balancer)
load_balancer_thread.start()

# Start the Tkinter main event loop
root.mainloop()
