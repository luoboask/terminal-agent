#!/usr/bin/env python3
"""
贪吃蛇游戏 - Snake Game
使用方向键控制蛇移动，吃到食物得分，撞墙或撞自己游戏结束
"""

import curses
import random
import time

class SnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.score = 0
        self.game_over = False
        
        # 初始化 curses
        curses.curs_set(0)  # 隐藏光标
        self.stdscr.nodelay(1)  # 非阻塞输入
        self.stdscr.timeout(100)  # 刷新间隔 (毫秒)
        
        # 初始化颜色
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 蛇
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # 食物
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # 蛇头
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # 边框
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 文字
        
        # 游戏区域边界
        self.border_top = 2
        self.border_bottom = self.height - 2
        self.border_left = 2
        self.border_right = self.width - 2
        
        # 初始化蛇 (从中间开始)
        start_x = (self.border_left + self.border_right) // 2
        start_y = (self.border_top + self.border_bottom) // 2
        self.snake = [
            [start_y, start_x],
            [start_y, start_x - 1],
            [start_y, start_x - 2]
        ]
        
        # 初始方向 (向右)
        self.direction = curses.KEY_RIGHT
        
        # 生成第一个食物
        self.food = self.generate_food()
    
    def generate_food(self):
        """生成食物，确保不在蛇身上"""
        while True:
            food_y = random.randint(self.border_top + 1, self.border_bottom - 1)
            food_x = random.randint(self.border_left + 1, self.border_right - 1)
            if [food_y, food_x] not in self.snake:
                return [food_y, food_x]
    
    def draw_border(self):
        """绘制游戏边框"""
        # 绘制上下边框
        for x in range(self.border_left, self.border_right + 1):
            self.stdscr.addch(self.border_top, x, '-', curses.color_pair(4))
            self.stdscr.addch(self.border_bottom, x, '-', curses.color_pair(4))
        
        # 绘制左右边框
        for y in range(self.border_top, self.border_bottom + 1):
            self.stdscr.addch(y, self.border_left, '|', curses.color_pair(4))
            self.stdscr.addch(y, self.border_right, '|', curses.color_pair(4))
        
        # 绘制四个角
        self.stdscr.addch(self.border_top, self.border_left, '+', curses.color_pair(4))
        self.stdscr.addch(self.border_top, self.border_right, '+', curses.color_pair(4))
        self.stdscr.addch(self.border_bottom, self.border_left, '+', curses.color_pair(4))
        self.stdscr.addch(self.border_bottom, self.border_right, '+', curses.color_pair(4))
    
    def draw(self):
        """绘制游戏画面"""
        self.stdscr.clear()
        
        # 绘制边框
        self.draw_border()
        
        # 绘制蛇
        for i, segment in enumerate(self.snake):
            y, x = segment
            if i == 0:  # 蛇头
                self.stdscr.addch(y, x, '@', curses.color_pair(3) | curses.A_BOLD)
            else:  # 蛇身
                self.stdscr.addch(y, x, 'O', curses.color_pair(1))
        
        # 绘制食物
        food_y, food_x = self.food
        self.stdscr.addch(food_y, food_x, '*', curses.color_pair(2) | curses.A_BOLD)
        
        # 显示分数
        score_text = f" Score: {self.score} "
        self.stdscr.addstr(0, (self.width - len(score_text)) // 2, score_text, 
                          curses.color_pair(5) | curses.A_BOLD)
        
        # 显示控制说明
        controls = "  ↑↓←→ 移动 | Q 退出 | P 暂停  "
        self.stdscr.addstr(1, (self.width - len(controls)) // 2, controls,
                          curses.color_pair(5))
        
        self.stdscr.refresh()
    
    def move(self):
        """移动蛇"""
        head_y, head_x = self.snake[0]
        
        # 根据方向计算新头部位置
        if self.direction == curses.KEY_UP:
            new_head = [head_y - 1, head_x]
        elif self.direction == curses.KEY_DOWN:
            new_head = [head_y + 1, head_x]
        elif self.direction == curses.KEY_LEFT:
            new_head = [head_y, head_x - 1]
        elif self.direction == curses.KEY_RIGHT:
            new_head = [head_y, head_x + 1]
        else:
            return
        
        # 检查是否撞墙
        if (new_head[0] <= self.border_top or 
            new_head[0] >= self.border_bottom or
            new_head[1] <= self.border_left or 
            new_head[1] >= self.border_right):
            self.game_over = True
            return
        
        # 检查是否撞到自己
        if new_head in self.snake[:-1]:
            self.game_over = True
            return
        
        # 移动蛇：添加新头部
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            # 加速
            current_timeout = self.stdscr.timeout()
            if current_timeout > 50:
                self.stdscr.timeout(current_timeout - 2)
        else:
            # 没吃到食物，移除尾部
            self.snake.pop()
    
    def show_game_over(self):
        """显示游戏结束画面"""
        self.stdscr.nodelay(0)  # 阻塞输入
        
        msg1 = " GAME OVER "
        msg2 = f" Final Score: {self.score} "
        msg3 = " Press R to Restart or Q to Quit "
        
        y = self.height // 2
        
        self.stdscr.addstr(y - 1, (self.width - len(msg1)) // 2, msg1,
                          curses.color_pair(2) | curses.A_BOLD | curses.A_REVERSE)
        self.stdscr.addstr(y, (self.width - len(msg2)) // 2, msg2,
                          curses.color_pair(5) | curses.A_BOLD)
        self.stdscr.addstr(y + 1, (self.width - len(msg3)) // 2, msg3,
                          curses.color_pair(5))
        
        self.stdscr.refresh()
        
        while True:
            key = self.stdscr.getch()
            if key in [ord('r'), ord('R')]:
                return True  # 重新开始
            elif key in [ord('q'), ord('Q')]:
                return False  # 退出
    
    def run(self):
        """运行游戏主循环"""
        paused = False
        
        while not self.game_over:
            self.draw()
            
            # 处理输入
            key = self.stdscr.getch()
            
            if key in [ord('q'), ord('Q')]:
                break
            elif key in [ord('p'), ord('P')]:
                paused = not paused
                if paused:
                    self.stdscr.nodelay(0)
                    self.stdscr.addstr(self.height // 2, (self.width - 7) // 2, 
                                      " PAUSED ", curses.color_pair(5) | curses.A_REVERSE)
                    self.stdscr.refresh()
                    while self.stdscr.getch() not in [ord('p'), ord('P')]:
                        pass
                    self.stdscr.nodelay(1)
                    self.stdscr.timeout(100 - self.score)
                continue
            
            # 方向控制 (不能直接反向)
            if key == curses.KEY_UP and self.direction != curses.KEY_DOWN:
                self.direction = key
            elif key == curses.KEY_DOWN and self.direction != curses.KEY_UP:
                self.direction = key
            elif key == curses.KEY_LEFT and self.direction != curses.KEY_RIGHT:
                self.direction = key
            elif key == curses.KEY_RIGHT and self.direction != curses.KEY_LEFT:
                self.direction = key
            
            if not paused:
                self.move()
        
        # 游戏结束
        if self.game_over:
            return self.show_game_over()
        return False


def main(stdscr):
    """主函数"""
    while True:
        game = SnakeGame(stdscr)
        game.run()
        
        # 如果用户选择退出
        if not game.game_over:
            break


if __name__ == "__main__":
    print("=" * 50)
    print("       🐍 贪吃蛇游戏 - Snake Game 🐍")
    print("=" * 50)
    print("\n控制方式:")
    print("  ↑ ↓ ← →  : 控制蛇的移动方向")
    print("  P        : 暂停/继续游戏")
    print("  Q        : 退出游戏")
    print("\n游戏规则:")
    print("  - 吃到食物 (*) 得 10 分")
    print("  - 撞墙或撞到自己游戏结束")
    print("  - 分数越高，速度越快!")
    print("\n按回车键开始游戏...")
    input()
    
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    
    print("\n感谢游玩！再见！👋")
