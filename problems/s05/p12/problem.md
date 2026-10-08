# p12. for 를 while 로 바꾸기 (빈칸 채우기 · 6점)

아래 프로그램은 세 정수 `start`, `end`, `step` 을 입력받아 `start` 부터 `end` 까지(끝 포함) `step` 씩 커지는 수를
한 줄에 하나씩 출력합니다.

```python
start = int(input())
end = int(input())
step = int(input())
for num in range(start, end + 1, step):
    print(num)
```

이 프로그램의 `for` 문을 `while` 문으로 바꿔 쓴 것이 아래 시작 코드입니다. 어떤 입력에도 위 프로그램과 같은 출력이 나오도록
빈칸(`____`) 세 곳을 채워 프로그램을 완성하세요.

- 빈칸만 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 시작 코드

```python
start = int(input())
end = int(input())
step = int(input())
num = ____
while ____:
    print(num)
    ____
```

## 제한 사항
- 1 ≤ start ≤ end ≤ 100
- 1 ≤ step ≤ 10

## 입출력 예

입력

```
2
11
3
```

출력

```
2
5
8
11
```

입력

```
1
10
4
```

출력

```
1
5
9
```
