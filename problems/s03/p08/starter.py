year = int(input())
if (year % 4 == 0 ____ year % 100 ____ 0) ____ year % 400 == 0:
    print(year, "윤년")
else:
    print(year, "평년")
