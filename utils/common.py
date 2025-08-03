import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_absolute_path(sub_path: str) -> str:
    """
    Resolves the absolute path of a subdirectory relative to the project root.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, sub_path)

def delete_files_in_dir(dir_path: str, prefix: str = "", extension: str = ""):
    """
    Deletes files in the given directory matching the prefix and extension.
    """
    resolved_path = get_absolute_path(dir_path)

    if not os.path.exists(resolved_path):
        logging.warning(f"Directory does not exist: {resolved_path}")
        return

    deleted = False
    for file in os.listdir(resolved_path):
        if file.startswith(prefix) and file.endswith(extension):
            file_path = os.path.join(resolved_path, file)
            try:
                os.remove(file_path)
                logging.info(f"Deleted file: {file_path}")
                deleted = True
            except Exception as e:
                logging.error(f"Failed to delete {file_path}: {e}")

    if not deleted:
        logging.info(f"No matching files to delete in: {resolved_path}")

def delete_transcripts():
    delete_files_in_dir("data/transcripts", prefix="transcript_", extension=".txt")

def delete_audio_files():
    delete_files_in_dir("data/audio", prefix="", extension=".mp3")

def delete_pdf_responses():
    delete_files_in_dir("responses/pdf", prefix="", extension=".pdf")

if __name__ == "__main__":
    delete_transcripts()
    delete_audio_files()
    delete_pdf_responses()
