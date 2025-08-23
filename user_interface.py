"""
User Interface Module
Handles all GUI components and user interactions for the P2P Chat application.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox


class UserInterface:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        """Configure TTK styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TChat.TLabel', background='#e3f2fd', padding=5)
        self.style.configure('Status.TLabel', background='#e0e0e0', font=('Arial', 9))

    def create_widgets(self):
        """Create all GUI widgets"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Network setup frame
        self.create_network_frame(main_frame)
        
        # Chat area
        self.create_chat_area(main_frame)
        
        # Message input frame
        self.create_message_frame(main_frame)
        
        # Status bar
        self.create_status_bar()
        
        # Initialize with nickname prompt
        self.root.after(500, self.prompt_nickname)

    def create_network_frame(self, parent):
        """Create the network setup section"""
        conn_frame = ttk.LabelFrame(parent, text=" P2P Network Setup ", padding=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Port configuration
        port_frame = ttk.Frame(conn_frame)
        port_frame.pack(fill=tk.X, pady=2)
        ttk.Label(port_frame, text="Listen Port:").pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar(value=str(self.app.my_port))
        port_entry = ttk.Entry(port_frame, textvariable=self.port_var, width=10)
        port_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(port_frame, text="Start Listening", command=self.start_listening).pack(side=tk.LEFT, padx=5)

        # Connect to peer frame
        peer_frame = ttk.Frame(conn_frame)
        peer_frame.pack(fill=tk.X, pady=2)
        ttk.Label(peer_frame, text="Connect to Peer:").pack(side=tk.LEFT, padx=5)
        self.peer_ip_var = tk.StringVar()
        ip_entry = ttk.Entry(peer_frame, textvariable=self.peer_ip_var, width=15)
        ip_entry.pack(side=tk.LEFT, padx=2)
        self.peer_port_var = tk.StringVar()
        port_entry = ttk.Entry(peer_frame, textvariable=self.peer_port_var, width=8)
        port_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(peer_frame, text="Connect", command=self.connect_to_peer).pack(side=tk.LEFT, padx=5)
        
        # Add placeholder-like labels
        if not self.peer_ip_var.get():
            ip_entry.insert(0, "IP Address")
            ip_entry.bind('<FocusIn>', lambda e: self.clear_placeholder(ip_entry, "IP Address"))
        if not self.peer_port_var.get():
            port_entry.insert(0, "Port")
            port_entry.bind('<FocusIn>', lambda e: self.clear_placeholder(port_entry, "Port"))

        # Peer list frame
        list_frame = ttk.Frame(conn_frame)
        list_frame.pack(fill=tk.X, pady=2)
        ttk.Label(list_frame, text="Connected Peers:").pack(side=tk.LEFT, padx=5)
        self.peer_count_label = ttk.Label(list_frame, text="0")
        self.peer_count_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(list_frame, text="Show Peers", command=self.show_peer_list).pack(side=tk.LEFT, padx=5)

    def create_chat_area(self, parent):
        """Create the chat display area"""
        self.chat_area = scrolledtext.ScrolledText(
            parent, wrap=tk.WORD, state='disabled',
            font=('Arial', 11), padx=10, pady=5
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def create_message_frame(self, parent):
        """Create the message input section"""
        msg_frame = ttk.Frame(parent)
        msg_frame.pack(fill=tk.X, padx=10, pady=5)

        self.msg_entry = ttk.Entry(msg_frame, font=('Arial', 12))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.msg_entry.bind("<Return>", self.send_message)

        ttk.Button(msg_frame, text="Send", command=self.send_message).pack(side=tk.LEFT)
        ttk.Button(msg_frame, text="File", command=self.send_file).pack(side=tk.LEFT)

        self.emoji_var = tk.StringVar()
        emoji_menu = ttk.OptionMenu(msg_frame, self.emoji_var, "😊", "😊", "😂", "❤", "👍", command=self.insert_emoji)
        emoji_menu.pack(side=tk.LEFT)

    def create_status_bar(self):
        """Create the status bar"""
        self.status = ttk.Label(self.root, text=f"Ready - Local IP: {self.app.network.get_local_ip()}",
                                style='Status.TLabel', anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def clear_placeholder(self, entry, placeholder):
        """Clear placeholder text when entry gets focus"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def prompt_nickname(self):
        """Prompt user for nickname"""
        nickname = simpledialog.askstring("Nickname", "Choose a nickname:", parent=self.root)
        if nickname:
            self.app.nickname = nickname
            self.update_chat(f"[System] Nickname set to {nickname}", 'system')

    def start_listening(self):
        """Start listening for incoming connections"""
        try:
            port = int(self.port_var.get())
            self.app.my_port = port
            success, message = self.app.network.start_listening(port)
            
            if success:
                self.update_status(message)
                self.update_chat(f"[System] Started listening on port {port}", 'system')
            else:
                messagebox.showerror("Error", message)
                
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")

    def connect_to_peer(self):
        """Connect to a peer using GUI inputs"""
        peer_ip = self.peer_ip_var.get().strip()
        peer_port_str = self.peer_port_var.get().strip()
        
        if not peer_ip or not peer_port_str or peer_ip == "IP Address" or peer_port_str == "Port":
            messagebox.showwarning("Input Required", "Please enter both IP address and port")
            return
            
        try:
            peer_port = int(peer_port_str)
            success, message = self.app.network.connect_to_peer(peer_ip, peer_port, self.app.my_port, self.app.nickname)
            
            if success:
                self.update_peer_count()
                self.update_chat(f"[System] {message}", 'system')
                self.peer_ip_var.set("")
                self.peer_port_var.set("")
            else:
                messagebox.showerror("Connection Failed", message)
                
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")

    def send_message(self, event=None):
        """Send a message"""
        msg = self.msg_entry.get().strip()
        if not msg:
            return
        self.msg_entry.delete(0, tk.END)
        
        self.app.message_handler.process_message(msg)

    def send_file(self):
        """Send a file"""
        self.app.message_handler.send_file()

    def insert_emoji(self, emoji):
        """Insert emoji into message entry"""
        self.msg_entry.insert(tk.END, emoji)

    def update_chat(self, message, msg_type='system'):
        """Update the chat display"""
        self.chat_area.config(state='normal')
        tag = msg_type
        self.chat_area.tag_config('system', foreground='#666666')
        self.chat_area.tag_config('self', foreground='#2c3e50', font=('Arial', 11, 'bold'))
        self.chat_area.tag_config('peer', foreground='#27ae60')
        self.chat_area.tag_config('error', foreground='#c0392b')
        self.chat_area.insert(tk.END, message + "\n", tag)
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def update_status(self, text):
        """Update status bar"""
        self.status.config(text=text)

    def update_peer_count(self):
        """Update the peer count display"""
        count = self.app.network.get_peer_count()
        self.peer_count_label.config(text=str(count))

    def show_peer_list(self):
        """Show list of connected and known peers"""
        peer_info = self.app.network.get_peer_list_info()
        messagebox.showinfo("Peer List", peer_info)
