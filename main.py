import pygame
from game_human import HumanGame

def show_menu(screen):
    menu_font = pygame.font.Font(None, 36)
    play_button = menu_font.render("Play", True, (255, 255, 255))
    load_button = menu_font.render("Load", True, (255, 255, 255))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.get_rect.collidepoint(event.pos):
                    return "play"
                elif load_button.collidepoint(event.pos):
                    return "load"

        screen.fill((0, 0, 0))
        screen.blit(play_button, (screen_width // 2 - 50, screen_height // 2 - 30))
        screen.blit(load_button, (screen_width // 2 - 50, screen_height // 2 + 30))

        pygame.display.flip()

if __name__ == '__main__':
    pygame.init()

    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height))

    game = HumanGame(screen_width, screen_height)

    while True:
        choice = show_menu(screen)

        if choice == "play":
            game.reset()
            while True:
                game_over, score = game.play_step()

                if game_over:
                    break

            print('Final Score', score)
        
        elif choice == "load":
            # Implement loading logic here
            pass

    pygame.quit()
