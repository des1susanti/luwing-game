import pygame
import math
import random
import os

# 1. SETUP SUARA (Proteksi untuk Mac & Python 3.14)
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

current_path = os.path.dirname(__file__)
makan_sfx = None
meledak_sfx = None

try:
    # Memuat Musik Latar
    pygame.mixer.music.load(os.path.join(current_path, 'bgm.mp3'))
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)

    # Memuat Efek Suara
    makan_sfx = pygame.mixer.Sound(os.path.join(current_path, 'makan.wav'))
    meledak_sfx = pygame.mixer.Sound(os.path.join(current_path, 'meledak.wav'))
    print("Musik dan SFX berhasil dimuat!")
except Exception as e:
    print(f"Suara tidak aktif (file tidak ditemukan atau error): {e}")

# 2. KONFIGURASI LAYAR
width, height = 900, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("LUWING GAME - Sound Edition")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 22, True)
big_font = pygame.font.SysFont("arial", 72, True)
menu_font = pygame.font.SysFont("arial", 32, True)

# 3. INITIAL STATE (Variabel Game)
segments = 3
points = [[width/2, height/2] for _ in range(segments)]

food_x, food_y = random.randint(50, width-50), random.randint(50, height-50)
bomb_x, bomb_y = random.randint(50, width-50), random.randint(50, height-50)
coin_x, coin_y = random.randint(50, width-50), random.randint(50, height-50)

score = 0
lives = 3
level = 1
time_val = 0
clouds = [[random.randint(0, width), random.randint(50, 400)] for _ in range(12)]

running = True
game_over = False
game_started = False
winner = False
sound_played = False #musik loser and win
level_configs = {
    1: [(110, 170, 255), (200, 230, 255), 0.15],
    2: [(255, 140, 50), (255, 200, 100), 0.20],
   3: [(255, 182, 193), (255, 218, 225), 0.25]
}

start_btn_rect = pygame.Rect(0, 0, 260, 60)
start_btn_rect.center = (width//2, height//2 + 60)
restart_btn_rect = pygame.Rect(0, 0, 260, 60)
restart_btn_rect.center = (width//2, height//2 + 80)

def draw_pro_button(surf, rect, color, text_str, mouse_pos):
    hover = rect.collidepoint(mouse_pos)
    shadow_rect = rect.copy()
    shadow_rect.y += 4
    pygame.draw.rect(surf, (20, 20, 20), shadow_rect, border_radius=12)
    main_color = (min(color[0]+40, 255), min(color[1]+40, 255), min(color[2]+40, 255)) if hover else color
    pygame.draw.rect(surf, main_color, rect, border_radius=12)
    pygame.draw.rect(surf, (255, 255, 255), rect, 2, border_radius=12)
    text_surf = menu_font.render(text_str, True, (255, 255, 255))
    surf.blit(text_surf, text_surf.get_rect(center=rect.center))

def draw_heart(surf, x, y, size):
    color = (255, 50, 50)
    left_circle = (int(x - size//2), int(y - size//2))
    right_circle = (int(x + size//2), int(y - size//2))
    pygame.draw.circle(surf, color, left_circle, size//2)
    pygame.draw.circle(surf, color, right_circle, size//2)
    points_tri = [(x - size, y - size//4), (x + size, y - size//4), (x, y + size)]
    pygame.draw.polygon(surf, color, points_tri)

def reset_game():
    # TAMBAHKAN sound_played di baris global ini
    global points, segments, score, lives, food_x, food_y, bomb_x, bomb_y, coin_x, coin_y, game_over, level, winner, sound_played
    segments = 3
    points = [[width/2, height/2] for _ in range(segments)]
    score, lives, level = 0, 3, 1
    game_over = winner = False
    
    sound_played = False 
    pygame.mixer.music.load(os.path.join(current_path, 'bgm.mp3'))
    pygame.mixer.music.play(-1)
    
    # sound:
    sound_played = False 
    pygame.mixer.music.load(os.path.join(current_path, 'bgm.mp3'))
    pygame.mixer.music.play(-1)
# 4. MAIN LOOP
while running:
    mx, my = pygame.mouse.get_pos()
    
    if score >= 50: winner = True
    elif score >= 30: level = 3
    elif score >= 10: level = 2
    
    current_config = level_configs[level]
    c1, c2 = current_config[0], current_config[1]
    
    # Background Gradient
    for y in range(height):
        r = c1[0] + (c2[0] - c1[0]) * y // height
        g = c1[1] + (c2[1] - c1[1]) * y // height
        b = c1[2] + (c2[2] - c1[2]) * y // height
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

    # Awan
    for cloud in clouds:
        cloud[0] += 0.3
        if cloud[0] > width + 120: cloud[0] = -120
        pygame.draw.circle(screen, (255, 255, 255, 150), (int(cloud[0]), int(cloud[1])), 25)
        pygame.draw.circle(screen, (255, 255, 255, 150), (int(cloud[0]+25), int(cloud[1]+8)), 30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not game_started and start_btn_rect.collidepoint(event.pos): game_started = True
            if (game_over or winner) and restart_btn_rect.collidepoint(event.pos): reset_game()

    if game_started and not game_over and not winner:
        speed = current_config[2]
        points[0][0] += (mx - points[0][0]) * speed
        points[0][1] += (my - points[0][1]) * speed

        for i in range(1, segments):
            dx, dy = points[i-1][0] - points[i][0], points[i-1][1] - points[i][1]
            dist = math.hypot(dx, dy)
            if dist != 0: dx, dy = dx/dist, dy/dist
            points[i][0] += (points[i-1][0] - dx*12 - points[i][0]) * 0.4
            points[i][1] += (points[i-1][1] - dy*12 - points[i][1]) * 0.4

        hx, hy = points[0]
        # TABRAKAN MAKANAN
        if math.hypot(food_x-hx, food_y-hy) < 25:
            if makan_sfx: makan_sfx.play() # Bunyi makan
            score += 1
            for _ in range(2): points.append(points[-1].copy())
            segments += 2
            food_x, food_y = random.randint(50, width-50), random.randint(50, height-50)
            
        # TABRAKAN KOIN
        if math.hypot(coin_x-hx, coin_y-hy) < 25:
            if makan_sfx: makan_sfx.play() # Bunyi koin
            score += 3
            coin_x, coin_y = random.randint(50, width-50), random.randint(50, height-50)
            
        # TABRAKAN BOM
        if math.hypot(bomb_x-hx, bomb_y-hy) < 25:
            if meledak_sfx: meledak_sfx.play() # Bunyi bom
            lives -= 1
            bomb_x, bomb_y = random.randint(50, width-50), random.randint(50, height-50)
            if lives <= 0: game_over = True
           
            # --- LOGIKA MUSIK MENANG / KALAH (TAMBAHKAN DISINI) ---
    if lives <= 0: game_over = True
           
    # --- SELIPKAN DI SINI (Sejajar dengan 'if game_started') ---
    if (winner or game_over) and not sound_played:
        pygame.mixer.music.stop()
        try:
            file_musik = 'winner.mp3' if winner else 'loser.mp3'
            pygame.mixer.music.load(os.path.join(current_path, file_musik))
            pygame.mixer.music.play(0)
        except:
            pass
        sound_played = True

    # 5. DRAWING ITEMS (VERSI BARU: APEL & JAMUR BERKEDIP)
    
    # --- APEL
    pygame.draw.circle(screen, (210, 40, 40), (int(food_x), int(food_y)), 15)  # Badan Apel
    pygame.draw.rect(screen, (100, 60, 30), (int(food_x-2), int(food_y-22), 4, 10)) # Tangkai
    pygame.draw.ellipse(screen, (60, 160, 60), (int(food_x), int(food_y-20), 12, 6)) # Daun

    # --- JAMUR PINK BERKEDIP (VERSI LENGKAP) ---
    # Angka 5 adalah kecepatan kedip (semakin kecil, semakin lambat)
    if math.sin(time_val * 2) > 0: 
        # 1. Batang Jamur (Putih)
        pygame.draw.rect(screen, (255, 255, 255), (int(coin_x-7), int(coin_y), 16, 20), border_radius=4)
        
        # 2. Kepala Jamur (Pink)
        pygame.draw.ellipse(screen, (220, 50, 50), (int(coin_x-17), int(coin_y-15), 34, 24))
        # 3. Bintik Putih di atas kepala
        pygame.draw.circle(screen, (255, 255, 255), (int(coin_x-10), int(coin_y-6)), 5)
        pygame.draw.circle(screen, (255, 255, 255), (int(coin_x+8), int(coin_y-7)), 4)
        pygame.draw.circle(screen, (255, 255, 255), (int(coin_x), int(coin_y-10)), 3)
#BOM
   # Badan Bom (Radius 15 agar sama dengan ukuran apel)
    pygame.draw.circle(screen, (20, 20, 20), (int(bomb_x), int(bomb_y)), 15)
    
    # Kilatan cahaya pada bom (biar tidak terlalu polos)
    pygame.draw.circle(screen, (40, 40, 40), (int(bomb_x-5), int(bomb_y-5)), 5)
    
    # Tangkai sumbu bom
    pygame.draw.rect(screen, (100, 100, 100), (int(bomb_x-3), int(bomb_y-22), 6, 10))
    
    # Api di ujung sumbu
    # Percikan Api di ujung sumbu (Merah & Oranye)
    pygame.draw.circle(screen, (255, 140, 0), (int(bomb_x), int(bomb_y-24)), 6) # Api luar (Oranye)
    pygame.draw.circle(screen, (255, 0, 0), (int(bomb_x), int(bomb_y-24)), 3)    # Inti api (Merah)

   # DRAW ULAT (LUWING STYLE)
    for i in range(segments):
        x, y = points[i]; size = max(3, 16 - i*0.2)
        # Badan: Warna Cokelat Luwing (SaddleBrown)
        pygame.draw.circle(screen, (139, 69, 19), (int(x), int(y)), int(size))
        
        if i % 2 == 0 and i < segments-1:
            # Kaki: Warna Hitam Kecokelatan agar lebih kontras
            nx, ny = points[i+1]; angle = math.atan2(ny-y, nx-x); wave = math.sin(time_val*4 + i*0.8) * 18
            fx1, fy1 = x + math.cos(angle + 1.5) * (abs(wave) + 10), y + math.sin(angle + 1.5) * (abs(wave) + 10)
            fx2, fy2 = x + math.cos(angle - 1.5) * (abs(wave) + 10), y + math.sin(angle - 1.5) * (abs(wave) + 10)
            
            # Garis kaki (lebih tebal: 3)
            pygame.draw.line(screen, (40, 20, 0), (x, y), (fx1, fy1), 3)
            pygame.draw.line(screen, (40, 20, 0), (x, y), (fx2, fy2), 3)
            
    # Kepala Luwing: Warna lebih gelap
    pygame.draw.circle(screen, (80, 40, 10), (int(points[0][0]), int(points[0][1])), 18)
    # HUD
    hud_surf = pygame.Surface((240, 90), pygame.SRCALPHA); pygame.draw.rect(hud_surf, (0, 0, 0, 160), (0, 0, 240, 90), border_radius=15)
    screen.blit(hud_surf, (20, 20)); screen.blit(font.render(f"SCORE: {score}", True, (255, 255, 255)), (40, 35))
    screen.blit(font.render(f"LV: {level}", True, (255, 215, 0)), (180, 35))
    for i in range(lives): draw_heart(screen, 50 + (i * 30), 75, 8)

    # MENUS
    if not game_started:
        ov = pygame.Surface((width, height), pygame.SRCALPHA); ov.fill((30, 30, 50, 220)); screen.blit(ov, (0, 0))
        title = big_font.render("LUWING GAME", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(width//2, height//2 - 80)))
        draw_pro_button(screen, start_btn_rect, (60, 100, 220), "START", (mx, my))
    if winner:
        ov = pygame.Surface((width, height), pygame.SRCALPHA); ov.fill((20, 60, 20, 220)); screen.blit(ov, (0, 0))
        t = big_font.render("MISSION COMPLETED", True, (0, 255, 120))
        screen.blit(t, t.get_rect(center=(width//2, height//2 - 60)))
        draw_pro_button(screen, restart_btn_rect, (40, 180, 100), "PLAY AGAIN", (mx, my))
    if game_over and not winner:
        ov = pygame.Surface((width, height), pygame.SRCALPHA); ov.fill((60, 20, 20, 220)); screen.blit(ov, (0, 0))
        t = big_font.render("MISSION FAILED", True, (255, 80, 80))
        screen.blit(t, t.get_rect(center=(width//2, height//2 - 60)))
        draw_pro_button(screen, restart_btn_rect, (220, 60, 60), "RETRY MISSION", (mx, my))

    pygame.display.update()
    time_val += 0.05
    clock.tick(60)

pygame.quit()