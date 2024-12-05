import pygame
import sys
import time

# 화면 설정
WIDTH, HEIGHT = 240, 240
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# PyGame 초기화
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HookMan Training Grounds")
clock = pygame.time.Clock()


# 텍스트 렌더링
def render_text(text, font_size, color, pos):
    font = pygame.font.Font(None, font_size)
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=pos)
    screen.blit(rendered_text, text_rect)


# 갈고리 팔 애니메이션
def play_intro():
    arm_color = RED
    arm_length = 40
    arm_thickness = 5
    hook_color = BLUE
    hook_radius = 5

    # 갈고리 애니메이션 시작 위치
    arm_pos = [WIDTH // 2, HEIGHT // 2]
    hook_pos = [WIDTH // 2, HEIGHT // 2]
    hook_speed = [-2, -2]  # 갈고리 이동 속도

    for frame in range(90):  # 90프레임 동안 애니메이션
        screen.fill(WHITE)

        # 배경 텍스트
        render_text("HookMan", 30, BLACK, (WIDTH // 2, HEIGHT // 4))
        render_text("Training Grounds", 20, BLACK, (WIDTH // 2, HEIGHT // 4 + 30))

        # 갈고리 팔 그리기
        pygame.draw.line(screen, arm_color, arm_pos, hook_pos, arm_thickness)
        pygame.draw.circle(screen, hook_color, hook_pos, hook_radius)

        # 갈고리 이동
        hook_pos[0] += hook_speed[0]
        hook_pos[1] += hook_speed[1]

        # 경계 체크 (벽에 닿으면 반사)
        if hook_pos[0] <= 0 or hook_pos[0] >= WIDTH:
            hook_speed[0] = -hook_speed[0]
        if hook_pos[1] <= 0 or hook_pos[1] >= HEIGHT:
            hook_speed[1] = -hook_speed[1]

        # 화면 업데이트
        pygame.display.flip()
        clock.tick(FPS)

    # 인트로 완료 텍스트
    for _ in range(60):  # 2초 동안 텍스트 표시
        screen.fill(WHITE)
        render_text("Ready for Training!", 24, BLACK, (WIDTH // 2, HEIGHT // 2))
        pygame.display.flip()
        clock.tick(FPS)


# 메인 루프
def main():
    play_intro()
    print("Main game starts!")  # 여기서 메인 게임 로직으로 넘어감
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
