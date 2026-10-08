n = int(input())

steps_list = []
total_steps = 0

for _ in range(n):
    step = int(input())
    steps_list.append(step)
    total_steps += step
    
with open("steps.txt", "w", encoding="utf-8") as f:
    for i in range(n):
        f.write(f"{i+1}일차 {steps_list[i]}\n")
    f.write(f"합계 {total_steps}\n")
    
    
with open("steps.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content, end="")
