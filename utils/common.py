import os

def delete_transcripts():
    transcript_dir = "data/transcripts"
    if os.path.exists(transcript_dir):
        for file in os.listdir(transcript_dir):
            if file.startswith("transcript_") and file.endswith(".txt"):
                transcript_path = os.path.join(transcript_dir, file)
                os.remove(transcript_path)
                print(f"Deleted transcript file: {transcript_path}")

if __name__ == "__main__":
    delete_transcripts()