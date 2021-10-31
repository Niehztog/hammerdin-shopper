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

MOUSE_MOVE_DELAY = 0.3


def move_and_click(x, y):
    pyautogui.moveTo(x, y, duration=MOUSE_MOVE_DELAY)  # walk to and interact with drognan
    pyautogui.click()


def start_to_drognan():
    move_and_click(1114, 846)  # walk to and interact with drognan
    move_and_click(1253, 344)  # open merchant window


def shop_open_weapons_tab():
    btn_weapons_tab = pyautogui.locateOnScreen('btn_weapons_tab.png', region=(314, 77, 190, 90))
    if btn_weapons_tab is None:
        btn_weapons_tab = pyautogui.locateOnScreen('btn_weapons_tab2.png', region=(314, 77, 190, 90))
        if btn_weapons_tab is None:
            exit("weapons tab not found")
    move_and_click(btn_weapons_tab.left + (btn_weapons_tab.width / 2),
                   btn_weapons_tab.top + (btn_weapons_tab.height / 2))


def search_items():
    pyautogui.moveTo(784, 25, duration=MOUSE_MOVE_DELAY)  # move cursor outside of merchant window
    item_found = False
    for imageFile in ['grand_scepter', 'rune_scepter']:
        for i in pyautogui.locateAllOnScreen(imageFile + '.png', region=(183, 129, 584, 588)):
            pyautogui.moveTo(i.left + (i.width / 2), i.top + (i.height / 2), duration=MOUSE_MOVE_DELAY)
            item_description = detect_text(imageFile)
            if 'PALADIN SKILL LEVELS' in item_description and 'FASTER CAST RATE' in item_description:
                item_found = True
    return item_found


def exit_shop_window():
    #  pyautogui.typewrite('escape', interval=0)
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
        move_and_click(1497, 354)  # walk from drognan outside of town


def out_to_drognan():
    move_and_click(820, 809)  # walk from outside of town inside
    move_and_click(848, 601)  # walk from inside to drognan
    move_and_click(1145, 321)  # open merchant window


def detect_text(item_type):
    filename = item_type + '_' + str(uuid.uuid4()) + '.png'
    img = pyautogui.screenshot(filename)
    text = pytesseract.image_to_string(img, 'eng')

    m = re.search(': [0-9]{4,}(.+UNDEAD)', text, re.DOTALL)
    if m:
        text = m.group(1).strip()

    file_object = open('log.txt', 'a')  # Open a file with access mode 'a'
    file_object.write('\n' + '===' + '\n' + text)  # Append 'hello' at the end of file
    file_object.close()  # Close the file
    return text


def start_at_startpoint():
    first_walk = True

    start_to_drognan()

    while True:
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

        shop_open_weapons_tab()
        if search_items() is True:
            print("item found, stopping")
            break


if __name__ == '__main__':
    pyautogui.PAUSE = 1.0
    pyautogui.FAILSAFE = True

    time.sleep(2)  # Sleep for 2 seconds

    print(pyautogui.position())  # current mouse x and y
    #  exit()

    start_at_startpoint()
    #  start_at_drognan()
