#!/usr/bin/env python3
"""
机器人大战外星人游戏
Robot vs Aliens Game

使用方向键移动，空格键射击
"""

import pygame
import random
import sys

# 初始化 Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🤖 机器人大战外星人 🛸")
clock = pygame.time.Clock()


class Robot(pygame.sprite.Sprite):
    """玩家控制的机器人"""
    
    def __init__(self):
        super().__init__()
        # 创建机器人图形
        self.image = pygame.Surface((50, 60), pygame.SRCALPHA)
        
        # 机器人身体
        pygame.draw.rect(self.image, BLUE, (15, 20, 20, 25))
        # 机器人头部
        pygame.draw.circle(self.image, BLUE, (25, 15), 12)
        # 机器人眼睛
        pygame.draw.circle(self.image, YELLOW, (22, 13), 3)
        pygame.draw.circle(self.image, YELLOW, (28, 13), 3)
        # 机器人手臂
        pygame.draw.rect(self.image, BLUE, (5, 25, 8, 20))
        pygame.draw.rect(self.image, BLUE, (37, 25, 8, 20))
        # 机器人腿部
        pygame.draw.rect(self.image, BLUE, (17, 45, 6, 15))
        pygame.draw.rect(self.image, BLUE, (27, 45, 6, 15))
        
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5
        self.lives = 3
        
    def move(self, keys):
        """根据按键移动机器人"""
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed


class Bullet(pygame.sprite.Sprite):
    """子弹类"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15), pygame.SRCALPHA)
        pygame.draw.rect(self.image, YELLOW, (0, 0, 6, 15))
        # 添加发光效果
        pygame.draw.rect(self.image, ORANGE, (2, 0, 2, 15))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10
        
    def update(self):
        """更新子弹位置"""
        self.rect.y += self.speed
        # 如果子弹飞出屏幕，删除它
        if self.rect.bottom < 0:
            self.kill()


class Alien(pygame.sprite.Sprite):
    """外星人类"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((45, 40), pygame.SRCALPHA)
        
        # 外星人身体（椭圆形）
        pygame.draw.ellipse(self.image, GREEN, (5, 10, 35, 25))
        # 外星人大脑袋
        pygame.draw.ellipse(self.image, GREEN, (10, 0, 25, 20))
        # 外星人眼睛
        pygame.draw.circle(self.image, RED, (17, 8), 4)
        pygame.draw.circle(self.image, RED, (28, 8), 4)
        # 外星人触角
        pygame.draw.line(self.image, GREEN, (15, 2), (10, -8), 2)
        pygame.draw.line(self.image, GREEN, (30, 2), (35, -8), 2)
        pygame.draw.circle(self.image, RED, (10, -8), 3)
        pygame.draw.circle(self.image, RED, (35, -8), 3)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 2
        self.speed_y = 0.5
        
    def update(self):
        """更新外星人位置"""
        self.rect.x += self.speed_x
        # 碰到边界就反向并下移
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.speed_x = -self.speed_x
            self.rect.y += 20


class AlienBullet(pygame.sprite.Sprite):
    """外星人子弹"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, PURPLE, (0, 0, 8, 12))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 5
        
    def update(self):
        """更新子弹位置"""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    """爆炸效果"""
    
    def __init__(self, x, y, size=30):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.frame = 0
        self.max_frames = 15
        
    def update(self):
        """更新爆炸动画"""
        self.frame += 1
        if self.frame >= self.max_frames:
            self.kill()
            return
            
        # 清除之前的绘制
        self.image.fill((0, 0, 0, 0))
        
        # 绘制爆炸效果
        radius = int(self.size * (self.frame / self.max_frames))
        alpha = 255 - int(255 * (self.frame / self.max_frames))
        
        # 外层红色
        color = (255, int(100 * (1 - self.frame/self.max_frames)), 0, alpha)
        pygame.draw.circle(self.image, color, (self.size, self.size), radius)
        
        # 内层黄色
        if self.frame > 3:
            inner_radius = int(radius * 0.6)
            color = (255, 255, 0, alpha)
            pygame.draw.circle(self.image, color, (self.size, self.size), inner_radius)


class Star:
    """背景星星"""
    
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)
        
    def update(self):
        """更新星星位置"""
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, surface):
        """绘制星星"""
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class Game:
    """游戏主类"""
    
    def __init__(self):
        self.reset_game()
        self.stars = [Star() for _ in range(100)]
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.game_over = False
        self.paused = False
        
    def reset_game(self):
        """重置游戏"""
        # 游戏状态（先设置，因为 create_aliens 需要使用）
        self.score = 0
        self.level = 1
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.game_over = False
        self.paused = False
        
        # 创建精灵组
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        
        # 创建玩家
        self.robot = Robot()
        self.all_sprites.add(self.robot)
        
        # 创建外星人
        self.create_aliens()
        
    def create_aliens(self):
        """创建外星人队列"""
        rows = 4
        cols = 8
        
        for row in range(rows):
            for col in range(cols):
                alien = Alien(50 + col * 70, 50 + row * 50)
                alien.speed_x = 2 + self.level * 0.5
                self.aliens.add(alien)
                self.all_sprites.add(alien)
                
    def shoot(self):
        """玩家射击"""
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.robot.rect.centerx, self.robot.rect.top)
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)
            
    def alien_shoot(self):
        """外星人随机射击"""
        if self.aliens and random.random() < 0.02:
            shooter = random.choice(self.aliens.sprites())
            bullet = AlienBullet(shooter.rect.centerx, shooter.rect.bottom)
            self.all_sprites.add(bullet)
            self.alien_bullets.add(bullet)
            
    def draw_hud(self):
        """绘制游戏界面"""
        # 分数
        score_text = self.font.render(f"分数：{self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # 生命值
        lives_text = self.font.render(f"生命：{'❤' * self.robot.lives}", True, RED)
        screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))
        
        # 关卡
        level_text = self.font.render(f"关卡：{self.level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - 50, 10))
        
    def draw_game_over(self):
        """绘制游戏结束画面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("游戏结束", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 50))
        
        score_text = self.font.render(f"最终分数：{self.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        
        restart_text = self.small_font.render("按 R 重新开始 或 按 Q 退出", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 50))
        
    def draw_pause(self):
        """绘制暂停画面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("游戏暂停", True, YELLOW)
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 30))
        
        resume_text = self.small_font.render("按 P 继续游戏", True, WHITE)
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 20))
        
    def update(self):
        """更新游戏状态"""
        if self.game_over or self.paused:
            return
            
        # 更新背景星星
        for star in self.stars:
            star.update()
            
        # 更新所有精灵
        self.all_sprites.update()
        
        # 玩家射击
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.shoot()
            
        # 外星人射击
        self.alien_shoot()
        
        # 检测子弹击中外星人
        for bullet in self.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.aliens, True)
            for hit in hits:
                bullet.kill()
                self.score += 100
                explosion = Explosion(hit.rect.centerx, hit.rect.centery)
                self.explosions.add(explosion)
                self.all_sprites.add(explosion)
                
        # 检测外星人子弹击中玩家
        for bullet in self.alien_bullets:
            if pygame.sprite.collide_rect(bullet, self.robot):
                bullet.kill()
                self.robot.lives -= 1
                explosion = Explosion(self.robot.rect.centerx, self.robot.rect.centery, 40)
                self.explosions.add(explosion)
                self.all_sprites.add(explosion)
                
                if self.robot.lives <= 0:
                    self.game_over = True
                    
        # 检测外星人撞到玩家
        hits = pygame.sprite.spritecollide(self.robot, self.aliens, True)
        for hit in hits:
            self.robot.lives -= 1
            explosion = Explosion(hit.rect.centerx, hit.rect.centery)
            self.explosions.add(explosion)
            self.all_sprites.add(explosion)
            
            if self.robot.lives <= 0:
                self.game_over = True
                
        # 检查是否所有外星人都被消灭
        if len(self.aliens) == 0:
            self.level += 1
            self.create_aliens()
            # 恢复玩家位置
            self.robot.rect.centerx = SCREEN_WIDTH // 2
            self.robot.rect.bottom = SCREEN_HEIGHT - 10
            
    def draw(self):
        """绘制游戏画面"""
        # 清空屏幕
        screen.fill(BLACK)
        
        # 绘制背景星星
        for star in self.stars:
            star.draw(screen)
            
        # 绘制所有精灵
        self.all_sprites.draw(screen)
        
        # 绘制界面
        self.draw_hud()
        
        # 绘制游戏结束画面
        if self.game_over:
            self.draw_game_over()
            
        # 绘制暂停画面
        if self.paused:
            self.draw_pause()
            
        # 更新显示
        pygame.display.flip()
        
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                    
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.game_over = False
                else:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                        
        return True
        
    def run(self):
        """运行游戏主循环"""
        running = True
        while running:
            clock.tick(FPS)
            running = self.handle_events()
            self.update()
            self.draw()
            
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    print("🤖 机器人大战外星人 🛸")
    print("=" * 40)
    print("操作说明：")
    print("  ← → ↑ ↓ : 移动机器人")
    print("  空格键   : 射击")
    print("  P 键     : 暂停游戏")
    print("  Q 键     : 退出游戏")
    print("  R 键     : 重新开始（游戏结束后）")
    print("=" * 40)
    
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
