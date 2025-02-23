import os
import re
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from moviepy.video.io.VideoFileClip import VideoFileClip  # Current MoviePy import

# --- Helper Functions ---
def srt_time_to_seconds(srt_time):
    """
    Converts the time in SRT format to seconds.
    Example: "00:03:08,480" -> 188.48
    """
    h, m, s_ms = srt_time.split(':')
    s, ms = s_ms.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def parse_srt(content):
    """
    Takes SRT content and returns a list containing each subtitle block 
    (start time, text).
    """
    blocks = content.strip().split('\n\n')
    subtitles = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) >= 3:
            time_line = lines[1]
            text = " ".join(lines[2:])
            start_time_str = time_line.split(" --> ")[0]
            start_time = srt_time_to_seconds(start_time_str)
            subtitles.append((start_time, text))
    return subtitles

# --- Tab 1: NGram (Bigram & Trigram) Creator (Multiple File Selection and Automatic Output Folder) ---
class GramCreatorTab(tk.Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.main_app = main_app
        self.srt_file_paths = []  # List for multiple file selection
        self.ngram_outputs = {}   # {filename: ngram_dict}
        # Create output folder (in the directory where the code is located, named "ngram_outputs")
        self.output_folder = os.path.join(os.getcwd(), "ngram_outputs")
        os.makedirs(self.output_folder, exist_ok=True)
        self.create_widgets()

    def create_widgets(self):
        file_frame = ttk.LabelFrame(self, text="File(s) Selection")
        file_frame.pack(fill="x", padx=10, pady=5)
        self.file_label = ttk.Label(file_frame, text="No file selected yet.")
        self.file_label.pack(side="left", padx=10, pady=5)
        select_button = ttk.Button(file_frame, text="Select File(s)", command=self.select_files)
        select_button.pack(side="right", padx=10, pady=5)

        options_frame = ttk.LabelFrame(self, text="Options")
        options_frame.pack(fill="x", padx=10, pady=5)
        output_label = ttk.Label(options_frame, text="Output Format:")
        output_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.output_format = tk.StringVar()
        self.output_combobox = ttk.Combobox(options_frame, textvariable=self.output_format, state="readonly",
                                              values=["JSON", "TXT"])
        self.output_combobox.current(0)
        self.output_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.case_insensitive_var = tk.BooleanVar(value=True)
        case_check = ttk.Checkbutton(options_frame, text="Convert to lowercase (Case Insensitive)",
                                     variable=self.case_insensitive_var)
        case_check.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        progress_frame = ttk.LabelFrame(self, text="Progress / Log")
        progress_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.log_text = tk.Text(progress_frame, wrap="word", height=15)
        self.log_text.pack(fill="both", padx=10, pady=5, expand=True)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=5)
        start_button = ttk.Button(button_frame, text="Start", command=self.start_processing)
        start_button.grid(row=0, column=0, padx=5)
        save_detailed_button = ttk.Button(button_frame, text="Save Detailed Output", command=self.save_detailed_output)
        save_detailed_button.grid(row=0, column=1, padx=5)
        save_plain_button = ttk.Button(button_frame, text="Save Plain Text Output", command=self.save_plain_text_output)
        save_plain_button.grid(row=0, column=2, padx=5)

    def select_files(self):
        file_paths = filedialog.askopenfilenames(title="Select SRT Files",
                                                 filetypes=[("SRT Files", "*.srt"), ("All Files", "*.*")])
        if file_paths:
            self.srt_file_paths = list(file_paths)
            filenames = [os.path.basename(p) for p in self.srt_file_paths]
            self.file_label.config(text=", ".join(filenames))
            self.log("Selected files: " + ", ".join(self.srt_file_paths))

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_processing(self):
        if not self.srt_file_paths:
            messagebox.showwarning("Warning", "Please select at least one SRT file.")
            return
        self.log("Processing started...")
        self.progress_bar['value'] = 0
        threading.Thread(target=self.process_files, daemon=True).start()

    def process_files(self):
        self.ngram_outputs = {}
        total_files = len(self.srt_file_paths)
        for idx, file_path in enumerate(self.srt_file_paths):
            self.log(f"Processing: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                subtitles = parse_srt(content)
                ngram_dict = {}
                for start_time, text in subtitles:
                    if self.case_insensitive_var.get():
                        text = text.lower()
                    words = re.findall(r'\b\w+\b', text, flags=re.UNICODE)
                    # Bigrams:
                    for i in range(len(words) - 1):
                        gram = words[i] + " " + words[i+1]
                        ngram_dict.setdefault(gram, []).append(start_time)
                    # Trigrams:
                    for i in range(len(words) - 2):
                        gram = words[i] + " " + words[i+1] + " " + words[i+2]
                        ngram_dict.setdefault(gram, []).append(start_time)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                self.ngram_outputs[base_name] = ngram_dict
                self.log(f"{base_name} file processed. {len(ngram_dict)} ngrams found.")
            except Exception as e:
                self.log(f"Error {file_path}: {e}")
            self.progress_bar['value'] = (idx + 1) / total_files * 100
        self.log("All files processed.")

    def save_detailed_output(self):
        if not self.ngram_outputs:
            messagebox.showwarning("Warning", "Please process the files first.")
            return
        output_format = self.output_format.get()
        for base_name, ngram_dict in self.ngram_outputs.items():
            if output_format == "JSON":
                output_str = json.dumps(ngram_dict, ensure_ascii=False, indent=4)
                ext = ".json"
            else:
                lines = []
                for gram, times in ngram_dict.items():
                    lines.append(f"{gram}: {times}")
                output_str = "\n".join(lines)
                ext = ".txt"
            output_path = os.path.join(self.output_folder, base_name + "_detailed" + ext)
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output_str)
                self.log(f"Detailed output saved: {output_path}")
            except Exception as e:
                self.log(f"Error saving output for {base_name}: {e}")

    def save_plain_text_output(self):
        if not self.ngram_outputs:
            messagebox.showwarning("Warning", "Please process the files first.")
            return
        # In the plain text output, only the ngram words (bigram and trigram) will be included.
        # Each will be enclosed in quotes and combined into a single, comma-separated line.
        for base_name, ngram_dict in self.ngram_outputs.items():
            ngram_list = list(ngram_dict.keys())
            # Enclose each ngram in quotes and create a comma-separated string.
            output_str = ", ".join([f"\"{ng}\"" for ng in ngram_list])
            output_path = os.path.join(self.output_folder, base_name + "_plain.txt")
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output_str)
                self.log(f"Plain text output saved: {output_path}")
            except Exception as e:
                self.log(f"Error saving plain text output for {base_name}: {e}")

# --- Tab 2: NGram Query and Query Output Generation ---
class GramQueryTab(tk.Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.main_app = main_app
        self.loaded_outputs = []  # List of tuples: (filename, dictionary)
        self.query_results = []   # Query results; each entry is a dict with keys: ngram, type, indices, matches, found
        self.create_widgets()

    def create_widgets(self):
        query_frame = ttk.LabelFrame(self, text="Query Sentence")
        query_frame.pack(fill="x", padx=10, pady=5)
        self.query_text = tk.Text(query_frame, height=4, wrap="word")
        self.query_text.pack(fill="x", padx=10, pady=5)
        options_frame = ttk.Frame(self)
        options_frame.pack(fill="x", padx=10, pady=5)
        self.case_insensitive = tk.BooleanVar(value=True)
        case_check = ttk.Checkbutton(options_frame, text="Convert to lowercase (Case Insensitive)", variable=self.case_insensitive)
        case_check.pack(side="left", padx=5)
        load_frame = ttk.Frame(self)
        load_frame.pack(fill="x", padx=10, pady=5)
        load_button = ttk.Button(load_frame, text="Load Output Files", command=self.load_output_files)
        load_button.pack(side="left", padx=5)
        self.loaded_label = ttk.Label(load_frame, text="No file loaded yet.")
        self.loaded_label.pack(side="left", padx=5)
        search_button = ttk.Button(self, text="Search", command=self.search_ngrams)
        search_button.pack(pady=5)
        output_button = ttk.Button(self, text="Get Query Output", command=self.save_query_output)
        output_button.pack(pady=5)
        result_frame = ttk.LabelFrame(self, text="Search Results")
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.results_text = tk.Text(result_frame, wrap="word")
        self.results_text.pack(fill="both", padx=10, pady=5, expand=True)
        self.results_text.tag_configure("missing", foreground="red")

    def load_output_files(self):
        file_paths = filedialog.askopenfilenames(title="Select Output Files",
                                                 filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt")])
        if not file_paths:
            return
        self.loaded_outputs.clear()
        file_names = []
        for path in file_paths:
            try:
                if path.lower().endswith(".json"):
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.loaded_outputs.append((os.path.basename(path), data))
                    file_names.append(os.path.basename(path))
                else:
                    data = {}
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if ": " in line:
                                parts = line.strip().split(": ", 1)
                                key = parts[0]
                                try:
                                    value = eval(parts[1])
                                except Exception:
                                    value = []
                                data[key] = value
                    self.loaded_outputs.append((os.path.basename(path), data))
                    file_names.append(os.path.basename(path))
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while loading {os.path.basename(path)}: {e}")
        self.loaded_label.config(text="Loaded files: " + ", ".join(file_names))

    def search_ngrams(self):
        """
        Using a greedy approach, splits the query sentence from left to right into segments:
        - First, checks for trigrams.
        - If not found, checks for bigrams.
        - Whichever is found, that segment is taken and indices are skipped.
        Thus, overlapping and repetitions are prevented.
        """
        self.results_text.delete("1.0", tk.END)
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query sentence.")
            return
        if self.case_insensitive.get():
            query = query.lower()
        words = re.findall(r'\b\w+\b', query, flags=re.UNICODE)
        self.query_results = []
        i = 0
        while i < len(words):
            # First check for trigram
            if i <= len(words) - 3:
                trigram = " ".join(words[i:i+3])
                matches = []
                for fname, out_dict in self.loaded_outputs:
                    if trigram in out_dict:
                        matches.append((fname, out_dict[trigram]))
                if matches:
                    self.query_results.append({
                        "ngram": trigram,
                        "type": "trigram",
                        "indices": list(range(i, i+3)),
                        "matches": matches,
                        "found": True
                    })
                    i += 3
                    continue  # Proceed to the next segment
            # If trigram not found, check for bigram
            if i <= len(words) - 2:
                bigram = " ".join(words[i:i+2])
                matches = []
                for fname, out_dict in self.loaded_outputs:
                    if bigram in out_dict:
                        matches.append((fname, out_dict[bigram]))
                if matches:
                    self.query_results.append({
                        "ngram": bigram,
                        "type": "bigram",
                        "indices": [i, i+1],
                        "matches": matches,
                        "found": True
                    })
                    i += 2
                    continue
            # If neither trigram nor bigram is found: record the segment as "NOT FOUND".
            if i <= len(words) - 3:
                trigram = " ".join(words[i:i+3])
                self.query_results.append({
                    "ngram": trigram,
                    "type": "trigram",
                    "indices": list(range(i, i+3)),
                    "matches": [],
                    "found": False
                })
                i += 3
            elif i <= len(words) - 2:
                bigram = " ".join(words[i:i+2])
                self.query_results.append({
                    "ngram": bigram,
                    "type": "bigram",
                    "indices": [i, i+1],
                    "matches": [],
                    "found": False
                })
                i += 2
            else:
                self.query_results.append({
                    "ngram": words[i],
                    "type": "unigram",
                    "indices": [i],
                    "matches": [],
                    "found": False
                })
                i += 1

        # Display results on screen
        for res in self.query_results:
            line = f"{res['ngram']} ({res['type']}): "
            if res["found"]:
                details = []
                for fname, times in res["matches"]:
                    details.append(f"{fname} -> {times}")
                line += "; ".join(details)
            else:
                line += "NOT FOUND"
            line += "\n"
            if not res["found"]:
                self.results_text.insert(tk.END, line, "missing")
            else:
                self.results_text.insert(tk.END, line)

    def save_query_output(self):
        if not self.query_results:
            messagebox.showwarning("Warning", "Please perform a search first.")
            return
        output_str = json.dumps(self.query_results, ensure_ascii=False, indent=4)
        save_path = filedialog.asksaveasfilename(title="Save Query Output", defaultextension=".json",
                                                   filetypes=[("JSON File", "*.json")])
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(output_str)
            messagebox.showinfo("Info", f"Query output saved: {save_path}")
            self.main_app.query_output = self.query_results

# --- Tab 3: Video Cutter ---
class VideoCutterTab(tk.Frame):
    def __init__(self, master, main_app):
        super().__init__(master)
        self.main_app = main_app
        self.video_files = {}  # {base filename (without extension): full path}
        self.output_dir = None
        self.create_widgets()

    def create_widgets(self):
        load_frame = ttk.LabelFrame(self, text="Load Video Files")
        load_frame.pack(fill="x", padx=10, pady=5)
        load_button = ttk.Button(load_frame, text="Load Videos", command=self.load_videos)
        load_button.pack(side="left", padx=5, pady=5)
        self.video_list_label = ttk.Label(load_frame, text="No videos loaded yet.")
        self.video_list_label.pack(side="left", padx=5, pady=5)

        output_frame = ttk.LabelFrame(self, text="Output Folder")
        output_frame.pack(fill="x", padx=10, pady=5)
        output_button = ttk.Button(output_frame, text="Select Output Folder", command=self.select_output_dir)
        output_button.pack(side="left", padx=5, pady=5)
        self.output_dir_label = ttk.Label(output_frame, text="No folder selected yet.")
        self.output_dir_label.pack(side="left", padx=5, pady=5)

        process_button = ttk.Button(self, text="Cut Videos", command=self.start_cutting)
        process_button.pack(pady=10)
        progress_frame = ttk.LabelFrame(self, text="Progress")
        progress_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.log_text = tk.Text(progress_frame, wrap="word", height=15)
        self.log_text.pack(fill="both", padx=10, pady=5, expand=True)

    def load_videos(self):
        file_paths = filedialog.askopenfilenames(title="Select Video Files",
                                                  filetypes=[("MP4 Files", "*.mp4")])
        if not file_paths:
            return
        self.video_files.clear()
        file_names = []
        for path in file_paths:
            base = os.path.splitext(os.path.basename(path))[0]
            self.video_files[base] = path
            file_names.append(os.path.basename(path))
        self.video_list_label.config(text="Loaded videos: " + ", ".join(file_names))

    def select_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Folder")
        if dir_path:
            self.output_dir = dir_path
            self.output_dir_label.config(text=dir_path)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_cutting(self):
        if not self.main_app.query_output:
            messagebox.showwarning("Warning", "Please get the query output from the second tab first.")
            return
        if not self.video_files:
            messagebox.showwarning("Warning", "Please load video files.")
            return
        if not self.output_dir:
            messagebox.showwarning("Warning", "Please select an output folder.")
            return
        threading.Thread(target=self.process_cutting, daemon=True).start()

    def process_cutting(self):
        query_output = self.main_app.query_output
        total_tasks = sum(len(entry["matches"]) for entry in query_output if entry["found"])
        if total_tasks == 0:
            self.log("No match found, no video segment to cut.")
            return
        task_count = 0
        for idx, entry in enumerate(query_output):
            if not entry["found"]:
                continue
            for match in entry["matches"]:
                fname, times = match
                base = os.path.splitext(fname)[0]
                if base not in self.video_files:
                    self.log(f"Video not found: {base}")
                    continue
                video_path = self.video_files[base]
                try:
                    clip = VideoFileClip(video_path)
                except Exception as e:
                    self.log(f"Error loading video: {video_path} - {e}")
                    continue
                for t in times:
                    start_time = t
                    end_time = start_time + 5
                    if end_time > clip.duration:
                        end_time = clip.duration
                    try:
                        subclip = clip.subclip(start_time, end_time)
                        output_filename = f"{base}_{entry['type']}_{idx}_{int(start_time)}.mp4"
                        output_filepath = os.path.join(self.output_dir, output_filename)
                        self.log(f"Cutting {output_filename}...")
                        subclip.write_videofile(output_filepath, codec="libx264", audio_codec="aac",
                                                  verbose=False, logger=None)
                        self.log(f"{output_filename} saved.")
                    except Exception as e:
                        self.log(f"Error: {video_path} {start_time} - {e}")
                    task_count += 1
                    progress = task_count / total_tasks * 100
                    self.progress_bar['value'] = progress
                clip.close()
        self.log("Video cutting process completed.")

# --- Main Application ---
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NGram Dictionary, Query, and Video Cutter")
        self.geometry("800x700")
        self.query_output = None  # Query output from the second tab will be stored here.
        notebook = ttk.Notebook(self)
        self.creator_tab = GramCreatorTab(notebook, self)
        self.query_tab = GramQueryTab(notebook, self)
        self.video_tab = VideoCutterTab(notebook, self)
        notebook.add(self.creator_tab, text="NGram Creator")
        notebook.add(self.query_tab, text="NGram Query")
        notebook.add(self.video_tab, text="Video Cutter")
        notebook.pack(fill="both", expand=True)

if __name__ == '__main__':
    app = MainApp()
    app.mainloop()
