import time
import functools

def create_debugger(name):
    def debugger(*args, **kwargs):
        print(f"[{name}]", *args, **kwargs)
    
    def monitor_performance(operation_name):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                print(f"[{name}] {operation_name} took {duration:.2f} seconds")
                return result
            return wrapper
        return decorator
    
    debugger.monitor_performance = monitor_performance
    return debugger

debugger = create_debugger("DEBUG")
