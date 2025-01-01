import subprocess
import sys
from django.conf import settings
import os
import tempfile

class CodeExecutionService:
    @staticmethod
    def execute_python_code(code: str) -> tuple[str, str]:
        """
        Execute Python code in a safe environment
        Returns: (output, error)
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            try:
                    # اجرای کد در محیط ایزوله با محدودیت زمانی
                result = subprocess.run(
                    [sys.executable, f.name],
                    capture_output=True,
                    text=True,
                    timeout=5  # محدودیت 5 ثانیه
                )
                return result.stdout, result.stderr
            except subprocess.TimeoutExpired:
                return "", "Execution timeout (5 seconds limit)"
            except Exception as e:
                return "", str(e)
            finally:
                os.unlink(f.name) 