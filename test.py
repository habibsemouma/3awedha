import os
import subprocess
import win32print

printer= win32print.GetDefaultPrinter().split(',')[0]
print("ssssssssssss",printer)
def print_pdf_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path) and file_path.lower().endswith('.pdf'):
            print("ddddddddddddddddd",file_path)
            subprocess.run(["lpr", "-P", printer, file_path], check=True)
            print(f"File '{file_path}' sent to printer.")
        else:
            print(f"File '{file_path}' is either invalid or not a PDF.")

# Example usage
file_paths = ["C:\\Users\\User\\Documents\\testing.pdf"]
print_pdf_files(file_paths)
