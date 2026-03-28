import flet as ft
from math import log

class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()

        self.process = ft.Text(value="", color="#ffffff", size=70, text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD)
        self.result = ft.Text(value="0", color="#ffffff", size=70, text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD)

        self.width = 380
        self.bgcolor = "#000000"  # 纯黑背景
        self.border_radius = ft.border_radius.all(35)
        self.padding = 20
        self.shadow = None

        self.content = ft.Column(
            controls=[
                # 显示屏幕区域
                ft.Container(
                    content=ft.Column(
                        controls=[self.process, self.result],
                        alignment=ft.MainAxisAlignment.END,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        tight=True,
                        spacing=0,
                    ),
                    alignment=ft.Alignment(1, 1),
                    padding=ft.Padding(right=15, bottom=20, top=60, left=15),
                ),
                # 第一行
                ft.Row(
                    controls=[
                        self.calc_button("AC", self.button_clicked, is_action=True),
                        self.calc_button("DEL", self.button_clicked, is_action=True),
                        self.calc_button("%", self.button_clicked, is_action=True),
                        self.calc_button("÷", self.button_clicked, is_operator=True),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                # 第二行
                ft.Row(
                    controls=[
                        self.calc_button("7", self.button_clicked),
                        self.calc_button("8", self.button_clicked),
                        self.calc_button("9", self.button_clicked),
                        self.calc_button("×", self.button_clicked, is_operator=True),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                # 第三行
                ft.Row(
                    controls=[
                        self.calc_button("4", self.button_clicked),
                        self.calc_button("5", self.button_clicked),
                        self.calc_button("6", self.button_clicked),
                        self.calc_button("-", self.button_clicked, is_operator=True),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                # 第四行
                ft.Row(
                    controls=[
                        self.calc_button("1", self.button_clicked),
                        self.calc_button("2", self.button_clicked),
                        self.calc_button("3", self.button_clicked),
                        self.calc_button("+", self.button_clicked, is_operator=True),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                # 第五行
                ft.Row(
                    controls=[
                        self.calc_button("+/-", self.button_clicked),
                        self.calc_button("0", self.button_clicked),
                        self.calc_button(".", self.button_clicked),
                        self.calc_button("=", self.button_clicked, is_equals=True),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            ],
            spacing=15,
        )

    def calc_button(self, text, handler, is_operator=False, is_action=False, is_equals=False):
        # 默认数字键样式 (深灰色)
        bgcolor = "#333333"
        color = "#ffffff"
        
        if is_operator or is_equals:
            bgcolor = "#ff9f0a" # 苹果橙色
            color = "#ffffff"
            
        elif is_action:
            bgcolor = "#a5a5a5" # 浅灰色
            color = "#000000"

        btn = ft.Container(
            content=ft.Text(value=text, size=32 if text not in ["AC", "DEL", "+/-"] else 22, color=color, weight=ft.FontWeight.BOLD),
            alignment=ft.Alignment(0, 0),
            width=75,
            height=75,
            shape=ft.BoxShape.CIRCLE, # 苹果的纯圆形按键
            bgcolor=bgcolor,
            on_click=lambda e: handler(text),
            ink=False, # 移除水波纹
        )
        return btn

    def reset(self):
        self.expression = ""
        self.evaluated = False

    def format_number(self, num):
        if num % 1 == 0:
            return int(num)
        else:
            return num

    def get_eval_expression(self):
        # 将显示用的 "×", "÷" 替换为 Python 可执行的 "*", "/"
        return self.expression.replace("×", "*").replace("÷", "/")

    def auto_evaluate(self):
        if not self.expression:
            self.result.value = "0"
            return
            
        expr = self.get_eval_expression()
        
        # 如果最后是操作符，说明还在输入中，暂时截断它进行计算
        if expr[-1] in ("+", "-", "*", "/"):
            expr = expr[:-1]
            
        if not expr:
            self.result.value = "0"
            return
            
        try:
            res = eval(expr)
            self.result.value = str(self.format_number(res))
        except Exception:
            pass # 保持上一个正确的计算结果（如发生比如被除数为0则忽略）

    def button_clicked(self, data):
        if data == "AC":
            self.result.value = "0"
            self.process.value = ""
            self.reset()
        elif data == "DEL":
            if self.evaluated:
                self.result.value = "0"
                self.process.value = ""
                self.reset()
                self.update()
                return

            self.expression = self.expression[:-1]
            self.process.value = self.expression
            self.auto_evaluate()
        elif data in ("+", "-", "×", "÷"):
            self.evaluated = False
            if self.expression == "":
                self.expression = "0" + data
            elif self.expression[-1] in ("+", "-", "×", "÷"):
                # 替换最后的操作符
                self.expression = self.expression[:-1] + data
            else:
                self.expression += data
            self.process.value = self.expression
            self.auto_evaluate()
        elif data == "=":
            self.auto_evaluate()
            # 💡 用户要求：按出等于号后，结果显示到计算过程那一行去
            self.process.value = self.result.value
            self.result.value = ""
            self.expression = self.process.value # 下次计算基于本次结果
            self.evaluated = True
        elif data == "%":
            self.evaluated = False
            try:
                res = eval(self.get_eval_expression()) / 100
                self.expression = str(self.format_number(res))
                self.process.value = self.expression
                self.result.value = self.expression # % 立即得出结果可以认为已经求值，也可以保留原样显示
                self.evaluated = True
            except Exception:
                self.result.value = "Error"
        elif data == "+/-":
            self.evaluated = False
            try:
                if self.expression:
                    res = eval(self.get_eval_expression()) * -1
                    self.expression = str(self.format_number(res))
                    self.process.value = self.expression
                    self.auto_evaluate()
            except Exception:
                pass
        else: # 数字或小数点
            if self.evaluated:
                self.expression = data
                self.evaluated = False
            else:
                self.expression += data
                
            self.process.value = self.expression
            self.auto_evaluate()
        
        # 限制字数防止溢出
        if len(self.result.value) > 12:
            self.result.value = self.result.value[:12]

        self.update()

def main(page: ft.Page):
    # 配置页面属性
    page.title = "Apple Style Calculator"
    # 自适应不同设备时，保持在中心
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = "#000000" # 全局纯黑
    page.window.width = 420
    page.window.height = 800
    page.window.resizable = True
    page.theme_mode = ft.ThemeMode.DARK # 强制深色模式
    
    # 实例化并添加主应用组件
    calc = CalculatorApp()
    page.add(calc)

if __name__ == "__main__":
    ft.app(target=main)
