import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import urllib.request
import urllib.error
import time

class PCDesktopClient:
    """
    🖥️ PCDesktopClient
    A premium Tkinter-based Windows desktop client for myBIZcon.
    Features:
    1. Premium dark-theme dashboard matching professional bi-modal design parameters.
    2. Frameless, semi-transparent Windows Overlay for floating live translations and replies.
    3. Active message simulator & Gemini API interface.
    4. Audio recording controls for PC-based meetings.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("myBIZcon — AI Business Assistant (PC Version)")
        self.root.geometry("850x550")
        self.root.configure(bg="#1E1E2E") # Vibrant sleek slate dark mode

        # API Configurations
        self.backend_url = "http://localhost:8000/api/v1"
        self.is_recording = False
        self.active_overlay = None

        # Apply Premium UI Styles
        self.setup_styles()
        self.build_dashboard()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure slate dark elements
        self.style.configure(".", background="#1E1E2E", foreground="#FFFFFF")
        self.style.configure("TFrame", background="#1E1E2E")
        self.style.configure("TLabel", background="#1E1E2E", foreground="#E0E0E0", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#00D1B2")
        self.style.configure("Sub.TLabel", font=("Segoe UI", 11, "italic"), foreground="#B5B5B5")

        # Sleek Premium Buttons style
        self.style.configure("TButton", 
            background="#2E7D32", 
            foreground="#FFFFFF", 
            bordercolor="#2E7D32", 
            font=("Segoe UI", 10, "bold"),
            padding=8
        )
        self.style.map("TButton",
            background=[("active", "#1B5E20")],
            bordercolor=[("active", "#1B5E20")]
        )

        self.style.configure("Action.TButton", 
            background="#008080", 
            foreground="#FFFFFF", 
            bordercolor="#008080",
            font=("Segoe UI", 10, "bold")
        )

    def build_dashboard(self):
        # Master Layout: Top header, Left settings, Right simulation
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=25, pady=15)

        title = ttk.Label(header_frame, text="🌐 myBIZcon AI Assistant — Desktop Copilot", style="Header.TLabel")
        title.pack(anchor="w")
        subtitle = ttk.Label(header_frame, text="Active platform: Windows PC | Connected via Localhost API", style="Sub.TLabel")
        subtitle.pack(anchor="w")

        # Main Body Splitter
        body_frame = ttk.Frame(self.root)
        body_frame.pack(fill="both", expand=True, padx=25, pady=5)

        # Left Column: Configuration & Status
        left_col = ttk.Frame(body_frame, width=280)
        left_col.pack(side="left", fill="y", padx=(0, 15))

        # Status Panel Card
        status_card = tk.LabelFrame(left_col, text=" System Status ", bg="#252538", fg="#00D1B2", font=("Segoe UI", 9, "bold"), padx=15, pady=15, bd=1, relief="solid")
        status_card.pack(fill="x", pady=(0, 15))

        ttk.Label(status_card, text="API Server Status: ", background="#252538").grid(row=0, column=0, sticky="w", pady=4)
        self.server_status_lbl = tk.Label(status_card, text="CHECKING...", bg="#252538", fg="#FFB300", font=("Segoe UI", 9, "bold"))
        self.server_status_lbl.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(status_card, text="Meeting Mode: ", background="#252538").grid(row=1, column=0, sticky="w", pady=4)
        self.meeting_status_lbl = tk.Label(status_card, text="STANDBY", bg="#252538", fg="#9E9E9E", font=("Segoe UI", 9, "bold"))
        self.meeting_status_lbl.grid(row=1, column=1, sticky="w", pady=4)

        # Quick Control Panel
        control_card = tk.LabelFrame(left_col, text=" Audio & Meeting Recorder ", bg="#252538", fg="#00D1B2", font=("Segoe UI", 9, "bold"), padx=15, pady=15, bd=1, relief="solid")
        control_card.pack(fill="x", expand=True)

        self.record_btn = ttk.Button(control_card, text="🎙️ START MEETING CAPTURE", command=self.toggle_recording)
        self.record_btn.pack(fill="x", pady=10)

        self.overlay_btn = ttk.Button(control_card, text="🖥️ TOGGLE PC SUBTITLE OVERLAY", style="Action.TButton", command=self.toggle_overlay)
        self.overlay_btn.pack(fill="x", pady=10)

        # Right Column: Messaging & Workspace Simulation Workspace
        right_col = tk.LabelFrame(body_frame, text=" Live Context Simulator ", bg="#1E1E2E", fg="#00D1B2", font=("Segoe UI", 9, "bold"), padx=20, pady=15, bd=1, relief="solid")
        right_col.pack(side="right", fill="both", expand=True)

        # Message Entry Fields
        ttk.Label(right_col, text="Sender Name (e.g. John Buyer / Boss):").pack(anchor="w", pady=(0, 2))
        self.sender_entry = ttk.Entry(right_col, font=("Segoe UI", 10))
        self.sender_entry.insert(0, "Director Kim (BOSS)")
        self.sender_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(right_col, text="Incoming Message Content:").pack(anchor="w", pady=(0, 2))
        self.message_txt = tk.Text(right_col, height=4, font=("Segoe UI", 10), bg="#252538", fg="#FFFFFF", insertbackground="white", bd=0)
        self.message_txt.insert("1.0", "Can we confirm the schedule for next Wednesday's strategy conference?")
        self.message_txt.pack(fill="x", pady=(0, 10))

        # Relationship Selector
        ttk.Label(right_col, text="Relationship Profile:").pack(anchor="w", pady=(0, 2))
        self.relation_var = tk.StringVar(value="BOSS")
        self.relation_combo = ttk.Combobox(right_col, textvariable=self.relation_var, values=["BOSS", "CLIENT", "COWORKER", "FAMILY"], state="readonly")
        self.relation_combo.pack(fill="x", pady=(0, 15))

        # Action Buttons
        ttk.Button(right_col, text="⚡ SYNC MESSAGE & TRANSLATE", command=self.sync_and_translate).pack(fill="x")

        # Periodically check server status in background
        threading.Thread(target=self.ping_backend_server, daemon=True).start()

    def ping_backend_server(self):
        """Pings FastAPI backend to verify connection status."""
        while True:
            try:
                with urllib.request.urlopen(self.backend_url, timeout=3.0) as response:
                    if response.status == 200:
                        self.server_status_lbl.config(text="ONLINE", fg="#00D1B2")
                    else:
                        self.server_status_lbl.config(text="ERROR", fg="#F44336")
            except Exception:
                self.server_status_lbl.config(text="OFFLINE", fg="#F44336")
            time.sleep(5)

    def toggle_recording(self):
        """Toggles Zoom/Meeting audio recording status."""
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.record_btn.config(text="🛑 STOP & SAVE MINUTES")
            self.meeting_status_lbl.config(text="RECORDING", fg="#F44336")
            # Simulate physical recording
            messagebox.showinfo("Meeting Mode Activated", "PC microphone is now listening. Generating live diarized meeting transcript.")
        else:
            self.record_btn.config(text="🎙️ START MEETING CAPTURE")
            self.meeting_status_lbl.config(text="STANDBY", fg="#9E9E9E")
            
            # Post mock meeting backup to Drive
            self.generate_and_save_minutes()

    def generate_and_save_minutes(self):
        """Mock pipeline saving meeting minutes to Drive."""
        mock_payload = {
            "title": f"PC Meeting minutes {time.strftime('%Y-%m-%d %H:%M')}",
            "transcript_markdown": (
                "## 📝 PC Meeting Summary\n"
                "Attendees: Speaker A (Client), Speaker B (User)\n\n"
                "### Key Decisions:\n"
                "- Confirmed the pricing schedule adjustment to +5%.\n"
                "- Approved development phase milestones.\n\n"
                "### Action Items:\n"
                "- User: Register Tasks schedules in Calendar.\n"
            )
        }
        
        # Trigger FastAPI workspace archival API
        url = f"{self.backend_url}/workspace/backup"
        req = urllib.request.Request(
            url,
            data=json.dumps(mock_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                messagebox.showinfo("Google Drive Archive", f"Meeting transcript processed and saved directly to Drive.\nPath: {result.get('filename')}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sync with FastAPI: {str(e)}")

    def sync_and_translate(self):
        """Synchronizes message with backend to generate translations and overlays."""
        sender = self.sender_entry.get().strip()
        content = self.message_txt.get("1.0", "end-1c").strip()
        relation = self.relation_var.get()

        if not content:
            messagebox.showwarning("Warning", "Please enter message content.")
            return

        payload = {
            "sender": sender,
            "content": content,
            "conversation_title": sender,
            "relationship": relation,
            "is_group": False
        }

        # Send request
        threading.Thread(target=self._post_message_to_api, args=(payload,), daemon=True).start()

    def _post_message_to_api(self, payload):
        url = f"{self.backend_url}/chat/message"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                # Update floating overlays
                self.show_floating_overlay(result)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Connection Error", f"FastAPI Server offline: {str(e)}"))

    def show_floating_overlay(self, data):
        """Displays or updates the frameless transparent subtitle overlay on PC screen."""
        self.root.after(0, lambda: self._render_overlay_window(data))

    def _render_overlay_window(self, data):
        if self.active_overlay:
            self.active_overlay.destroy()

        translation = data.get("translation", "")
        suggestions = data.get("suggestions", [])

        # Create transparent floating Tkinter window
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True) # Frameless
        overlay.attributes("-topmost", True) # Keep on top of all windows
        overlay.attributes("-alpha", 0.9) # Transparent
        overlay.configure(bg="#212529")

        # Place bottom right
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        overlay.geometry(f"450x250+{screen_w - 480}+{screen_h - 320}")

        # Drag handle
        drag_bar = tk.Label(overlay, text="🌐 myBIZcon Subtitle Overlay (Drag to move)", bg="#00D1B2", fg="#1E1E2E", font=("Segoe UI", 9, "bold"))
        drag_bar.pack(fill="x")
        
        # Make draggable
        def make_draggable(widget):
            def start_drag(event):
                widget.x = event.x
                widget.y = event.y
            def drag(event):
                deltax = event.x - widget.x
                deltay = event.y - widget.y
                x = overlay.winfo_x() + deltax
                y = overlay.winfo_y() + deltay
                overlay.geometry(f"+{x}+{y}")
            widget.bind("<Button-1>", start_drag)
            widget.bind("<B1-Motion>", drag)

        make_draggable(drag_bar)

        # Content
        body = tk.Frame(overlay, bg="#212529", padx=15, pady=10)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=f"🎯 번역: {translation}", bg="#212529", fg="#FFFFFF", font=("Segoe UI", 11, "bold"), wraplength=420, justify="left").pack(anchor="w", pady=(0, 10))

        tk.Label(body, text="💡 추천 답변 선택 (HITL):", bg="#212529", fg="#B5B5B5", font=("Segoe UI", 8, "italic")).pack(anchor="w", pady=(0, 5))

        for sug in suggestions:
            btn_text = f"[{sug.get('tone')}] {sug.get('content')}"
            btn = tk.Button(body, text=btn_text, bg="#2E7D32", fg="#FFFFFF", font=("Segoe UI", 9, "bold"), activebackground="#1B5E20", activeforeground="#FFFFFF", bd=0, padx=10, pady=5, anchor="w")
            
            # Simulated text injection
            def inject(txt=sug.get('content')):
                messagebox.showinfo("Text Injection", f"Selected draft has been copied to clipboard & typed:\n--> \"{txt}\"")
                overlay.destroy()
                self.active_overlay = None

            btn.config(command=inject)
            btn.pack(fill="x", pady=2)

        self.active_overlay = overlay

    def toggle_overlay(self):
        """Toggles the state of subtitle overlay manually."""
        if self.active_overlay:
            self.active_overlay.destroy()
            self.active_overlay = None
        else:
            mock_data = {
                "translation": "안녕하세요, 제안서 검토 결과를 언제쯤 공유받을 수 있을까요?",
                "suggestions": [
                    {"tone": "예의 바름", "content": "네, 현재 기획안 조정 중으로 금일 오후 4시 전까지 공유드리겠습니다."},
                    {"tone": "신속 답변", "content": "네, 바로 이메일 발송해 드리겠습니다."}
                ]
            }
            self._render_overlay_window(mock_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = PCDesktopClient(root)
    root.mainloop()
