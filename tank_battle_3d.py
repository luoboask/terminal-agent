"""
3D 坦克大战游戏
使用 Ursina 引擎开发
控制方式:
- WASD 或 方向键：移动坦克
- 鼠标：控制炮塔方向
- 左键：发射炮弹
- R：重新开始游戏
- ESC：退出游戏
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

# 初始化游戏
app = Ursina()
window.title = "3D 坦克大战"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# 游戏配置
PLAYER_SPEED = 6
PLAYER_ROTATION_SPEED = 100
BULLET_SPEED = 15
ENEMY_SPEED = 3
ENEMY_SPAWN_INTERVAL = 5  # 秒
MAX_ENEMIES = 5

# 游戏状态
game_over = False
score = 0
player_health = 100
enemies = []
bullets = []
enemy_bullets = []
last_enemy_spawn = 0

# 创建地面
ground = Entity(
    model='plane',
    texture='grass',
    scale=(50, 1, 50),
    collider='box',
    texture_scale=(50, 50),
    color=color.rgb(0, 150, 0)
)

# 创建墙壁列表
walls = []

def create_wall(position, scale=(2, 3, 2), color=color.gray):
    """创建墙壁"""
    wall = Entity(
        model='cube',
        position=position,
        scale=scale,
        color=color,
        collider='box',
        texture='white_cube'
    )
    walls.append(wall)
    return wall

# 创建地图障碍物
def create_map():
    """创建游戏地图"""
    # 外围墙壁
    create_wall((0, 1.5, -25), scale=(50, 3, 1), color=color.dark_gray)
    create_wall((0, 1.5, 25), scale=(50, 3, 1), color=color.dark_gray)
    create_wall((-25, 1.5, 0), scale=(1, 3, 50), color=color.dark_gray)
    create_wall((25, 1.5, 0), scale=(1, 3, 50), color=color.dark_gray)
    
    # 内部障碍物
    positions = [
        (-10, 1.5, -10), (10, 1.5, -10),
        (-10, 1.5, 10), (10, 1.5, 10),
        (0, 1.5, 0),
        (-15, 1.5, 0), (15, 1.5, 0),
        (0, 1.5, -15), (0, 1.5, 15),
        (-20, 1.5, -5), (20, 1.5, 5),
        (-5, 1.5, 20), (5, 1.5, -20),
    ]
    
    for pos in positions:
        create_wall(pos, scale=(3, 3, 3), color=color.rgb(139, 90, 43))

create_map()

# 玩家坦克类
class PlayerTank(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.green,
            scale=(2, 1, 3),
            position=(0, 0.5, 20),
            collider='box'
        )
        
        # 炮塔
        self.turret = Entity(
            model='cube',
            color=color.dark_green,
            scale=(1.2, 0.8, 1.5),
            parent=self,
            position=(0, 0.6, 0.5),
            collider='box'
        )
        
        # 炮管
        self.barrel = Entity(
            model='cube',
            color=color.dark_green,
            scale=(0.4, 0.4, 2),
            parent=self.turret,
            position=(0, 0.3, 1)
        )
        
        self.health = 100
        self.last_shot = 0
        self.shoot_cooldown = 0.5
        
    def update(self):
        if game_over:
            return
            
        # 移动控制
        move_speed = PLAYER_SPEED * time.dt
        rotation_speed = PLAYER_ROTATION_SPEED * time.dt
        
        if held_keys['w'] or held_keys['up arrow']:
            self.position += self.forward * move_speed
        if held_keys['s'] or held_keys['down arrow']:
            self.position -= self.forward * move_speed
        if held_keys['a'] or held_keys['left arrow']:
            self.rotation_y -= rotation_speed
        if held_keys['d'] or held_keys['right arrow']:
            self.rotation_y += rotation_speed
            
        # 炮塔跟随鼠标
        if mouse.position.x < window.width / 2:
            self.turret.rotation_y -= 200 * time.dt
        if mouse.position.x > window.width / 2:
            self.turret.rotation_y += 200 * time.dt
            
        # 限制炮塔旋转
        self.turret.rotation_y = clamp(self.turret.rotation_y, -90, 90)
        
        # 射击
        if mouse.left and time.time() - self.last_shot > self.shoot_cooldown:
            self.shoot()
            self.last_shot = time.time()
            
        # 边界检查
        self.x = clamp(self.x, -23, 23)
        self.z = clamp(self.z, -23, 23)
        
    def shoot(self):
        """发射炮弹"""
        bullet_pos = self.world_position + self.forward * 2
        bullet = Entity(
            model='sphere',
            color=color.yellow,
            scale=0.3,
            position=bullet_pos,
            collider='box'
        )
        bullet.direction = self.forward
        bullet.speed = BULLET_SPEED
        bullet.is_player_bullet = True
        bullet.lifetime = 3
        bullets.append(bullet)
        
        # 射击音效（视觉反馈）
        flash = Entity(
            model='sphere',
            color=color.white,
            scale=0.5,
            position=bullet_pos,
            alpha=1
        )
        destroy(flash, delay=0.1)

# 敌方坦克类
class EnemyTank(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=color.red,
            scale=(2, 1, 3),
            position=position,
            collider='box'
        )
        
        # 炮塔
        self.turret = Entity(
            model='cube',
            color=color.dark_red,
            scale=(1.2, 0.8, 1.5),
            parent=self,
            position=(0, 0.6, 0.5),
            collider='box'
        )
        
        # 炮管
        self.barrel = Entity(
            model='cube',
            color=color.dark_red,
            scale=(0.4, 0.4, 2),
            parent=self.turret,
            position=(0, 0.3, 1)
        )
        
        self.health = 30
        self.last_shot = 0
        self.shoot_cooldown = 2
        self.move_timer = 0
        self.move_direction = random.choice([1, -1, 1, -1])
        
    def update(self):
        if game_over:
            return
            
        # 简单的 AI
        self.move_timer += time.dt
        
        # 移动
        if self.move_timer > 2:
            self.move_direction = random.choice([1, -1, 0, 0])
            self.move_timer = 0
            
        move_speed = ENEMY_SPEED * time.dt
        if self.move_direction != 0:
            self.position += self.right * self.move_direction * move_speed
            
        # 朝向玩家
        if player:
            direction_to_player = player.position - self.position
            self.look_at(player.position)
            self.rotation_y = self.rotation_y  # 保持朝向
            
        # 射击
        if player:
            distance = distance_xz(self.position, player.position)
            if distance < 20 and time.time() - self.last_shot > self.shoot_cooldown:
                if random.random() < 0.3:  # 30% 命中率
                    self.shoot()
                    self.last_shot = time.time()
                    
        # 边界检查
        self.x = clamp(self.x, -23, 23)
        self.z = clamp(self.z, -23, 23)
        
    def shoot(self):
        """发射炮弹"""
        bullet_pos = self.world_position + self.forward * 2
        bullet = Entity(
            model='sphere',
            color=color.orange,
            scale=0.3,
            position=bullet_pos,
            collider='box'
        )
        bullet.direction = self.forward
        bullet.speed = BULLET_SPEED * 0.7
        bullet.is_player_bullet = False
        bullet.lifetime = 3
        enemy_bullets.append(bullet)

# 创建玩家
player = PlayerTank()

# 相机设置
camera.position = (0, 15, 30)
camera.look_at(player.position)

# UI 元素
health_text = Text(
    text=f'生命值：{player.health}',
    position=(-0.85, 0.45),
    scale=2,
    color=color.white,
    background_color=color.black
)

score_text = Text(
    text=f'得分：{score}',
    position=(-0.85, 0.40),
    scale=2,
    color=color.yellow,
    background_color=color.black
)

enemy_count_text = Text(
    text=f'敌人：0/{MAX_ENEMIES}',
    position=(-0.85, 0.35),
    scale=1.5,
    color=color.red,
    background_color=color.black
)

game_over_text = Text(
    text='游戏结束!\n按 R 重新开始',
    origin=(0, 0),
    scale=3,
    color=color.red,
    background_color=color.black,
    enabled=False
)

# 生成敌人
def spawn_enemy():
    """在随机位置生成敌人"""
    if len(enemies) >= MAX_ENEMIES:
        return
        
    # 随机生成位置（远离玩家）
    while True:
        x = random.uniform(-20, 20)
        z = random.uniform(-20, 20)
        if distance_xz((x, 0, z), player.position) > 10:
            break
            
    enemy = EnemyTank((x, 0.5, z))
    enemies.append(enemy)

# 碰撞检测
def check_collisions():
    """检查子弹碰撞"""
    global score, player_health, game_over
    
    # 玩家子弹碰撞
    for bullet in bullets[:]:
        bullet.position += bullet.direction * bullet.speed * time.dt
        bullet.lifetime -= time.dt
        
        # 检查是否击中敌人
        for enemy in enemies[:]:
            if distance_xz(bullet.position, enemy.position) < 1.5:
                enemy.health -= 10
                bullets.remove(bullet)
                destroy(bullet)
                
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    destroy(enemy)
                    score += 100
                    score_text.text = f'得分：{score}'
                break
        else:
            # 检查是否击中墙壁
            for wall in walls:
                if distance_xz(bullet.position, wall.position) < 2:
                    bullets.remove(bullet)
                    destroy(bullet)
                    break
                    
        # 子弹过期
        if bullet.lifetime <= 0:
            if bullet in bullets:
                bullets.remove(bullet)
                destroy(bullet)
    
    # 敌方子弹碰撞
    for bullet in enemy_bullets[:]:
        bullet.position += bullet.direction * bullet.speed * time.dt
        bullet.lifetime -= time.dt
        
        # 检查是否击中玩家
        if distance_xz(bullet.position, player.position) < 1.5:
            player_health -= 10
            health_text.text = f'生命值：{player_health}'
            enemy_bullets.remove(bullet)
            destroy(bullet)
            
            if player_health <= 0:
                game_over = True
                game_over_text.enabled = True
            break
        else:
            # 检查是否击中墙壁
            for wall in walls:
                if distance_xz(bullet.position, wall.position) < 2:
                    if bullet in enemy_bullets:
                        enemy_bullets.remove(bullet)
                        destroy(bullet)
                    break
                    
        # 子弹过期
        if bullet.lifetime <= 0:
            if bullet in enemy_bullets:
                enemy_bullets.remove(bullet)
                destroy(bullet)

# 更新函数
def update():
    global game_over, last_enemy_spawn
    
    if game_over:
        if held_keys['r']:
            restart_game()
        return
    
    # 更新相机跟随玩家
    camera.position = lerp(camera.position, player.position + (0, 15, 25), time.dt * 2)
    camera.look_at(player.position)
    
    # 生成敌人
    if time.time() - last_enemy_spawn > ENEMY_SPAWN_INTERVAL:
        spawn_enemy()
        last_enemy_spawn = time.time()
        
    # 更新敌人计数
    enemy_count_text.text = f'敌人：{len(enemies)}/{MAX_ENEMIES}'
    
    # 检查碰撞
    check_collisions()

# 重新开始游戏
def restart_game():
    global game_over, score, player_health, enemies, bullets, enemy_bullets, last_enemy_spawn
    
    # 清除所有敌人和子弹
    for enemy in enemies:
        destroy(enemy)
    for bullet in bullets:
        destroy(bullet)
    for bullet in enemy_bullets:
        destroy(bullet)
        
    enemies = []
    bullets = []
    enemy_bullets = []
    
    # 重置玩家状态
    player.position = (0, 0.5, 20)
    player.rotation_y = 0
    player.health = 100
    player_health = 100
    
    # 重置游戏状态
    score = 0
    game_over = False
    last_enemy_spawn = time.time()
    
    # 更新 UI
    health_text.text = f'生命值：{player_health}'
    score_text.text = f'得分：{score}'
    game_over_text.enabled = True

# 输入处理
def input(key):
    if key == 'escape':
        application.quit()
    if key == 'r' and game_over:
        restart_game()

# 运行游戏
print("=" * 50)
print("🎮 3D 坦克大战游戏已启动!")
print("=" * 50)
print("控制方式:")
print("  WASD / 方向键 - 移动坦克")
print("  鼠标 - 控制炮塔方向")
print("  鼠标左键 - 发射炮弹")
print("  R - 重新开始游戏")
print("  ESC - 退出游戏")
print("=" * 50)

app.run()
