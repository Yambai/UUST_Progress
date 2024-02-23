from PIL import Image, ImageDraw, ImageFont
import os
from isu_parser import ISUParser

class MarksPainter:
    def __init__(self,
                 user: ISUParser):

        self.save_path = "mark_images"
        self.img = None
        self.name = user.name
        self.all_marks = user.all_marks
        self.semester = 1
        self.width = 1920
        self.height = 1080
        self.rounded_rectangle_size = ((50.0, 200.0), (1870.0, 1030.0))
        self.rounded_rectangle_radius = 20
        self.rounded_rectangle_color = (255, 255, 255)
        self.highlighter_color = (200, 200, 200)
        self.gradient_color_1 = (2, 0, 36)
        self.gradient_color_2 = (175, 0, 255)
        self.bad_color = (255, 0, 0)
        self.headers_x = 1500
        self.headers_y = 230
        self.subject_x = 200
        self.subject_x_marks = 1500
        self.subject_y = 280
        self.x_plus = 130
        self.y_plus = 50
        self.font_path = 'fonts/regular.ttf'
        self.font1 = ImageFont.truetype(self.font_path, size=100)
        self.font2 = ImageFont.truetype(self.font_path, size=70)
        self.font3 = ImageFont.truetype(self.font_path, size=30)
        self.font4 = ImageFont.truetype(self.font_path, size=40)
        self.headers = [
            'Дисциплина',
            'Экзамен',
            'Зачет',
            'Диф.Зачет'
        ]

    def gradient(self) -> Image:
        canvas_size = (self.width, self.height)
        color1 = self.gradient_color_1
        color2 = self.gradient_color_2
        base = Image.new('RGB', canvas_size, color1)
        top = Image.new('RGB', canvas_size, color2)
        mask = Image.new('L', canvas_size)
        mask_data = []
        for y in range(canvas_size[1]):
            mask_data.extend(int(255 * (1 - y / canvas_size[1])) for _ in range(canvas_size[0]))
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base

    def draw_background(self) -> ImageDraw:
        self.img: Image = self.gradient()
        rounded_rectangle_size = self.rounded_rectangle_size
        rounded_rectangle_color = self.rounded_rectangle_color
        rounded_rectangle_radius = self.rounded_rectangle_radius
        draw = ImageDraw.Draw(self.img)
        draw.rounded_rectangle(xy=rounded_rectangle_size, fill=rounded_rectangle_color, radius=rounded_rectangle_radius)
        return draw

    def draw_headers(self):
        headers = self.headers
        draw = self.draw_background()
        draw.text((50, 50), self.name, fill=(255, 255, 255), font=self.font1)
        draw.text((1920 - 300, 50), f"{self.semester} семестр", fill=(255, 255, 255), font=self.font2)
        x = self.headers_x
        y = self.headers_y
        x_plus = self.x_plus
        draw.text((200, 230), headers[0], fill=(0, 0, 0), font=self.font4, anchor="mm")
        for text in headers[1:]:
            draw.text((x, y), text, fill=(0, 0, 0), font=self.font4, anchor="mm")
            x += x_plus
        return draw

    def draw_subjects(self) -> Image:
        draw = self.draw_headers()
        semester = self.semester
        all_marks = self.all_marks
        y = self.subject_y
        y_plus = self.y_plus
        for subject in all_marks[semester - 1]:
            x = self.subject_x
            draw.rounded_rectangle([(x - 125, y - 20), ((1920 + 125 - x), y + 20)], fill=(200, 200, 200), radius=20)
            draw.text((100, y), f"• {subject[1]}", fill=(0, 0, 0), font=self.font3, anchor="lm")
            texts = [subject[7],
                     subject[8],
                     subject[10]]
            x = self.subject_x_marks
            for mark in texts:
                if mark in ["Не зачет", "Неявка", "1", "2"]:
                    fill = (255, 0, 0)
                else:
                    fill = (0, 0, 0)

                draw.text((x, y), mark, fill=fill, font=self.font3, anchor="mm")
                x += self.x_plus
            y += y_plus
        return self.img

    def draw_img(self):
        img = self.draw_subjects()
        return img

    def save_img(self, semester: int, folder: str = "mark_images"):
        if not (1 <= semester <= len(self.all_marks)):
            return None
        self.save_path = folder
        self.semester = semester
        img: Image = self.draw_img()
        os.makedirs(self.save_path, exist_ok=True)
        path = f'{self.save_path}/{semester}_semester.png'
        img.save(path)
        return path

