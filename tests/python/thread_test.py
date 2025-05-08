import threading
import time


def task(name):
    print(f"{name} start")
    count = 0
    for i in range(0, 7):
        count += i
    print(f"{name} end")
    return count


def thread_demo():
    start_time = time.time()
    threads = []

    for i in range(4):
        t = threading.Thread(target=task, args=(f"Thread-{i}",))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()
    print(f"Threading execution time: {end_time - start_time:.4f} seconds!")


"""
Thread-1 startThread-2 start
Thread-2 end

Thread-1 end
Thread-0 start
Thread-0 end
Thread-3 start
Thread-3 end
"""
thread_demo()
print("Thread test successfully!")
