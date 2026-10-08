# 여기에 코드를 작성하세요
menu = input()
price = int(input())
count = int(input())


total = price * count
new_order = f"- {menu} ({price}원) x {count} {total}원\n"

with open("order.txt", "a", encoding="utf-8") as f:
    f.write(new_order)
    
with open("order.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content, end="")
