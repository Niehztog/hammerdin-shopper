import pyautogui
import time
import uuid
import re
import pyscreeze
import pytesseract
import concurrent.futures
import threading
from PIL import Image

from crop_item import extract_item
from enum import Enum, auto

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class Diablo2Class(Enum):
    AMAZON = auto()
    SORCERESS = auto()
    NECROMANCER = auto()
    PALADIN = auto()
    BARBARIAN = auto()

class WeaponsTabNotFoundError(Exception):
    pass

MOUSE_MOVE_DELAY = 0.2
buy_counter = 0
MAX_BUY = 5
MAX_SESSIONS = 0
shopping_session_counter = 0
shopping_session_durations = list()
item_counter = dict()
item_counter_total = dict()
time_total_start = time.time()
char_type = Diablo2Class.SORCERESS


def move_and_click(x: int | None, y: int | None, right_click: bool = False, duration: float = MOUSE_MOVE_DELAY, delay: float = 0.2, mode: str = 'moveAndClick') -> None:
    if mode == 'clickOnly':
        pyautogui.click(x, y, button='right' if right_click else 'left', duration=duration)
        time.sleep(delay)
    elif mode == 'moveOnly':
        pyautogui.moveTo(x, y, duration=duration)
        time.sleep(delay)
    elif mode == 'moveAndClick':
        pyautogui.moveTo(x, y, duration=duration)
        time.sleep(delay)
        pyautogui.click(button='right' if right_click else 'left')
        time.sleep(delay)
    else:
        raise ValueError("Invalid mode. Use 'clickOnly', 'moveOnly', or 'moveAndClick'.")


def press_key(key: str, delay: float = 0.2) -> None:
    pyautogui.press(keys=key)
    time.sleep(delay)


def generate_random_filename(filename: str) -> str:
    return f'{filename}_{uuid.uuid4()}.png'


def shop_open_weapons_tab():
    for btn_weapons_tab_filename in [r'assets/btn_weapons_tab.png', r'assets/btn_weapons_tab2.png']:
        try:
            btn_weapons_tab = pyautogui.locateOnScreen(btn_weapons_tab_filename, region=(189, 95, 575, 41))
        except pyautogui.ImageNotFoundException:
            continue
        move_and_click(int(btn_weapons_tab.left + (btn_weapons_tab.width / 2)),
                       int(btn_weapons_tab.top + (btn_weapons_tab.height / 2)),
                       duration=0.05, delay=0.2, mode='clickOnly')
        return
    pyautogui.screenshot(generate_random_filename('error'))
    raise WeaponsTabNotFoundError("Weapons tab not found")


def search_items():
    global item_counter, item_counter_total, buy_counter
    item_counter = dict()
    move_and_click(784, 25, duration=0.05, delay=0.2, mode='moveOnly')  # move cursor on the red x (close button)
    items_found = find_and_process_items()

    for character_class, item_type, item_description, img, mouse_x, mouse_y in items_found:
        if not re.search(r'2.*SKILL LEVELS', item_description, re.IGNORECASE):
            continue

        item_counter[item_type] = item_counter.get(item_type, 0) + 1
        item_counter_total[item_type] = item_counter_total.get(item_type, 0) + 1
        img.save(generate_random_filename(item_type))
        log_text(character_class, item_description)

        # if (character_class == 'paladin'
        #     and 'PALADIN SKILL LEVELS' in item_description and 'FASTER CAST RATE' in item_description
        #     and ('concentration' in item_description.lower() or 'shield' in item_description.lower()
        #          or 'blessed' in item_description.lower() or 'freeze' in item_description.lower())) \

        if (character_class == 'paladin'
            and 'PALADIN SKILL LEVELS' in item_description and 'FASTER CAST RATE' in item_description
            and 'concentration' in item_description.lower() and 'blessed' in item_description.lower()) \
                or (character_class == 'paladin'
                    and 'PALADIN SKILL LEVELS' in item_description and 'FASTER CAST RATE' in item_description
                    and re.match(r".*\+3 T.{1} BLesseD HAmmeR", item_description, re.DOTALL | re.IGNORECASE)) \
                or (character_class == 'paladin'
                    and re.match(r".*\+2 T.{1} PALADIN SKILL LEVELS", item_description, re.DOTALL | re.IGNORECASE)
                    and re.match(r".*\+3 T.{1} BLesseD HAmmeR", item_description, re.DOTALL | re.IGNORECASE)
                    and re.match(r".*\+3 T.{1} Concentration", item_description, re.DOTALL | re.IGNORECASE)) \
                or (character_class == 'necromancer'
                    and 'SKILL LEVELS' in item_description and re.match(r".*2.{1}% FASTER CAST RATE",
                                                                        item_description, re.DOTALL)
                    and re.match(r".*\+3 T.{1} Corpse EXPLOSION", item_description, re.DOTALL | re.IGNORECASE)) \
                or (character_class == 'necromancer'
                    and 'SKILL LEVELS' in item_description and re.match(r".*2.{1}% FASTER CAST RATE",
                                                                        item_description, re.DOTALL)
                    and 'resist (' in item_description.lower() and 'e explosion' in item_description.lower()):
            if buy_counter < MAX_BUY:
                buy_item(mouse_x, mouse_y)
    return


def find_and_process_items() -> list[tuple[str, str, str, Image.Image, int, int]]:
    search_list = {
        'paladin': ['grand_scepter_green', 'grand_scepter_bright', 'grand_scepter_bright2', 'grand_scepter_brown',
                    'grand_scepter_grey', 'grand_scepter_black', 'grand_scepter_yellow', 'grand_scepter_red',
                    'grand_scepter_lightblue', 'grand_scepter_blue', 'grand_scepter_darkblue', 'grand_scepter_lightred',
                    'grand_scepter_lightbrown','rune_scepter']
    }
    items_processed = []
    mouse_lock = threading.Lock()

    def process_item(img: Image.Image, character_class: str, item_type: str):
        try:
            locations = list(pyautogui.locateAll(r'assets/' + item_type + '.png', img, region=(190, 137, 574, 572)))
            for loc in locations:
                mouse_x = int(loc.left + (loc.width / 2))
                mouse_y = int(loc.top + (loc.height / 2))

                with mouse_lock:
                    move_and_click(mouse_x, mouse_y, duration=0.1, delay=0.2, mode='moveOnly')
                    img_merchant_window = pyautogui.screenshot(region=(0, 0, 950, 1010))

                box = extract_item(img_merchant_window)
                if box is not None:
                    img_merchant_window = img_merchant_window.crop(box)
                else:
                    print('Failed to locate item box')
                    img_merchant_window.save(generate_random_filename('no_item_box'))

                text = pytesseract.image_to_string(
                    img_merchant_window,
                    lang='eng',
                    config='-c tessedit_char_blacklist="@®™*<>" --psm 6'
                )
                m = re.search(': [0-9]{4,}(.+UNDEAD)', text, re.DOTALL)
                if m:
                    text = m.group(1).strip()
                text = re.sub(r'\n\s*\n', '\n', text).strip()
                items_processed.append((character_class, item_type, text, img_merchant_window, mouse_x, mouse_y))
        except (pyautogui.ImageNotFoundException, pyscreeze.ImageNotFoundException):
            return

    img = pyautogui.screenshot()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for character_class, item_names in search_list.items():
            for item_type in item_names:
                futures.append(executor.submit(process_item, img, character_class, item_type))

        concurrent.futures.wait(futures)

    return items_processed


def buy_item(mouse_x: int, mouse_y: int) -> None:
    global buy_counter
    print('attempting to buy item')
    move_and_click(mouse_x, mouse_y, duration=0.05, delay=0.2, mode='clickOnly')
    move_and_click(784, 25, duration=0.05, delay=0.2, mode='moveOnly')  # move cursor outside of merchant window
    press_key(key='down', delay=0.2)
    press_key(key='enter', delay=0.2)
    buy_counter += 1


def exit_shop_window() -> None:
    if pyautogui.position() == (784, 25):
        move_and_click(None, None, duration=0.0, delay=0.1, mode='clickOnly')
    else:
        # move_and_click(784, 25)  # click red x button
        press_key(key='esc', delay=0.1)


def start_to_drognan() -> None:
    move_and_click(1114, 846, delay=0.7, mode='clickOnly') # walk to and interact with Drognan
    if char_type == Diablo2Class.SORCERESS:
        move_and_click(1239, 344, duration=0.05, delay=0.7, mode='moveAndClick') # open merchant window (sorceress)
    else:
        move_and_click(1234, 374, duration=0.05, delay=0.7, mode='moveAndClick') # open merchant window (barbarian)


def drognan_to_out(first_walk: bool = False) -> None:
    if first_walk is True:
        move_and_click(2059, 294, duration=0.05, delay=0.7, mode='clickOnly') # walk from Drognan outside of town
        move_and_click(1425, 366, duration=0.05, delay=0.7, mode='moveAndClick') # walk from Drognan outside of town
    else:
        if char_type == Diablo2Class.SORCERESS:
            move_and_click(1970, 249, duration=0.05, delay=0.7, mode='clickOnly') # walk from Drognan outside of town
            move_and_click(1400, 373, duration=0.05, delay=0.8, mode='moveAndClick') # walk from Drognan outside of town
        else:
            move_and_click(1931, 241, duration=0.05, delay=0.7, mode='clickOnly') # walk from Drognan outside of town
            move_and_click(1480, 354, delay=0.7, mode='moveAndClick') # walk from Drognan outside of town


def out_to_drognan() -> None:
    if char_type == Diablo2Class.SORCERESS:
        move_and_click(456, 954, True, duration=0.05, delay=0.2, mode='moveAndClick') # teleport from outside to Drognan
        move_and_click(1195, 489, duration=0.05, delay=0.25, mode='moveAndClick') # interact with Drognan
        move_and_click(1190, 308, duration=0.05, delay=0.25, mode='moveAndClick') # open merchant window
    else:
        move_and_click(820, 809, delay=0.7, mode='moveAndClick') # walk from outside of town inside
        move_and_click(840, 601, delay=0.7, mode='moveAndClick') # walk from inside to Drognan
        move_and_click(1150, 335, duration=0.05, delay=0.7, mode='moveAndClick') # open merchant window


def log_text(character_class: str, text: str) -> None:
    with open(f'log_{character_class}.txt', 'a') as file_object:
        file_object.write(f'\n===\n{text}')


def log_shopping_session(elapsed_time: float) -> None:
    global shopping_session_counter, shopping_session_durations
    if shopping_session_counter > 0:
        shopping_session_durations.append(elapsed_time)
    shopping_session_counter += 1
    print('shopping session #' + str(shopping_session_counter)
          + ', time elapsed ' + str(round(elapsed_time, 2)) + ' s'
          + ', results: ' + str(item_counter))


def draw_end_statistics(exit_reason: str, elapsed_time: float) -> None:
    mean_duration = sum(shopping_session_durations) / len(shopping_session_durations)
    print(exit_reason + ', stopping'
        + ', total duration: ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        + f", mean duration: {mean_duration:.2f} seconds"
        + ', results: ' + str(item_counter_total))


def main_shopping_loop() -> None:
    global time_total_start

    # Initial setup (first run)
    time_start = time.time()
    start_to_drognan()
    shop_open_weapons_tab()
    search_items()
    time_stop = time.time()
    log_shopping_session(time_stop - time_start)

    # Main loop (subsequent runs)
    while True:
        if buy_counter >= MAX_BUY:
            draw_end_statistics('item buy counter reached limit', time.time() - time_total_start)
            break
        if MAX_SESSIONS > 0 and shopping_session_counter >= MAX_SESSIONS:
            draw_end_statistics('shopping session counter reached limit', time.time() - time_total_start)
            break

        exit_shop_window()
        time_start = time.time()
        drognan_to_out(shopping_session_counter == 1) # First movement out uses different coordinates
        out_to_drognan()
        shop_open_weapons_tab()
        search_items()
        time_stop = time.time()
        log_shopping_session(time_stop - time_start)


if __name__ == '__main__':
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0

    time.sleep(2)  # Sleep for 2 seconds

    # print(pyautogui.position())  # current mouse x and y
    # pyautogui.displayMousePosition()
    # exit()

    try:
        main_shopping_loop()
    except pyautogui.FailSafeException:
        draw_end_statistics('User interrupted', time.time() - time_total_start)
    except WeaponsTabNotFoundError:
        draw_end_statistics('Weapons tab not found', time.time() - time_total_start)
