import sys
import traceback

class CustomException(Exception):
    def __init__(self, message: str, original_exception: Exception = None):
        """
        Args:
            message: Human-readable error description
            original_exception: The original exception that was caught
        """
        self.message = message
        self.original_exception = original_exception
        
        if original_exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            if exc_tb:
                tb_frame = traceback.extract_tb(exc_tb)[-1]
                self.file_name = tb_frame.filename
                self.line_number = tb_frame.lineno
                self.function_name = tb_frame.name
            else:
                self.file_name = "Unknown"
                self.line_number = "Unknown"
                self.function_name = "Unknown"
        else:
            self.file_name = "Unknown"
            self.line_number = "Unknown"
            self.function_name = "Unknown"
        
        detailed_message = self._build_error_message()
        
        super().__init__(detailed_message)
        if original_exception:
            self.__cause__ = original_exception
    
    def _build_error_message(self) -> str:
        """Constructs detailed error message."""
        parts = [
            f"Error: {self.message}",
            f"File: {self.file_name}",
            f"Line: {self.line_number}",
            f"Function: {self.function_name}"
        ]
        
        if self.original_exception:
            parts.append(f"Original Error: {str(self.original_exception)}")
        
        return " | ".join(parts)
    
    def __str__(self):
        return self._build_error_message()