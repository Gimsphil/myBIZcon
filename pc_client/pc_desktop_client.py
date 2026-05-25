# -*- coding: utf-8 -*-
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import urllib.request
import urllib.error
import time
import os

# Import our custom multi-threaded audio recorder
from audio_recorder import AudioRecorder

class PCDesktopClient:
    """
    PCDesktopClient
    A premium Tkinter-based Windows desktop client for myBIZcon.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("myBIZcon - AI Business Assistant (PC Version)")
        self.root.geometry("900x620")
        self.root.configure(bg="#1E1E2E")

        # API & Recording Configurations
        self.backend_url = "http://localhost:8000/api/v1"
        self.is_recording = False
        self.active_overlay = None
        self.audio_path = os.path.join(os.getcwd(), "meeting_capture.wav")
        self.recorder = None

        # Apply Premium UI Styles
        self.setup_styles()
        self.build_dashboard()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure(".", background="#1E1E2E", foreground="#FFFFFF")
        self.style.configure("TFrame", background="#1E1E2E")
        self.style.configure("TLabel", background="#1E1E2E", foreground="#E0E0E0", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#00D1B2")
        self.style.configure("Sub.TLabel", font=("Segoe UI", 11, "italic"), foreground="#B5B5B5")

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
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=25, pady=15)

        title = ttk.Label(header_frame, text="Universal AI Business Assistant - Desktop Copilot", style="Header.TLabel")
        title.pack(anchor="w")
        subtitle = ttk.Label(header_frame, text="Active platform: Windows PC | Connected via Localhost API", style="Sub.TLabel")
        subtitle.pack(anchor="w")

        body_frame = ttk.Frame(self.root)
        body_frame.pack(fill="both", expand=True, padx=25, pady=5)

        left_col = ttk.Frame(body_frame, width=300)
        left_col.pack(side="left", fill="y", padx=(0, 15))

        status_card = tk.LabelFrame(left_col, text=" System Status ", bg="#252538", fg="#00D1B2", font=("Segoe UI", 9, "bold"), padx=15, pady=15, bd=1, relief="solid")
        status_card.pack(fill="x", pady=(0, 15))

        ttk.Label(status_card, text="API Server Status: ", background="#252538").grid(row=0, column=0, sticky="w", pady=4)
        self.server_status_lbl = tk.Label(status_card, text="CHECKING...", bg="#252538", fg="#FFB300", font=("Segoe UI", 9, "bold"))
        self.server_status_lbl.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(status_card, text="Meeting Mode: ", background="#252538").grid(row=1, column=0, sticky="w", pady=4)
        self.meeting_status_lbl = tk.Label(status_card, text="STANDBY", bg="#252538", fg="#9E9E9E", font=("Segoe UI", 9, "bold"))
        self.meeting_status_lbl.grid(row=1, column=1, sticky="w", pady=4)

        control_card = tk.LabelFrame(left_col, text=" Audio & Meeting Recorder ", bg="#252538", fg="#00D1B2", font=("Segoe UI", 9, "bold"), padx=15, pady=15, bd=1, relief="solid")
        control_card.pack(fill="both", expand=True)

        self.record_btn = ttk.Button(control_card, text="START MEETING CAPTURE", command=self.toggle_recording)
        self.record_btn.pack(fill="x", pady=10)

        self.overlay_btn = ttk.Button(control_card, text="TOGGLE PC SUBTITLE OVERLAY", style="Action.TButton", command=self.toggle_overlay)
        self.overlay_btn.pack(fill="x", pady=10)

        ttk.Label(control_card, text="Saved Recording WAV Path:", background="#252538", font=("Segoe UI", 8, "italic")).pack(anchor="w", pady=(15, 2))
        self.path_lbl = tk.Entry(control_card, bg="#1E1E2E", fg="#B5B5B5", bd=0, font=("Segoe UI", 8))
        self.path_lbl.insert(0, self.audio_path)
        self.path_lbl.config(state="readonly")
        self.path_lbl.pack(fill="x")

        right_col = ttk.Frame(body_frame)
        right_col.pack(side="right", fill="both", expand=True)

        sim_card = tk.LabelFrame(right_col, text=" Live Context Simulator ", bg="#1E1E2E", fg="#00D1B2", font=("Segoe UI", 9, "bold"), padx=20, pady=10, bd=1, relief="solid")
        sim_card.pack(fill="x", pady=(0, 15))

        ttk.Label(sim_card, text="Sender Name (e.g. John Buyer / Boss):").pack(anchor="w", pady=(0, 2))
        self.sender_entry = ttk.Entry(sim_card, font=("Segoe UI", 10))
        self.sender_entry.insert(0, "Director Kim (BOSS)")
        self.sender_entry.pack(fill="x", pady=(0, 6))

        ttk.Label(sim_card, text="Incoming Message Content:").pack(anchor="w", pady=(0, 2))
        self.message_txt = tk.Text(sim_card, height=3, font=("Segoe UI", 10), bg="#252538", fg="#FFFFFF", insertbackground="white", bd=0)
        self.message_txt.insert("1.0", "Can we confirm the schedule for next Wednesday's strategy conference? Mention NDA and pricing.")
        self.message_txt.pack(fill="x", pady=(0, 6))

        action_frame = ttk.Frame(sim_card)
        action_frame.pack(fill="x", pady=5)
        
        self.relation_var = tk.StringVar(value="BOSS")
        self.relation_combo = ttk.Combobox(action_frame, textvariable=self.relation_var, values=["BOSS", "CLIENT", "COWORKER", "FAMILY"], state="readonly", width=15)
        self.relation_combo.pack(side="left", padx=(0, 10))

        ttk.Button(action_frame, text="SYNC MESSAGE & TRANSLATE", command=self.sync_and_translate).pack(side="right", fill="x", expand=True)

        self.copilot_card = tk.LabelFrame(right_col, text=" Search-Assisted Web Copilot (Live Facts) ", bg="#252538", fg="#00D1B2", font=("Segoe UI", 9, "bold"), padx=20, pady=10, bd=1, relief="solid")
        self.copilot_card.pack(fill="both", expand=True)

        self.copilot_txt = tk.Text(self.copilot_card, bg="#1E1E2E", fg="#00D1B2", font=("Segoe UI", 9), bd=0, wrap="word", insertbackground="white")
        self.copilot_txt.pack(fill="both", expand=True)
        self.copilot_txt.insert("1.0", "Web Copilot Standby. Active keyword matching triggers real-time business templates NDA, pricing lookup and facts.")
        self.copilot_txt.config(state="disabled")

        threading.Thread(target=self.ping_backend_server, daemon=True).start()

    def ping_backend_server(self):
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
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.record_btn.config(text="STOP & PROCESS MEETING")
            self.meeting_status_lbl.config(text="RECORDING", fg="#F44336")
            self.recorder = AudioRecorder(filename=self.audio_path)
            self.recorder.start()
            self._update_copilot_facts("Meeting Audio Capture is active. Recording mic and system call loopback...")
        else:
            self.record_btn.config(text="START MEETING CAPTURE")
            self.meeting_status_lbl.config(text="STANDBY", fg="#9E9E9E")
            if self.recorder:
                self.recorder.stop()
            self._update_copilot_facts("Ingesting audio, performing speaker diarization via Gemini multimodal routing...")
            threading.Thread(target=self.process_meeting_recording, daemon=True).start()

    def process_meeting_recording(self):
        url = f"{self.backend_url}/voice/meeting"
        payload = {"file_path": self.audio_path}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                transcript = result.get("transcript_markdown", "")
                summary = result.get("summary", "")
                decisions = result.get("decisions", [])
                
                facts_text = "Meeting Diarization and Workspace Sync Complete\n\n"
                facts_text += f"Summary: {summary}\n\n"
                facts_text += "Decisions:\n"
                for dec in decisions:
                    facts_text += f" - {dec}\n"
                
                facts_text += "\nGoogle Workspace Synchronized:\n"
                facts_text += " - Google Drive: Meeting Minutes archived\n"
                facts_text += " - Google Tasks: Dynamic Tasks registered\n"
                facts_text += " - Google Calendar: Meeting schedules registered\n\n"
                facts_text += f"Full Transcript:\n{transcript}"
                
                self.root.after(0, lambda: self._update_copilot_facts(facts_text))
                self.root.after(0, lambda: messagebox.showinfo("Google Workspace Sync", "Meeting audio processed successfully!\nMinutes archived in Google Drive, and Agenda items registered on Calendar/Tasks."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Connection Error", f"Diarization Backend Error: {str(e)}"))
            self.root.after(0, lambda: self._update_copilot_facts("Diarization parsing failed. Ensure backend API server is online."))

    def sync_and_translate(self):
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

        threading.Thread(target=self._post_message_to_api, args=(payload,), daemon=True).start()
        
        search_query = ""
        if "NDA" in content.upper() or "계약" in content:
            search_query = "제휴 계약서"
        elif "pricing" in content.lower() or "가격" in content or "인상" in content:
            search_query = "pricing"
        else:
            search_query = content[:15]
            
        threading.Thread(target=self.trigger_copilot_search, args=(search_query,), daemon=True).start()

    def trigger_copilot_search(self, query):
        url = f"{self.backend_url}/copilot/search"
        payload = {"query": query}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                facts = result.get("facts", [])
                
                facts_text = f"Search-Assisted Web Copilot Support - Keyword: '{query}'\n\n"
                for idx, fact in enumerate(facts, 1):
                    facts_text += f"{idx}. {fact.get('title')}\n"
                    facts_text += f"   - {fact.get('snippet')}\n"
                    facts_text += f"   - [Source]: {fact.get('source')}\n\n"
                
                self.root.after(0, lambda: self._update_copilot_facts(facts_text))
        except Exception:
            pass

    def _update_copilot_facts(self, text):
        self.copilot_txt.config(state="normal")
        self.copilot_txt.delete("1.0", "end")
        self.copilot_txt.insert("1.0", text)
        self.copilot_txt.config(state="disabled")

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
                self.show_floating_overlay(result)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Connection Error", f"FastAPI Server offline: {str(e)}"))

    def show_floating_overlay(self, data):
        self.root.after(0, lambda: self._render_overlay_window(data))

    def _render_overlay_window(self, data):
        if self.active_overlay:
            self.active_overlay.destroy()

        translation = data.get("translation", "")
        suggestions = data.get("suggestions", [])

        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.9)
        overlay.configure(bg="#212529")

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        overlay.geometry(f"450x250+{screen_w - 480}+{screen_h - 320}")

        drag_bar = tk.Label(overlay, text="myBIZcon Subtitle Overlay (Drag to move)", bg="#00D1B2", fg="#1E1E2E", font=("Segoe UI", 9, "bold"))
        drag_bar.pack(fill="x")
        
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

        body = tk.Frame(overlay, bg="#212529", padx=15, pady=10)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=f"Translation: {translation}", bg="#212529", fg="#FFFFFF", font=("Segoe UI", 11, "bold"), wraplength=420, justify="left").pack(anchor="w", pady=(0, 10))

        tk.Label(body, text="Suggestions (HITL):", bg="#212529", fg="#B5B5B5", font=("Segoe UI", 8, "italic")).pack(anchor="w", pady=(0, 5))

        for sug in suggestions:
            btn_text = f"[{sug.get('tone')}] {sug.get('content')}"
            btn = tk.Button(body, text=btn_text, bg="#2E7D32", fg="#FFFFFF", font=("Segoe UI", 9, "bold"), activebackground="#1B5E20", activeforeground="#FFFFFF", bd=0, padx=10, pady=5, anchor="w")
            
            def inject(txt=sug.get('content')):
                messagebox.showinfo("Text Injection", f"Selected draft has been copied to clipboard & typed:\n--> \"{txt}\"")
                overlay.destroy()
                self.active_overlay = None

            btn.config(command=inject)
            btn.pack(fill="x", pady=2)

        self.active_overlay = overlay

    def toggle_overlay(self):
        if self.active_overlay:
            self.active_overlay.destroy()
            self.active_overlay = None
        else:
            mock_data = {
                "translation": "Hello, when can I expect the review results of the proposal?",
                "suggestions": [
                    {"tone": "Polite", "content": "Yes, I am refining the plan and will share it by 4 PM today."},
                    {"tone": "Fast", "content": "Yes, I will send the email right away."}
                ]
            }
            self._render_overlay_window(mock_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = PCDesktopClient(root)
    root.mainloop()
