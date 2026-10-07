def check_age(age):
    if age < 0:
        ____ ValueError("나이는 0 이상이어야 합니다")
    return age

try:
    age = int(input())
    print("나이:", check_age(age))
except ____ as e:
    print("오류:", ____)
