import curses
from random import randint
import time


def main(stdscr):
    # start screen and name your snake!
    def start_screen(stdscr):
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        stdscr.addstr(height // 3, width // 3, "Welcome to Snake Game!", curses.A_BOLD)
        stdscr.addstr(height // 2, width // 3, "Enter your snake's name:", curses.A_BOLD)
        stdscr.refresh()

        snake_name = ""
        while True:
            key = stdscr.getch()
            if key == 10:  # Enter key
                break
            elif key == 27:  # Escape key to quit
                return None
            elif 32 <= key <= 126:  # Only allow printable characters
                snake_name += chr(key)
                stdscr.clear()
                stdscr.addstr(height // 3, width // 3, "Welcome to Snake Game!", curses.A_BOLD)
                stdscr.addstr(height // 2, width // 3, "Enter your snake's name:", curses.A_BOLD)
                stdscr.addstr(height // 2 + 1, width // 3, snake_name)
                stdscr.refresh()

        stdscr.addstr(height // 2 + 3, width // 3, "Press any key to start!", curses.A_BOLD)
        stdscr.refresh()
        stdscr.getch()  # Wait for user to press a key to start the game

        # clear screen
        stdscr.clear()
        stdscr.refresh()

        return snake_name

    # initialize 
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)  # Make getch() non-blocking
    stdscr.timeout(100)  # Refresh rate in ms

    # color
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # purple snake
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)      # red food
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)    # green bonus letters

    # show start screen and get the snake's name
    snake_name = start_screen(stdscr)
    if not snake_name:  # If the user pressed escape, exit the game
        return

    # dimensions
    height, width = stdscr.getmaxyx()

    # initialize snake with a single character
    start_x = width // 4
    start_y = height // 2
    snake = [[start_y, start_x]]  # Snake segments, starting with just the head
    direction = curses.KEY_RIGHT  # Initial direction
    food = [randint(1, height - 2), randint(1, width - 2)]  # Random food position
    growth_value = randint(1, 5)  # Random number on food
    stdscr.addch(food[0], food[1], str(growth_value), curses.color_pair(2))  # Draw food

    # Power-up state
    bonus_word = None
    bonus_letters = []  # Positions of the "Yessuhhh" letters
    speed_multiplier = 1  # Default speed multiplier

    # main game loop
    while True:
        # Adjust speed based on multiplier
        stdscr.timeout(int(100 / speed_multiplier))

        # user control
        key = stdscr.getch()
        if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            direction = key

        # new head position
        head = snake[0]
        if direction == curses.KEY_UP:
            new_head = [head[0] - 1, head[1]]
        elif direction == curses.KEY_DOWN:
            new_head = [head[0] + 1, head[1]]
        elif direction == curses.KEY_LEFT:
            new_head = [head[0], head[1] - 1]
        elif direction == curses.KEY_RIGHT:
            new_head = [head[0], head[1] + 1]

        # collision checker
        game_over_message = ""
        if new_head in snake:  # Snake runs into itself
            game_over_message = "You ran into yourself!!"
        elif new_head[0] in [0, height - 1]:  # Top/bottom wall collision
            game_over_message = "GAME OVER!"
        elif new_head[1] in [0, width - 1]:  # Left/right wall collision
            game_over_message = "My Grandma could play better than that!"

        if game_over_message:
            stdscr.clear()
            stdscr.addstr(height // 2, width // 4, "Game Over!", curses.A_BOLD)
            stdscr.addstr(height // 2 + 1, width // 4, game_over_message, curses.A_BOLD)
            stdscr.refresh()
            time.sleep(2)
            break

        # add new head 
        snake.insert(0, new_head)

        # check if snake eats food
        if new_head == food:
            # Add segments to the snake based on food value
            for _ in range(growth_value - 1):
                snake.append([snake[-1][0], snake[-1][1]])  # add new segment at the last position

            # spawn that food!
            food = [randint(1, height - 2), randint(1, width - 2)]
            growth_value = randint(1, 5)  # Generate a new random number
            stdscr.addch(food[0], food[1], str(growth_value), curses.color_pair(2))  # Draw new food

        # bonus word when snake reaches 10
        if len(snake) >= 10 and not bonus_word:
            bonus_word = "wohooo"
            bonus_letters = []
            # word position
            start_row = randint(1, height - 2)
            start_col = randint(1, width - len(bonus_word) - 1)
            # placement
            for i, char in enumerate(bonus_word):
                pos = [start_row, start_col + i]
                bonus_letters.append(pos)
                stdscr.addch(pos[0], pos[1], char, curses.color_pair(3))

        # check if snake eats a bonus letter
        for letter_pos in bonus_letters[:]:
            if new_head == letter_pos:
                bonus_letters.remove(letter_pos)
                stdscr.addch(letter_pos[0], letter_pos[1], ' ')  # Clear the letter

        # check if all bonus letters are eaten
        if bonus_word and not bonus_letters:
            bonus_word = None
            speed_multiplier = 2  # Increase speed 2x

        # remove tail if no food is eaten
        if new_head != food and new_head not in bonus_letters:
            tail = snake.pop()
            stdscr.addch(tail[0], tail[1], ' ')  # Clear tail from screen

        # draw the snake's body
        for i, segment in enumerate(snake):
            if i == 0:
                stdscr.addch(segment[0], segment[1], '#', curses.color_pair(1))  # Head
            elif i <= len(snake_name):
                stdscr.addch(segment[0], segment[1], snake_name[i - 1], curses.color_pair(1))  # Name letters
            else:
                stdscr.addch(segment[0], segment[1], '#', curses.color_pair(1))  # Regular body

        # Snake name display
        snake_length = len(snake)
        stdscr.addstr(0, 0, f"{snake_name}'s Length: {snake_length}", curses.A_BOLD)

        stdscr.refresh()


# run game!
curses.wrapper(main)
