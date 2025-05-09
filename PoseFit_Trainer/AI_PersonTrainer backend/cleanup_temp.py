import os
import sys
import time
import shutil
from datetime import datetime

def clean_temp_videos():
    print("Starting cleanup of temp_videos directory...")
    
    # Get the path to the temp_videos directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(current_dir, "temp_videos")
    
    if not os.path.exists(temp_dir):
        print(f"Temp directory does not exist: {temp_dir}")
        return False
        
    print(f"Cleaning directory: {temp_dir}")
    
    # Try to remove all files in the directory
    try:
        files_removed = 0
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    # Try to delete the file - ignore files that can't be deleted
                    try:
                        print(f"Attempting to delete: {filename}")
                        os.remove(file_path)
                        files_removed += 1
                        print(f"Successfully deleted: {filename}")
                    except Exception as e:
                        print(f"Error deleting {filename}: {e}")
                        
                        # If removing fails, try with file unlinking
                        try:
                            print(f"Trying alternative method to delete {filename}")
                            # Make sure file isn't read-only
                            os.chmod(file_path, 0o777)
                            # Force close any open handles
                            os.unlink(file_path)
                            files_removed += 1
                            print(f"Successfully deleted {filename} with unlink")
                        except Exception as unlink_err:
                            print(f"Unlink also failed: {unlink_err}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                
        print(f"Cleanup complete. Removed {files_removed} files.")
        
        # Create marker to show cleanup was performed
        try:
            marker_path = os.path.join(temp_dir, f"manual_cleanup_{int(time.time())}.txt")
            with open(marker_path, "w") as f:
                f.write(f"Manual cleanup performed at {datetime.now().isoformat()}")
            print(f"Created cleanup marker: {marker_path}")
        except Exception as marker_err:
            print(f"Error creating cleanup marker: {marker_err}")
            
        return True
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return False

if __name__ == "__main__":
    print("=== TEMP VIDEOS CLEANUP UTILITY ===")
    clean_temp_videos()
    print("Press Enter to exit...")
    input() 