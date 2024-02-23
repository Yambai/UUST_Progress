from isu_parser import ISUParser
from Painter import MarksPainter


def main():
    user = ISUParser(login="username@mail.com", password="password")
    # Авторизуемся
    user.authorisation()
    # Явно получаем в первый раз все оценки
    user.update_all_marks()
    # Создаем объект для сохранения оценок в виде красивых картинок
    user_painter = MarksPainter(user)
    # Выходим из аккаунта
    user.exit()
    k = 1
    while k:
        # Указываем нужный вам семестр
        i = int(input("Enter a semester number: "))
        # Если введете 0,то программа закончит выполнение
        if i == 0:
            k = 0
        # Сохраняет картинку и возвращает путь к нему
        print(user_painter.save_img(semester=i))


if __name__ == "__main__":
    main()
