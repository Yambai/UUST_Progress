import requests
from bs4 import BeautifulSoup
import fake_useragent
import secrets
import pickle
import re


class MyError(Exception):
    pass


class ISUParser:
    def __init__(self, login, password):
        self.name = "Yambai"
        self.session = requests.Session()
        self.login = login
        self.password = password
        self.headers = {'User-Agent': fake_useragent.UserAgent().random}
        self.cookies = {'PHPSESSID': f'{secrets.randbits(64)}'}
        self.all_marks = None
        self.table_headers = None

    def authorisation(self) -> requests.Session:
        login = self.login
        password = self.password
        cookies = self.cookies
        headers = self.headers
        session = self.session

        form_num_response = session.get('https://isu.uust.ru/login/', cookies=cookies, headers=headers).text
        soup = BeautifulSoup(form_num_response, 'lxml')
        value = soup.find('input')['value']

        data = {'form_num': f'{value}', 'login': f'{login}', 'password': f'{password}'}
        authorisation_request_code = session.post(url='https://isu.uust.ru',
                                                  cookies=cookies,
                                                  headers=headers,
                                                  data=data,
                                                  allow_redirects=False)
        if authorisation_request_code.status_code == 200:
            raise MyError("Авторизация не прошла. Логин или пароль не верный.")
        re_authorisation = session.post(url='https://isu.uust.ru',
                     cookies=cookies,
                     headers=headers,
                     data=data)

        soup = BeautifulSoup(re_authorisation.text, "html.parser")
        name = soup.find('h4', class_='user-name').text.split('\n')[0]
        self.name = ' '.join(name.split(' ')[:2])
        self.session = session
        return self.session

    def exit(self):
        session = self.session
        headers = self.headers
        params = {
            'exit': 'exit',
        }
        session.get('https://isu.uust.ru/', params=params, headers=headers)

    def update_all_marks(self):
        session = self.session
        headers = self.headers

        marks_response = session.post('https://isu.uust.ru/student_points_view/', headers=headers).text
        soup = BeautifulSoup(marks_response, 'lxml')

        # нахождение таблицы по id
        table = soup.find('table', {'id': 'basic-datatable'})

        # извлечение заголовков таблицы
        headers = [header.text for header in table.find_all('th')]
        self.table_headers = headers

        # извлечение строк таблицы
        rows = table.find_all('tr')

        table_data = []
        for row in rows:
            cols = row.find_all('td')
            cols = [f'{col}'.strip().replace("\n", '').replace("\t", "").replace("\r", "").replace("<td>", "").replace(
                "</td>", "") for col in cols]
            new_cols = []
            for text in cols:
                if "<i" in text:
                    if "text" not in text:
                        new_cols.append("---")
                        continue
                    if re.compile(r'<i.*?>(.*?)<\/i>').findall(text)[0] == "":
                        if "title" not in text:
                            new_cols.append("---")
                            continue
                        else:
                            match = re.search(r'title="(.*?)"', text)
                            result = match.group(1)
                            new_cols.append(result)
                            continue
                    else:
                        pattern = re.compile(r'<i.*?>(.*?)<\/i>')
                        matches = pattern.findall(text)
                        result = matches[0]
                        new_cols.append(result)


                pattern = re.compile(r'<span.*?>(.*?)<\/span>')
                matches = pattern.findall(text)
                result = matches[0] if matches else 'No matches'
                if result == 'No matches':
                    new_cols.append(text)
                else:
                    new_cols.append(result)

            #print(new_cols)
            table_data.append(new_cols)
        semester_count = 0
        # Считаем количество семестров
        for i in table_data[1:]:
            if not i:
                semester_count += 1

        marks = [[] for _ in range(semester_count)]
        semester_num = -1
        for data_row in table_data[1:]:

            if not data_row:
                semester_num += 1
            elif data_row[0][0] == 'Б':
                marks[semester_num].append(data_row)
        self.all_marks = marks
        return self.all_marks

    def get_semester_marks(self, semester_num: int) -> list:
        all_semester_marks = self.update_all_marks()
        if 1 <= semester_num <= len(all_semester_marks):
            return all_semester_marks[semester_num - 1]
        raise MyError("Указанное количество семестров не соответствует действительности")

    def session_dump(self, path):

        with open(path, "wb") as file:
            pickle.dump(self.session, file)

    def session_load(self, path):
        with open(path, "rb") as file:
            session = pickle.load(file)
        self.session = session
