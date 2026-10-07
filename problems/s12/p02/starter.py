f = open("log.txt", "w")
f.write("start\n")
f.close()

f = open("log.txt", ____)
for i in range(1, 4):
    f.write("%d번 작업 완료\n" % ____)
f.____()

f = open("log.txt", "r")
print(f.read(), end="")
f.close()
