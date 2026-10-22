import customtkinter as ctk
import re
from math import tan

pat_num = r"-?\d+.\d+"
pat_filt_front = r"(?<![*/%])"
pat_filt_back = r"(?![*/%])"
pat_filt_front_2 = r"(?<![*/%+-])"
pat_filt_back_2 = r"(?![*/%+-])"
class Vychislyator():
    def __init__(self): pass

    def base_characters(self, expression):
        new_expression = []
        for i in range(len(expression)):
            if expression[i] == "t":
                new_expression = [float(expression[1:]),"t"]
            if expression[i] in ["+", "-", "*", "/", "%", "|"] and i != 0:
                new_expression = [float(expression[:i]),expression[i],float(expression[(i+1):])]
                break
        result = 0
        match new_expression[1]:
            case "*": result = new_expression[0] * new_expression[2]
            case "/": result = new_expression[0] / new_expression[2]
            case "+": result = new_expression[0] + new_expression[2]
            case "-": result = new_expression[0] - new_expression[2]
            case "%": result = new_expression[0] % new_expression[2]
            case "|": result = round(new_expression[0]) | round(new_expression[2])
            case "t": result = tan(new_expression[0])
        return result



    def splitter(self, expression): #Последовательность обнаружения: скобки, {*,%,/}, базовые знаки
        try:
            new_expression = "".join(expression)
            flag = False
            for i in re.findall(r"tan\([^)(]+\)", new_expression):
                new_expression = new_expression.replace(i, str(self.base_characters("t"+str(float(self.splitter(i[4:-1]))))))
            if re.search(r"tan\([^)(]+\)", new_expression) is not None:
                flag = True

            for i in re.findall(r"\([^)(]+\)", new_expression):
                onlyone = re.search(rf"\({pat_num}\)", new_expression)
                if onlyone is not None:
                    onlyone = onlyone.group()
                    new_expression = new_expression.replace(onlyone,onlyone[1:-1])
                else:
                    new_expression = new_expression.replace(i, str(float(self.splitter(i[1:-1]))))
            if re.search(r"\([^)(]+\)", new_expression) is not None:
                flag = True

            for i in re.findall(rf"{pat_num}[/*%]{pat_num}", new_expression):
                new_expression = new_expression.replace(i, str(self.base_characters(i)))
            for i in re.findall(rf"{pat_filt_front}{pat_num}[+\-]{pat_num}{pat_filt_back}", new_expression):
                new_expression = new_expression.replace(i, str(self.base_characters(i)))
            if re.search(rf"{pat_num}[+\-*/%]{pat_num}", new_expression) is not None:
                flag = True

            for i in re.findall(rf"{pat_filt_front_2}{pat_num}\|{pat_num}{pat_filt_back_2}" , new_expression):
                new_expression = new_expression.replace(i, str(self.base_characters(i)))
            if re.search(rf"{pat_num}\|{pat_num}", new_expression) is not None:
                flag = True


            if flag:
                new_expression = self.splitter(new_expression)

            if round(float(new_expression)) == float(new_expression):
                return round(float(new_expression))
            else:
                return round(float(new_expression),3)
        except Exception:
            return "Error"



class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор")
        self.root.geometry("400x550")

        self.input_text = ctk.StringVar()
        self.timed = ""
        self.expression = ""
        self.list_expression = []
        self.num_color = ("#3a3a3a", "#2a2a2a")
        self.create_widgets()

    def create_widgets(self):

        self.display = ctk.CTkEntry(
            self.root,
            textvariable=self.input_text,
            justify="right",
            font=("Arial", 20),
            height=60
        )
        self.display.pack(pady=20, padx=15, fill="both")
        self.display.configure(state="readonly")
        self.button_frame = ctk.CTkFrame(self.root)
        self.button_frame.pack(pady=10, padx=15, fill="both", expand=True)
        self.button_layout("N")

    def button_layout(self, type):
        for i in self.button_frame.winfo_children():
            i.destroy()

        buttons = [
            ["(", ")", "⌫", "UN"],
            ["7", "8", "9", "-"],
            ["4", "5", "6", "+"],
            ["1", "2", "3", "*"],
            [".", "0", "/", "="]
        ]
        extended_buttons = [
            ["tan(", ")", "⌫", "N"],
            ["7", "8", "9", "-"],
            ["4", "5", "6", "+"],
            ["1", "2", "3", "|"],
            [".", "0", "%", "="]
        ]
        for i in range(5):
            self.button_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.button_frame.grid_columnconfigure(i, weight=1)

        for row_idx, row in enumerate(buttons if type == "N" else extended_buttons):
            for col_idx, btn_text in enumerate(row):
                btn = ctk.CTkButton(
                    self.button_frame,
                    text=btn_text,
                    height=60,
                    font=("Arial", 20),
                    fg_color=self.num_color,
                    command=lambda x=btn_text: self.add(x)
                )
                btn.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")

    def add(self,text):
        if text == "UN" or text == "N":
            self.button_layout(text)
        else:
            self.expression += text
            self.input_text.set(self.expression)
            digit = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
            sign = ["+", "−", "*", "%", "/", "(", ")", "tan(", "|"]
            if text == "⌫":
                if self.timed != "":
                    self.timed = ""
                else:
                    self.list_expression = self.list_expression[:-1]
                self.expression = self.expression[:-2]
                self.input_text.set(self.expression)

            elif text == "=":
                self.list_expression.append(str(float(self.timed))) if self.timed != "" else None
                self.input_text.set(vy.splitter(self.list_expression))
                self.expression = ""
                self.list_expression = []
                self.timed = ""

            elif (text == "-" and ((self.timed == "") or (self.expression[-1] in sign))) or text in digit:
                self.timed += text
            elif (text in sign) or (self.timed != ""):
                if self.timed != "":
                    self.list_expression.append(str(float(self.timed)))
                    self.timed = ""
                self.list_expression.append(text)


if __name__ == "__main__":
    root = ctk.CTk()
    app = Interface(root)
    vy = Vychislyator()
    root.mainloop()
