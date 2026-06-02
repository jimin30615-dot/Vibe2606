# 파이썬 연습.py

# 숫자와 글자를 담는 상자를 만들어요.
# x라는 상자에는 100을 넣고, y라는 상자에는 200을 넣어요.
# strA라는 상자에는 글자 "문자열을 저장"을 넣어요.
x = 100
y = 200
strA = "문자열을 저장"

# dir()는 지금 이 코드에 어떤 이름들이 있는지 보여줘요.
# len()는 글자의 길이를 세어줘요.
print(dir())
print(len(strA))

# times라는 이름의 함수를 만들어요.
# 이 함수는 두 숫자를 받아서 서로 곱해주는 역할을 해요.
def times(a, b):
    return a * b

# times 함수에 3과 4를 넣어서 계산한 결과를 result라는 상자에 저장해요.
result = times(3, 4)
print(result)

# Person이라는 새로운 종류의 장난감을 만들어요.
# 이 장난감은 id와 name이라는 두 가지 정보를 가지고 있어요.
class Person:
    # __init__는 장난감을 처음 만들 때 불러오는 마법이에요.
    # id와 name 정보를 받아서 장난감에 붙여줘요.
    def __init__(self, id, name):
        self.id = id
        self.name = name

    # printinfo는 이 장난감이 자신의 이름과 번호를 말하게 해요.
    def printinfo(self):
        print(f"ID: {self.id}, Name: {self.name}")


# Person 장난감을 두 개 만들어요.
person1 = Person(1, "Alice")
person2 = Person(2, "Bob")

# person1 장난감에게 자기 정보를 말하게 해요.
person1.printinfo()



