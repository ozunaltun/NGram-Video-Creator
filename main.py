# NGram Dictionary, Query, and Video Cutter 🎬📚

## Overview
NGram Dictionary, Query, and Video Cutter is a multi-functional Python application that combines subtitle processing with video editing. With its user-friendly GUI built with Tkinter, this tool lets you:

- 🔤 **Generate ngrams:** Create bigrams and trigrams from SRT subtitle files.
- 🔍 **Query ngrams:** Search and query these ngrams using a custom sentence input.
- ✂️ **Cut videos:** Automatically extract video segments based on query results.

This project is perfect for analyzing subtitle files and automatically extracting relevant clips from MP4 videos.

---

## Features

### 🔤 NGram Creator
- **Multiple File Processing:** Process several SRT files to generate ngram dictionaries.
- **Output Formats:** Supports both JSON and plain text outputs.
- **Auto Output Folder:** Automatically creates an output folder to store results.

### 🔍 NGram Query
- **Custom Sentence Search:** Search for specific ngrams using your own sentence.
- **Greedy Segmentation:** Utilizes a greedy segmentation approach (trigrams then bigrams) to avoid overlaps.
- **Visual Feedback:** Displays search results with clear visual cues.

### ✂️ Video Cutter
- **Video Loading:** Supports loading MP4 video files.
- **Timestamp-Based Cutting:** Cuts video segments based on subtitle timestamps.
- **User-Specified Output:** Saves video clips to a directory of your choice.
- **Fixed Duration:** Typically cuts 5-second segments (or shorter if near the video’s end).

### 💻 User-Friendly GUI
- **Intuitive Design:** Built with Tkinter featuring clear tabs for each functionality.
- **Real-Time Logging:** Provides live logs and progress indicators for all operations.

---

## Installation

### Prerequisites
- **Python 3.6+**
- **Tkinter** (usually included with Python installations)
- **MoviePy** (for video processing)

### Installing Dependencies
It's recommended to use a virtual environment. Run the following commands to set up your environment and install the necessary packages:

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv

# On Unix or MacOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install MoviePy
pip install moviepy
