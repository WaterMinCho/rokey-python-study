# p01. 메뉴 이터레이터 (빈칸 채우기 · 4점)

메뉴 리스트를 이터레이터로 바꾼 뒤 자료형을 출력하고, 첫 메뉴는 직접 하나 꺼내고 나머지는 for 문으로 출력하는 프로그램입니다.
빈칸(`____`) 2곳을 채워 프로그램을 완성하세요.

```python
menu = ["bibimbap", "ramen", "gimbap", "sushi"]
it = ____(menu)
print(type(it))
print("first:", ____(it))
for food in it:
    print("next:", food)
```

- 첫 번째 빈칸: 리스트(이터러블)를 이터레이터로 바꾸는 내장 함수
- 두 번째 빈칸: 이터레이터에서 값을 하나 꺼내는 내장 함수
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 출력 예

```
<class 'list_iterator'>
first: bibimbap
next: ramen
next: gimbap
next: sushi
```
