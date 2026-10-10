def solution(total, size):
    boxes = total // size
    rest = total % size 
    return boxes, rest
