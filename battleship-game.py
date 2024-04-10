from random import randint
from time import sleep

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f"({self.x}, {self.y})"

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы стреляете вне поля!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"

class BoardWrongShipException(BoardException):
    pass

class Ship:
    def __init__(self, starting_point, l, orient):
        self.starting_point = starting_point
        self.l = l
        self.orient = orient
        self.lives = l
    
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.starting_point.x
            cur_y = self.starting_point.y
            
            if self.orient == 0:
                cur_x += i
            
            elif self.orient == 1:
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid
        
        self.count = 0
        
        self.field = [[" "]*size for _ in range(size)]
        
        self.busy = []
        self.ships = []
    
    def add_ship(self, ship):
        
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)
        
        self.ships.append(ship)
        self.contour(ship)
            
    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for dot in ship.dots:
            for dx, dy in near:
                cur = Dot(dot.x + dx, dot.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "•"
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "   | 1 | 2 | 3 | 4 | 5 | 6 |\n——— ——— ——— ——— ——— ——— ———"
        for i, row in enumerate(self.field):
            res += f"\n {i + 1} | " + " | ".join(row) + " |\n——— ——— ——— ——— ——— ——— ———"
        if self.hid:
            res = res.replace("■", " ")
        return res
    
    def out(self, dot):
        return not((0<= dot.x < self.size) and (0<= dot.y < self.size))

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()
        
        if dot in self.busy:
            raise BoardUsedException()
        
        self.busy.append(dot)
        
        for ship in self.ships:
            if dot in ship.dots:
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен!")
                    sleep(2)
                    return True
                else:
                    print("Корабль ранен!")
                    sleep(2)
                    return True
        
        self.field[dot.x][dot.y] = "•"
        print("Мимо!")
        sleep(2)
        return False
    
    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        raise NotImplementedError()
    
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш выстрел: ").split()
            
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue
            
            x, y = int(x), int(y)
            
            return Dot(x-1, y-1)

class Game:
    def __init__(self, size = 6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        player = self.random_board()
        comp = self.random_board()
        comp.hid = True
        
        self.ai = AI(comp, player)
        self.us = User(player, comp)
    
    def greet(self):
        print('''
     ————————————————————————————————————————————
    |   Добро пожаловать в игру "Морской Бой"!   |
     ————————————————————————————————————————————
    |                   ПРАВИЛА                  |
    |                                            |
    |          Ваш соперник - компьютер.         |
    |     Во время своего хода Вы называете      |
    |    координаты на неизвестной вам карте     |
    |      компьютера. Если у него по этим       |
    |        координатам имеется корабль         |
    |  (координаты заняты), то корабль или его   |
    |  часть «топится»(метка Х), а Вы получаете  |
    |  право сделать ещё один ход. Ваша цель —   |
    |  первым потопить все корабли компьютера.   |
    |                                            |
    |      Корабли не касаются друг друга        |
    |            сторонами и углами.             |
    |                                            |
    |   Формат ввода хода: х(строка) у(столбец)  |
    ''')
        sleep(3)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def print_boards(self):
        print("-" * 20)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.board)
        print("-" * 20)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("-"*20)
                print("Стреляет пользователь!")
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Стреляет компьютер!")
                sleep(2)
                repeat = self.ai.move()
            if repeat:
                num -= 1
            
            if self.ai.board.count == 7:
                print('''
         ——————————————————————
        | Пользователь выиграл!|
         ——————————————————————
        ''')
                sleep(3)
                break
            
            if self.us.board.count == 7:
                print('''
         ———————————————————
        | Компьютер выиграл!|
         ———————————————————
        ''')
                sleep(3)
                break
            num += 1
            
    def start(self):
        self.greet()
        self.loop()
            
answer = 'да'
while answer == 'да':
    g = Game()
    g.start()
    answer = input("Сыграть еще раз? да/нет ")
    if answer == "да":
        continue
    else:
        print('''
         ———————
        | ПОКА! |
         ———————
      ''')
        sleep(5)
        break