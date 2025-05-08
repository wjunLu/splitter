from multiprocessing import Process, Queue
import time


def producer(queue_test):
    for i in range(5):
        time.sleep(1)
        queue_test.put(f"data {i}")
        print(f"produce: data {i}")

    # 生产完数据后，放入一个结束信号告诉消费者
    queue_test.put(None)


def consumer(queue_test):
    while True:
        item = queue_test.get()
        if item is None:
            break
        print(f"consume: {item}")


"""
produce: data 0
consume: data 0
produce: data 1
consume: data 1
produce: data 2
consume: data 2
produce: data 3
consume: data 3
produce: data 4
consume: data 4
"""
queue_test = Queue()
p1 = Process(target=producer, args=(queue_test,))
p2 = Process(target=consumer, args=(queue_test,))

p1.start()
p2.start()

p1.join()
p2.join()

print("Queue test successfully!")
