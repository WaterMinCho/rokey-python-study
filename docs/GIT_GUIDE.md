# Git 흐름 가이드

이 스터디는 문제 풀이를 **브랜치 → 커밋 → 푸시 → PR → 리뷰 → 머지** 흐름으로 제출합니다.
회사에서 쓰는 방식과 같으니, 문제를 풀면서 git 도 같이 익힙니다.

## 0. 처음 한 번

1. 스터디장이 보낸 초대(collaborator)를 수락합니다. (GitHub 알림 또는 메일)
2. 저장소를 내 컴퓨터로 가져옵니다.

```bash
git clone https://github.com/<스터디장ID>/rokey-python-study.git
cd rokey-python-study
python study.py init <내 깃허브 ID>
```

> `python` 이 안 되면 `python3` 로 실행하세요.

## 1. 매일 하는 흐름

```bash
# ① 최신 상태 받기 (새 문제·다른 사람 풀이가 main 에 들어와 있습니다)
git switch main
git pull

# ② 오늘 풀 차시용 브랜치 만들기  (이름 규칙: <내ID>/<세트>)
git switch -c minsu/s03

# ③ 문제 받기 → 풀기 → 채점
python study.py start 3
python study.py grade 3

# ④ 내 풀이를 커밋하고 올리기
git add submissions/minsu/s03
git commit -m "s03 풀이"
git push -u origin minsu/s03
```

⑤ GitHub 저장소 페이지에 뜨는 **Compare & pull request** 버튼으로 PR 을 만듭니다.

⑥ 잠시 뒤 Actions 가 자동 채점해 PR 에 **점수 코멘트**를 답니다.

⑦ 스터디 시간에 서로의 PR 을 보며 틀린 문제를 설명해 줍니다(리뷰 코멘트).

⑧ 리뷰가 끝나면 **Squash and merge** → 브랜치 삭제. 다음 날 ①부터 반복합니다.

### 채점 후 다시 고쳤다면

같은 브랜치에서 고치고 다시 커밋·푸시하면 PR 이 자동으로 갱신되고 재채점됩니다.

```bash
git add submissions/minsu/s03
git commit -m "s03 p04 수정"
git push
```

## 2. 규칙 (CI 가 검사합니다)

- 내 폴더 `submissions/<내 ID>/` 안의 파일만 고칩니다.
- `problems/`, `study.py` 등 다른 파일은 건드리지 않습니다. (문제에 오류가 있으면 이슈로 알려 주세요)
- PR 하나에는 한 사람의 풀이만 담습니다.
- 아직 풀지 않은 차시의 다른 사람 풀이는 열어 보지 않습니다.

## 3. 자주 쓰는 명령

| 하고 싶은 것 | 명령 |
|---|---|
| 지금 상태 보기 (가장 자주 씀) | `git status` |
| 무엇을 고쳤는지 보기 | `git diff` |
| 커밋 기록 보기 | `git log --oneline` |
| 지금 브랜치 확인 | `git branch` |
| 파일 수정 취소(커밋 전) | `git restore <파일>` |
| `git add` 취소 | `git restore --staged <파일>` |

## 4. 자주 겪는 상황

**실수로 main 에서 풀고 커밋까지 했어요**

```bash
git switch -c minsu/s03      # 지금 상태 그대로 새 브랜치를 만들면 커밋이 따라옵니다
git push -u origin minsu/s03
git switch main
git reset --hard origin/main # main 을 원격과 같게 되돌림 (방금 커밋은 새 브랜치에 안전하게 있음)
```

**실수로 문제 파일(problems/)을 고쳤어요**

```bash
git restore problems/        # 커밋 전이라면 이것으로 원상 복구
```

**push 가 거부(rejected)됐어요**

원격에 내가 모르는 커밋이 있다는 뜻입니다. 같은 브랜치를 먼저 받아 온 뒤 다시 올립니다.

```bash
git pull --rebase
git push
```

**PR 에 "This branch has conflicts" 가 떠요**

사람마다 폴더가 달라 거의 생기지 않습니다. 생겼다면 main 을 내 브랜치에 합칩니다.

```bash
git switch minsu/s03
git pull origin main
# 충돌 표시(<<<<<<<)가 난 파일을 고친 뒤
git add .
git commit
git push
```

## 5. 초대받지 않은 사람이 참여하려면 (Fork 방식)

저장소를 **Fork** → 내 포크를 clone → 같은 방법으로 브랜치·커밋·푸시 → 원본 저장소로 PR.
이 경우 점수는 PR 코멘트 대신 PR 의 **Checks → 채점 → Summary** 에서 확인합니다.
