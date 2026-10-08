def in_range(value, low, high):
    return ____

def count_ok(values, low, high):
    count = 0
    for v in values:
        if in_range(v, low, high):
            count += 1
    ____ count

weights = [98, 105, 110, 95, 94, 100]
low = int(input())
high = int(input())
print("합격:", ____, "개")
