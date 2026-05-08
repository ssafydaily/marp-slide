import time 

def count():
    print('One')
    time.sleep(1)
    print('Two')
    time.sleep(1)

def main():
    for _ in range(3):
        count()


start = time.perf_counter()
main()
elapsed = time.perf_counter() - start
print(f'{__file__} 실행 시간 {elapsed:0.2f} 초.')
