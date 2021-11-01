import pyautogui
import time
import uuid
import re

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

MOUSE_MOVE_DELAY = 0.2
buy_counter = 0
MAX_BUY = 7
shopping_session_counter = 0


def move_and_click(x, y):
    pyautogui.moveTo(x, y, duration=MOUSE_MOVE_DELAY)  # walk to and interact with drognan
    pyautogui.click()


def take_screenshot(filename, region=None):
    filename = filename + '_' + str(uuid.uuid4()) + '.png'
    if region is None:
        return pyautogui.screenshot(filename)
    else:
        return pyautogui.screenshot(filename, region=region)


def start_to_drognan():
    move_and_click(1114, 846)  # walk to and interact with drognan
    move_and_click(1253, 344)  # open merchant window


def shop_open_weapons_tab():
    for btn_weapons_tab_filename in (
    'btn_weapons_tab.png', 'btn_weapons_tab2.png', 'btn_weapons_tab3.png', 'btn_weapons_tab4.png'):
        btn_weapons_tab = pyautogui.locateOnScreen(btn_weapons_tab_filename, region=(314, 77, 190, 90))
        if btn_weapons_tab is None:
            print('weapons button ' + btn_weapons_tab_filename + ' not found')
        else:
            move_and_click(btn_weapons_tab.left + (btn_weapons_tab.width / 2),
                           btn_weapons_tab.top + (btn_weapons_tab.height / 2))
            return
    take_screenshot('error')
    exit("weapons tab not found")


def search_items():
    stop_shopping = False
    for character_class, item_names in {'paladin': ['grand_scepter', 'rune_scepter'],
                                        'necromancer': ['wand', 'bone_wand', 'yew_wand']}.items():
        for item_type in item_names:
            pyautogui.moveTo(784, 25, duration=MOUSE_MOVE_DELAY)  # move cursor outside of merchant window
            for item_location in pyautogui.locateAllOnScreen(item_type + '.png', region=(183, 129, 411, 588)):
                # if item_location.left + item_location.width > 594:
                #    print('found an item in one of the last four columns')
                #    take_screenshot('unusual_shop_layout')
                pyautogui.moveTo(item_location.left + (item_location.width / 2),
                                 item_location.top + (item_location.height / 2), duration=MOUSE_MOVE_DELAY)
                item_description = detect_text(character_class, item_type)
                log_text(character_class, item_description)
                if (character_class == 'paladin'
                    and 'PALADIN SKILL LEVELS' in item_description and 'FASTER CAST RATE' in item_description
                    and ('concentration' in item_description.lower() or 'shield' in item_description.lower() or 'blessed' in item_description.lower())) \
                    or (character_class == 'paladin'
                        and re.match(r".*\+2 T.{1} PALADIN SKILL LEVELS", item_description,
                                     re.DOTALL | re.IGNORECASE)
                        and re.match(r".*\+3 T.{1} BLesseD HAmmeR", item_description, re.DOTALL | re.IGNORECASE)
                        and re.match(r".*\+3 T.{1} Concentration", item_description, re.DOTALL | re.IGNORECASE)) \
                    or (character_class == 'necromancer'
                        and 'SKILL LEVELS' in item_description and re.match(r".*2.{1}% FASTER CAST RATE", item_description, re.DOTALL)
                        and ('resist (' in item_description.lower() or 'e explosion' in item_description.lower())):
                    stop_shopping = False
                    if buy_counter < MAX_BUY:
                        buy_item()
                    else:
                        stop_shopping = True
    return stop_shopping


def buy_item():
    global buy_counter
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


def detect_text(character_class, item_type):
    img = take_screenshot(item_type, (0, 0, 1050, 977))
    text = pytesseract.image_to_string(img, 'eng')

    m = re.search(': [0-9]{4,}(.+UNDEAD)', text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    return text


def log_text(character_class, text):
    file_object = open('log_' + character_class + '.txt', 'a')  # Open a file with access mode 'a'
    file_object.write('\n' + '===' + '\n' + text)  # Append 'hello' at the end of file
    file_object.close()  # Close the file


def log_shopping_session():
    global shopping_session_counter
    shopping_session_counter += 1
    print('shopping session #' + str(shopping_session_counter))


def start_at_startpoint():
    first_walk = True

    start_to_drognan()

    while True:
        log_shopping_session()
        shop_open_weapons_tab()
        if search_items() is True:
            print("item found, stopping")
            break

        exit_shop_window()

        drognan_to_out(first_walk)
        first_walk = False
        out_to_drognan()


def start_at_drognan():
    while True:
        exit_shop_window()

        drognan_to_out(False)
        out_to_drognan()
        log_shopping_session()
        shop_open_weapons_tab()
        if search_items() is True:
            print("item found, stopping")
            break


if __name__ == '__main__':
    pyautogui.PAUSE = 0.7
    pyautogui.FAILSAFE = True

    time.sleep(2)  # Sleep for 2 seconds

    print(pyautogui.position())  # current mouse x and y
    #  exit()

    #  start_at_startpoint()
    start_at_drognan()
