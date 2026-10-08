# p02. 재생 목록 클래스 (빈칸 채우기 · 4점)

노래 제목을 모으는 `Playlist` 클래스입니다. 객체를 만들 때 받은 이름을 인스턴스 변수 `title` 에 저장하고 빈 리스트 `songs` 를 만듭니다. `add()` 는 노래 제목을 `songs` 맨 뒤에 추가하고, `count()` 는 담긴 노래 수를 반환합니다. 빈칸(`____`) 3곳을 채워 클래스를 완성하세요.

```python
class Playlist:
    def ____(self, title):
        self.title = title
        self.songs = []

    def add(self, song):
        ____.append(song)

    def count(self):
        return ____(self.songs)
```

- 첫 번째 빈칸은 객체를 만들 때 자동으로 호출되는 메서드의 이름입니다.
- 객체마다 `songs` 는 따로 관리됩니다.
- 클래스만 완성하면 됩니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 테스트 코드와 출력 예

```python
p = Playlist("출근길")
p.add("봄날")
p.add("밤편지")
print(p.title, p.count())
print(p.songs)
```

```
출근길 2
['봄날', '밤편지']
```

```python
a = Playlist("A")
b = Playlist("B")
a.add("x")
print(a.count(), b.count())
```

```
1 0
```
