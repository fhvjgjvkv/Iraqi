import random
import datetime
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore

import arabic_reshaper
from bidi.algorithm import get_display

def fix_arabic(text):
    if not text: return ""
    return get_display(arabic_reshaper.reshape(text))

class IraqiAdviceApp(App):
    def build(self):
        # مخزن محلي لحفظ حكمك الخاصة على الهاتف
        self.store = JsonStore('my_custom_quotes.json')
        if not self.store.exists('quotes_list'):
            self.store.put('quotes_list', data=[])

        self.كل_النصائح = []
        self.المعروضة_مسبقا = set()

        # الواجهة الرئيسية (ثيم فخم داكن افتراضي)
        self.layout = BoxLayout(orientation='vertical', padding=25, spacing=20)
        
        # 1. شاشة عرض النصيحة
        self.label = Label(
            text=fix_arabic("جاري جلب نصيحة عراقية فخمة..."), 
            font_size='22sp', halign='center', valign='middle'
        )
        self.label.bind(size=self.label.setter('text_size'))
        self.layout.add_widget(self.label)

        # 2. خانة إضافة حكمة شخصية
        self.input_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.25), spacing=10)
        self.input_field = TextInput(
            hint_text=fix_arabic("اكتب حكمتك الخاصة هنا ليتم حفظها..."),
            font_size='16sp', halign='right', multiline=False,
            background_color=(0.15, 0.15, 0.15, 1), foreground_color=(1, 1, 1, 1)
        )
        self.save_btn = Button(text=fix_arabic("إضافة حكمتي لدفتر الذكريات"), size_hint=(1, 0.4), font_size='16sp')
        self.save_btn.bind(on_press=self.حفظ_حكمة_المستخدم)
        self.input_layout.add_widget(self.input_field)
        self.input_layout.add_widget(self.save_btn)
        self.layout.add_widget(self.input_layout)

        # 3. زر التحديث اليدوي
        self.next_btn = Button(text=fix_arabic("نصيحة عراقية أخرى"), size_hint=(1, 0.15), font_size='18sp')
        self.next_btn.bind(on_press=self.تغيير_يدوي)
        self.layout.add_widget(self.next_btn)

        # جلب البيانات وتطبيق الثيم اليومي
        self.جلب_النصائح_العراقية()
        self.تحديث_المظهر_اليومي()
        
        # التحديث التلقائي للمظهر والنصيحة كل 5 ساعات (18000 ثانية)
        Clock.schedule_interval(self.تحديث_المظهر_اليومي, 18000)

        return self.layout

    def تحديث_المظهر_اليومي(self, *args):
        today = datetime.datetime.now()
        seed_value = today.year + today.month + today.day
        random.seed(seed_value)

        # توليد ألوان داكنة فخمة تتغير يومياً
        bg_r, bg_g, bg_b = random.uniform(0.05, 0.12), random.uniform(0.05, 0.12), random.uniform(0.08, 0.15)
        btn_r, btn_g, btn_b = random.uniform(0.6, 0.85), random.uniform(0.5, 0.75), random.uniform(0.2, 0.4)

        self.layout.canvas.before.clear()
        with self.layout.canvas.before:
            Color(bg_r, bg_g, bg_b, 1)
            self.rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos, radius=[10])
        self.layout.bind(size=self._update_canvas, pos=self._update_canvas)

        self.next_btn.background_normal = ''
        self.next_btn.background_color = [btn_r, btn_g, btn_b, 1]
        self.next_btn.color = [0, 0, 0, 1]

        self.save_btn.background_normal = ''
        self.save_btn.background_color = [btn_r * 0.7, btn_g * 0.7, btn_b * 0.7, 1]
        self.save_btn.color = [1, 1, 1, 1]

        random.seed()
        self.عرض_نصيحة_جديدة()

    def _update_canvas(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def جلب_النصائح_العراقية(self):
        url = "https://raw.githubusercontent.com/aminsb/iraqi-quotes/main/quotes.txt"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                self.كل_النصائح = [line.strip() for line in res.text.split('\n') if line.strip()]
        except:
            pass
        
        user_quotes = self.store.get('quotes_list')['data']
        if user_quotes:
            for q in user_quotes:
                if q not in self.كل_النصائح:
                    self.كل_النصائح.append(q)
        
        if not self.كل_النصائح:
            self.كل_النصائح = ["امشي شهر ولا تعبر نهر.. ادرس خطوتك زين."]

    def عرض_نصيحة_جديدة(self):
        if not self.كل_النصائح: return

        # تم استبدال الاسم بمتغير إنجليزي لمنع أي خطأ في الحروف العربية داخل الكود
        available_quotes = [q for q in self.كل_النصائح if q not in self.المعروضة_مسبقا]
        if not available_quotes:
            self.المعروضة_مسبقا.clear()
            available_quotes = self.كل_النصائح

        انتخاب = random.choice(available_quotes)
        self.المعروضة_مسبقا.add(انتخاب)
        self.label.text = fix_arabic(انتخاب)

    def حفظ_حكمة_المستخدم(self, instance):
        text = self.input_field.text.strip()
        if text:
            current_data = self.store.get('quotes_list')['data']
            
            if text in current_data or text in self.كل_النصائح:
                self.label.text = fix_arabic("هذه الحكمة موجودة مسبقاً في تطبيقك!")
                self.input_field.text = ""
                return

            current_data.append(text)
            self.store.put('quotes_list', data=current_data)
            self.كل_النصائح.append(text)
            self.input_field.text = ""
            self.label.text = fix_arabic(f"تم حفظ حكمتك بنجاح: \n\"{text}\"")

    def تغيير_يدوي(self, instance):
        self.next_btn.background_color = [random.random(), random.random(), random.random(), 1]
        self.عرض_نصيحة_جديدة()

if __name__ == "__main__":
    IraqiAdviceApp().run()
