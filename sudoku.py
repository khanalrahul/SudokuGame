import pygame
import random
import pymysql


# Function to connect to the MySQL database
def connect_to_database():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="score",  # Replace with your actual database name
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Function to create a table in the database if it doesn't exist
def create_table(connection):
    with connection.cursor() as cursor:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS score (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            marks FLOAT
        )
        """
        cursor.execute(create_table_query)
    connection.commit()

# Function to store marks in the database
def store_marks_in_database(username, marks, connection):
    with connection.cursor() as cursor:
        insert_query = "INSERT INTO score (username, marks) VALUES (%s, %s)"
        cursor.execute(insert_query, (username, marks))
    connection.commit()


# Constants
WIDTH, HEIGHT = 540, 540
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)

# Fonts
pygame.font.init()
FONT = pygame.font.Font(None, 36)



# Function to generate a Sudoku puzzle of a given difficulty level
def generate_sudoku_puzzle(difficulty):
    base = 3
    side = base * base
    board = [[0] * side for _ in range(side)]

    def pattern(r, c):
        return (base * (r % base) + r // base + c) % side

    def shuffle(s):
        return random.sample(s, len(s))

    r_base = range(base)
    rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
    cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
    nums = shuffle(range(1, base * base + 1))

    # Fill the diagonal of the puzzle
    for r, c, num in zip(rows, cols, nums):
        board[r][c] = num

    # Solve the puzzle
    solve_sudoku(board)

    # Remove numbers based on difficulty level
    squares = side * side
    empties = squares * difficulty // 10
    for _ in range(empties):
        p = random.randint(0, squares - 1)
        board[p // side][p % side] = 0

    return board

# Function to draw the Sudoku grid
def draw_grid(screen, board):
    for i in range(GRID_SIZE):
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 2)
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), 2)

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            value = board[i][j]
            if value != 0:
                text = FONT.render(str(value), True, BLACK)
                text_rect = text.get_rect(center=(j * CELL_SIZE + CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(text, text_rect)

# Function to draw the selected cell
def draw_selected_cell(screen, row, col):
    pygame.draw.rect(screen, GREEN, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

# Function to check if the puzzle is solved
def is_puzzle_solved(board):
    for row in board:
        if 0 in row:
            return False
    return True

# Function to solve the Sudoku puzzle using backtracking
def solve_sudoku(board):
    empty = find_empty_location(board)
    if not empty:
        return True

    row, col = empty
    for num in range(1, GRID_SIZE + 1):
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve_sudoku(board):
                return True
            board[row][col] = 0

    return False

# Function to find an empty location in the Sudoku board
def find_empty_location(board):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if board[i][j] == 0:
                return (i, j)
    return None

# Function to check if a number can be placed in a given cell
def is_valid(board, row, col, num):
    # Check row and column
    for i in range(GRID_SIZE):
        if board[row][i] == num or board[i][col] == num:
            return False

    # Check 3x3 grid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False

    return True

# Function to display welcome screen with instructions
def welcome_screen(screen):
    screen.fill(WHITE)
    welcome_text = FONT.render("Welcome to Sudoku Solver!", True, BLACK)
    screen.blit(welcome_text, (WIDTH // 2 - welcome_text.get_width() // 2, HEIGHT // 2 - 50))
    instruction_text = FONT.render("Press any key for instruction screen.", True, BLACK)
    screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    wait_for_key()

# Function to display level selection screen
def level_selection_screen(screen):
    screen.fill(WHITE)
    level_text = FONT.render("Select Difficulty Level:", True, BLACK)
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 - 100))
    easy_text = FONT.render("1. Easy", True, BLACK)
    screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, HEIGHT // 2 - 50))
    medium_text = FONT.render("2. Medium", True, BLACK)
    screen.blit(medium_text, (WIDTH // 2 - medium_text.get_width() // 2, HEIGHT // 2))
    hard_text = FONT.render("3. Hard", True, BLACK)
    screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    return wait_for_level_selection()

# Function to display instruction screen
def instruction_screen(screen):
    screen.fill(WHITE)
    title_text = FONT.render("How to Play Sudoku:", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    instructions = [
        "1. Use arrow keys or mouse click to select a cell.",
        "2. Use number keys 1-9 to input a number into the selected cell.",
        "3. Press 'Space' to solve the puzzle automatically.",
        "4. Press 'N' to generate a new puzzle.",
        "5. Complete the puzzle by filling all cells with numbers 1-9.",
        "6. Each row, column, and 3x3 subgrid must contain all digits 1-9.",
        "7. Enjoy the game!"
    ]

    y_offset = 150
    for instruction in instructions:
        instruction_text = pygame.font.Font(None, 18).render(instruction, True, BLACK)
        screen.blit(instruction_text, (20, y_offset))
        y_offset += 30

    pygame.display.flip()
    wait_for_key()

# Function to display login screen
def login_screen(screen):
    screen.fill(WHITE)
    username = ''
    password = ''
    input_rect_username = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 30)
    input_rect_password = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 30)
    pygame.draw.rect(screen, GRAY, input_rect_username)
    pygame.draw.rect(screen, GRAY, input_rect_password)
    username_text = FONT.render("Username:", True, BLACK)
    screen.blit(username_text, (WIDTH // 2 - 100, HEIGHT // 2 - 100))
    password_text = FONT.render("Password:", True, BLACK)
    screen.blit(password_text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
    pygame.display.flip()

    active = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if username == 'user' and password == 'pass':  # Replace 'user' and 'pass' with actual credentials
                            return
                        else:
                            # Incorrect credentials, clear fields
                            username = ''
                            password = ''
                    elif event.key == pygame.K_BACKSPACE:
                        if active:
                            if input_rect_username.collidepoint(pygame.mouse.get_pos()):
                                username = username[:-1]
                            elif input_rect_password.collidepoint(pygame.mouse.get_pos()):
                                password = password[:-1]
                    else:
                        if active:
                            if input_rect_username.collidepoint(pygame.mouse.get_pos()):
                                username += event.unicode
                            elif input_rect_password.collidepoint(pygame.mouse.get_pos()):
                                password += event.unicode
                if event.key == pygame.K_TAB:
                    active = not active
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect_username.collidepoint(event.pos):
                    active = True
                elif input_rect_password.collidepoint(event.pos):
                    active = True
                else:
                    active = False
        screen.fill(WHITE)
        pygame.draw.rect(screen, GRAY, input_rect_username)
        pygame.draw.rect(screen, GRAY, input_rect_password)
        if active:
            if input_rect_username.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, BLACK, input_rect_username, 2)
            elif input_rect_password.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, BLACK, input_rect_password, 2)
        screen.blit(username_text, (WIDTH // 2 - 100, HEIGHT // 2 - 100))
        screen.blit(password_text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
        pygame.display.flip()

# Function to wait for a key press
def wait_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                waiting = False

# Function to wait for level selection
def wait_for_level_selection():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    waiting = False
                    return 1
                elif event.key == pygame.K_2:
                    waiting = False
                    return 4
                elif event.key == pygame.K_3:
                    waiting = False
                    return 7

# Function to display the main menu
def main_menu(screen):
    screen.fill(WHITE)
    play_text = FONT.render("1. Play Sudoku", True, BLACK)
    screen.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, HEIGHT // 2 - 50))
    scores_text = FONT.render("2. View Top 10 Scores", True, BLACK)
    screen.blit(scores_text, (WIDTH // 2 - scores_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    return wait_for_main_menu_selection()

# Function to wait for main menu selection
def wait_for_main_menu_selection():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    waiting = False
                    return "play"
                elif event.key == pygame.K_2:
                    waiting = False
                    return "scores"

# Function to display the past highest 10 scores
def display_top_scores(screen, connection):
    with connection.cursor() as cursor:
        select_query = "SELECT username, marks FROM score ORDER BY marks DESC LIMIT 10"
        cursor.execute(select_query)
        scores = cursor.fetchall()

    screen.fill(WHITE)
    title_text = FONT.render("Top 10 Scores:", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    y_offset = 150
    for index, score in enumerate(scores, start=1):
        score_text = pygame.font.Font(None, 24).render(f"{index}. {score['username']}: {score['marks']}", True, BLACK)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, y_offset))
        y_offset += 30

# Function to play Sudoku game
def play_sudoku():
    pygame.init()       
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku Solver")
    clock = pygame.time.Clock()

    # Connect to the database and create a table if not exists
    connection = connect_to_database()
    create_table(connection)

    while True:
        login_screen(screen)
        welcome_screen(screen)
        instruction_screen(screen)
        difficulty = level_selection_screen(screen)
        sudoku_board = generate_sudoku_puzzle(difficulty)

        selected_row, selected_col = -1, -1

        running = True
        solving = False
        start_time = pygame.time.get_ticks()  # Start time in milliseconds
        while running:
            time_passed = pygame.time.get_ticks() - start_time
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        solving = not solving
                        if solving:
                            solve_sudoku(sudoku_board)
                    elif event.key == pygame.K_n:
                        running = False
                    elif not solving and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        num = int(pygame.key.name(event.key))
                        sudoku_board[selected_row][selected_col] = num if is_valid(sudoku_board, selected_row, selected_col, num) else 0

            mouse_click = pygame.mouse.get_pressed()
            if mouse_click[0]:
                pos = pygame.mouse.get_pos()
                selected_col = pos[0] // CELL_SIZE
                selected_row = pos[1] // CELL_SIZE

            screen.fill(WHITE)
            draw_grid(screen, sudoku_board)
            if not solving:
                draw_selected_cell(screen, selected_row, selected_col)
            display_timer(screen, time_passed)

            if is_puzzle_solved(sudoku_board):
                display_completion_message(screen, time_passed, connection)
                pygame.time.wait(3000)  # Display completion message for 3 seconds
                running = False

            pygame.display.flip()
            clock.tick(FPS)

    connection.close()  # Close the database connection when done
    pygame.quit()

# Function to display completion message with score based on time taken
def display_completion_message(screen, time_passed, connection):
    completion_text = FONT.render("You completed the Game!", True, GREEN)
    screen.blit(completion_text, (WIDTH // 2 - completion_text.get_width() // 2, HEIGHT // 2))

    # Calculate score based on time taken
    score = round((GRID_SIZE * GRID_SIZE * 1000) / time_passed, 2)

    # Store the score in the database
    store_marks_in_database("user", score, connection)  # Replace with your actual username

    score_text = FONT.render("Score: {}".format(score), True, BLACK)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()

# Function to display timer
def display_timer(screen, time_passed):
    time_text = FONT.render("Time: " + format_time(time_passed), True, BLACK)
    screen.blit(time_text, (1, 1))

# Function to format time as mm:ss
def format_time(milliseconds):
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds %= 60
    return "{:02}:{:02}".format(minutes, seconds)
# Main function
if __name__ == "__main__":
    play_sudoku()