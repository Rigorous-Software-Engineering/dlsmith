from dlsmith.utils.file_operations import create_file
import os

class Logging(object):
    def __init__(self):
        self.log_file_path = None
        self.log_file_name = "logging.txt"
        self.log_text = "\n XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        self.log_text += "\n XXXXXXXXXXXXXXX    LOGS     XXXXXXXXXXXXXXX"
        self.log_text += "\n XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

    def set_log_file_path(self, path):
        self.log_file_path = path
    
    def set_log_file_name(self, name): 
        self.log_file_name = name
    
    def add_log_text(self, text): 
        self.log_text += "\n" + text

    def dump_log_file(self):
        create_file(self.log_text, os.path.join(self.log_file_path, self.log_file_name))
        
    def refresh_log_text(self):
        self.log_text = ""

    def get_log_file_path(self):
        return os.path.join(self.log_file_path, self.log_file_name)

