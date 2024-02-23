from isu_parser import ISUParser
from Painter import MarksPainter

user = ISUParser(login="username@mail.com", password="password")
user.authorisation()
all_marks = user.get_all_marks()


user_painter = MarksPainter(user)
user.exit()
k=1
while k:
    i = int(input("Enter a semester number: "))
    if i == 0:
        k = 0
    print(user_painter.save_img(semester=i))
