# p01. 강아지 클래스 상속하기 (빈칸 채우기 · 4점)

`Animal` 클래스를 **상속받는** `Puppy` 클래스를 만들고, 물려받은 메서드와 자기 메서드를 차례로 호출하는 프로그램입니다.
빈칸(`____`) 2곳을 채워 프로그램을 완성하세요.

- `Puppy` 는 `Animal` 의 모든 멤버(`legs`, `eat`)를 물려받고, 자기만의 메서드 `bark` 를 가집니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

```python
class Animal:
    legs = 4

    def eat(self):
        print("먹는다")


class Puppy(____):
    def bark(self):
        print("멍멍")


p = Puppy()
p.eat()
p.____()
print(p.legs)
```

## 출력 예

```
먹는다
멍멍
4
```
