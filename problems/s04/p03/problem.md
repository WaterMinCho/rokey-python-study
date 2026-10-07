# p03. 로봇 정보 딕셔너리 (빈칸 채우기 · 4점)

로봇 정보를 담은 딕셔너리 `robot` 을 고쳐서 출력하는 프로그램입니다. 빈칸(`____`)을 채워 프로그램을 완성하세요.

1. 색 이름을 한 줄 입력받아 `robot` 에 `"color"` 라는 키로 추가합니다.
2. `"battery"` 키의 값을 `100` 으로 바꿉니다.
3. 딕셔너리 전체를 출력한 뒤 `"color"` 키의 값을 꺼내 출력합니다.

빈칸만 채우세요. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 시작 코드

```python
robot = {"name": "ROKEY", "battery": 80}
color = input()
robot[____] = color
robot[____] = 100
print(robot)
print(robot.____("color"))
```

## 입출력 예

입력

```
blue
```

출력

```
{'name': 'ROKEY', 'battery': 100, 'color': 'blue'}
blue
```
