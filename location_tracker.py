import tkinter as tk
from tkinter import messagebox
import folium
import webbrowser
import socket
import json
import threading
import os
from datetime import datetime

class LocationTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Device Location Tracker")
        self.root.geometry("600x400")
        
        # Set up the server
        self.host = '0.0.0.0'  # Listen on all available interfaces
        self.port = 5000
        self.server_socket = None
        self.is_server_running = False
        self.locations = []
        
        # Create UI elements
        self.setup_ui()
        
    def setup_ui(self):
        # Server control frame
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(fill=tk.X)
        
        # IP Display
        ip_frame = tk.Frame(control_frame)
        ip_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(ip_frame, text="Your IP Address:").pack(side=tk.LEFT)
        self.ip_display = tk.Entry(ip_frame, width=20)
        self.ip_display.pack(side=tk.LEFT, padx=5)
        self.ip_display.insert(0, self.get_local_ip())
        self.ip_display.config(state='readonly')
        
        # Port Display
        port_frame = tk.Frame(control_frame)
        port_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
        self.port_display = tk.Entry(port_frame, width=10)
        self.port_display.pack(side=tk.LEFT, padx=5)
        self.port_display.insert(0, str(self.port))
        self.port_display.config(state='readonly')
        
        # Buttons
        button_frame = tk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = tk.Button(button_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.map_button = tk.Button(button_frame, text="Show Map", command=self.show_map, state=tk.DISABLED)
        self.map_button.pack(side=tk.LEFT, padx=5)
        
        # Status and location display
        self.status_label = tk.Label(self.root, text="Server Status: Stopped", bg="light gray", padx=10, pady=5)
        self.status_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Location history frame
        history_frame = tk.LabelFrame(self.root, text="Location History", padx=10, pady=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar for the history
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.location_listbox = tk.Listbox(history_frame, yscrollcommand=scrollbar.set)
        self.location_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.location_listbox.yview)
        
    def get_local_ip(self):
        try:
            # Create a socket to determine the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
            
    def start_server(self):
        if not self.is_server_running:
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen(5)
                
                self.is_server_running = True
                self.status_label.config(text="Server Status: Running", bg="light green")
                
                # Update button states
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                
                # Start a thread to listen for connections
                threading.Thread(target=self.listen_for_connections, daemon=True).start()
                
                messagebox.showinfo("Server Started", 
                                   f"Server is running at {self.get_local_ip()}:{self.port}\n"
                                   f"Configure your OWTracker app to send location to this address.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not start server: {str(e)}")
                
    def stop_server(self):
        if self.is_server_running:
            try:
                self.is_server_running = False
                self.server_socket.close()
                self.status_label.config(text="Server Status: Stopped", bg="light gray")
                
                # Update button states
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                
                if not self.locations:
                    self.map_button.config(state=tk.DISABLED)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error stopping server: {str(e)}")
                
    def listen_for_connections(self):
        while self.is_server_running:
            try:
                client_socket, address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True).start()
            except:
                # Server socket was closed or an error occurred
                break
                
    def handle_client(self, client_socket, address):
        try:
            data = b""
            while self.is_server_running:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                
                # Try to decode and process the data when we have a complete message
                try:
                    location_data = json.loads(data.decode('utf-8'))
                    self.process_location(location_data, address)
                    data = b""  # Reset data buffer after successful processing
                except json.JSONDecodeError:
                    # Not a complete JSON yet, continue receiving
                    pass
                    
        except Exception as e:
            print(f"Error handling client {address}: {str(e)}")
        finally:
            client_socket.close()
            
    def process_location(self, location_data, address):
        try:
            latitude = float(location_data.get('latitude', 0))
            longitude = float(location_data.get('longitude', 0))
            timestamp = location_data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            device_id = location_data.get('device_id', f"Unknown ({address[0]})")
            
            location_info = {
                'latitude': latitude,
                'longitude': longitude,
                'timestamp': timestamp,
                'device_id': device_id
            }
            
            self.locations.append(location_info)
            
            # Update UI from the main thread
            self.root.after(0, self.update_location_display, location_info)
            
            # Enable map button if we have locations
            if self.map_button['state'] == tk.DISABLED:
                self.root.after(0, lambda: self.map_button.config(state=tk.NORMAL))
                
        except Exception as e:
            print(f"Error processing location: {str(e)}")
            
    def update_location_display(self, location_info):
        # Add to the listbox
        display_text = f"{location_info['timestamp']} - {location_info['device_id']}: {location_info['latitude']:.6f}, {location_info['longitude']:.6f}"
        self.location_listbox.insert(tk.END, display_text)
        self.location_listbox.see(tk.END)  # Auto-scroll to the bottom
        
    def show_map(self):
        if not self.locations:
            messagebox.showinfo("No Data", "No location data available to display.")
            return
            
        # Get the most recent location
        latest = self.locations[-1]
        
        # Create a map centered at the latest location
        m = folium.Map(location=[latest['latitude'], latest['longitude']], zoom_start=14)
        
        # Add markers for all locations
        for loc in self.locations:
            popup_text = f"Device: {loc['device_id']}<br>Time: {loc['timestamp']}<br>Lat: {loc['latitude']:.6f}<br>Lng: {loc['longitude']:.6f}"
            folium.Marker(
                [loc['latitude'], loc['longitude']], 
                popup=popup_text
            ).add_to(m)
            
        # If we have multiple locations, add a line showing the path
        if len(self.locations) > 1:
            points = [(loc['latitude'], loc['longitude']) for loc in self.locations]
            folium.PolyLine(points, color="blue", weight=2.5, opacity=0.7).add_to(m)
        
        # Save the map to an HTML file
        map_file = os.path.join(os.path.expanduser("~"), "device_location_map.html")
        m.save(map_file)
        
        # Open the map in the default browser
        webbrowser.open('file://' + map_file)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = LocationTracker(root)
    root.mainloop()