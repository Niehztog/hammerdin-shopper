import pyautogui
import time
import uuid
import re
import pyscreeze
import pytesseract
from crop_item import extract_item

try:
    from PIL import Image
except ImportError:
    import Image


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

MOUSE_MOVE_DELAY = 0.2
buy_counter = 0
MAX_BUY = 4
MAX_SESSIONS = 0
shopping_session_counter = 0
item_counter = dict()
item_counter_total = dict()
time_total_start = time.time()


def move_and_click(x, y):
    pyautogui.moveTo(x, y, duration=MOUSE_MOVE_DELAY)  # walk to and interact with drognan
    pyautogui.click()


def take_screenshot(filename, region=None):
    if isinstance(filename, str):
        filename = generate_random_filename(filename)
        if region is None:
            return pyautogui.screenshot(filename)
        else:
            return pyautogui.screenshot(filename, region=region)
    else:
        if region is None:
            return pyautogui.screenshot()
        else:
            return pyautogui.screenshot(region=region)


def generate_random_filename(filename):
    return filename + '_' + str(uuid.uuid4()) + '.png'


def start_to_drognan():
    move_and_click(1114, 846)  # walk to and interact with drognan
    move_and_click(1234, 374)  # open merchant window (large font mode)


def shop_open_weapons_tab():
    for btn_weapons_tab_filename in [r'assets/btn_weapons_tab.png', r'assets/btn_weapons_tab2.png']:
        try:
            btn_weapons_tab = pyautogui.locateOnScreen(btn_weapons_tab_filename, region=(189, 95, 575, 41))
        except pyautogui.ImageNotFoundException:
            continue
        move_and_click(btn_weapons_tab.left + (btn_weapons_tab.width / 2),
                       btn_weapons_tab.top + (btn_weapons_tab.height / 2))
        return
    take_screenshot('error')
    exit("weapons tab not found")


def search_items():
    global item_counter, item_counter_total, buy_counter
    item_counter = dict()
    # search_list = {'paladin': ['grand_scepter', 'rune_scepter'], 'necromancer': ['wand', 'bone_wand', 'yew_wand']}
    search_list = {
        'paladin': ['grand_scepter_green', 'grand_scepter_bright', 'grand_scepter_bright2', 'grand_scepter_brown',
                    'grand_scepter_grey', 'grand_scepter_black', 'grand_scepter_yellow', 'grand_scepter_red',
                    'grand_scepter_lightblue', 'grand_scepter_blue', 'grand_scepter_darkblue', 'rune_scepter']}

    items_found = []
    for character_class, item_names in search_list.items():
        for item_type in item_names:
            pyautogui.moveTo(784, 25, duration=MOUSE_MOVE_DELAY) # move cursor on the red x (close button)
            try:
                locations = list(
                    pyautogui.locateAllOnScreen(r'assets/' + item_type + '.png', region=(190, 137, 574, 572)))
                for location in locations:
                    items_found.append((character_class, item_type, location))
            except (pyautogui.ImageNotFoundException, pyscreeze.ImageNotFoundException):
                continue

    for character_class, item_type, item_location in items_found:
        pyautogui.moveTo(item_location.left + (item_location.width / 2),
                         item_location.top + (item_location.height / 2), duration=MOUSE_MOVE_DELAY)
        img = take_screenshot(False, (0, 0, 940, 900))

        box = extract_item(img)
        if box is not None:
            img = img.crop(box)

        item_description = detect_text(img)

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
                buy_item()
    return


def buy_item():
    global buy_counter
    # raise SystemExit
    print('attempting to buy item')
    pyautogui.click()
    pyautogui.moveTo(784, 25, duration=MOUSE_MOVE_DELAY)  # move cursor outside of merchant window
    pyautogui.press('down')
    pyautogui.press('enter')
    buy_counter += 1


def exit_shop_window():
    if pyautogui.position() == (784, 25):
        pyautogui.click()
    else:
        move_and_click(784, 25)  # click red x button


def drognan_to_out(first_walk):
    if first_walk is True:
        move_and_click(2059, 294)  # walk from drognan outside of town
        move_and_click(1425, 366)  # walk from drognan outside of town
    else:
        move_and_click(1931, 241)  # walk from drognan outside of town
        move_and_click(1480, 354)  # walk from drognan outside of town


def out_to_drognan():
    move_and_click(820, 809)  # walk from outside of town inside
    move_and_click(840, 601)  # walk from inside to drognan
    move_and_click(1150, 335)  # open merchant window


def detect_text(img):
    text = pytesseract.image_to_string(
        img,
        lang='eng',
        config='-c tessedit_char_blacklist="@®™*<>" --psm 6'
    )
    m = re.search(': [0-9]{4,}(.+UNDEAD)', text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    return text


def log_text(character_class, text):
    file_object = open('log_' + character_class + '.txt', 'a')
    file_object.write('\n' + '===' + '\n' + text)
    file_object.close()


def log_shopping_session(elapsed_time):
    global shopping_session_counter
    shopping_session_counter += 1
    print('shopping session #' + str(shopping_session_counter)
          + ', time elapsed ' + str(round(elapsed_time, 2)) + ' s'
          + ', results: ' + str(item_counter))


def draw_end_statistics(exit_reason, elapsed_time):
    print(exit_reason + ', stopping'
        + ', total duration: ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        + ', results: ' + str(item_counter_total))


def main_shopping_loop(first_walk=False):

    global time_total_start

    if first_walk is True:
        time_start = time.time()
        start_to_drognan()
        shop_open_weapons_tab()
        # raise SystemExit
        search_items()
        time_stop = time.time()
        log_shopping_session(time_stop - time_start)

    while True:
        exit_shop_window()

        time_start = time.time()
        drognan_to_out(first_walk)
        first_walk = False
        out_to_drognan()
        shop_open_weapons_tab()
        search_items()
        if buy_counter >= MAX_BUY:
            draw_end_statistics('item buy counter reached limit', time.time() - time_total_start)
            break
        if MAX_SESSIONS > 0 and shopping_session_counter >= MAX_SESSIONS:
            draw_end_statistics('shopping session counter reached limit', time.time() - time_total_start)
            break

        time_stop = time.time()
        log_shopping_session(time_stop - time_start)


if __name__ == '__main__':
    pyautogui.PAUSE = 0.7
    pyautogui.FAILSAFE = True

    time.sleep(2)  # Sleep for 2 seconds

    print(pyautogui.position())  # current mouse x and y
    # pyautogui.displayMousePosition()
    #  exit()

    try:
        main_shopping_loop(True)
    except pyautogui.FailSafeException:
        draw_end_statistics('User interrupted', time.time() - time_total_start)
