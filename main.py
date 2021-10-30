import pyautogui
import time

MOUSE_MOVE_DELAY = 0.3


def move_and_click(x, y):
    pyautogui.moveTo(x, y, duration=MOUSE_MOVE_DELAY)  # walk to and interact with drognan
    pyautogui.click()


def start_to_drognan():
    move_and_click(1114, 846)  # walk to and interact with drognan
    move_and_click(1253, 344)  # open merchant window


def shop_open_weapons_tab():
    btn_weapons_tab = pyautogui.locateOnScreen('btn_weapons_tab.png')
    if btn_weapons_tab is None:
        btn_weapons_tab = pyautogui.locateOnScreen('btn_weapons_tab2.png')
        if btn_weapons_tab is None:
            exit("weapons tab not found")
    move_and_click(btn_weapons_tab.left + (btn_weapons_tab.width / 2),
                     btn_weapons_tab.top + (btn_weapons_tab.height / 2))


def search_items():
    pyautogui.moveTo(846, 441, duration=MOUSE_MOVE_DELAY)  # move cursor outside of merchant window
    for imageFile in ['grand_scepter.png', 'rune_scepter.png']:
        for i in pyautogui.locateAllOnScreen(imageFile):
            pyautogui.moveTo(i.left + (i.width / 2), i.top + (i.height / 2), duration=MOUSE_MOVE_DELAY)
            return True
    return False


def exit_shop_window():
    #  pyautogui.typewrite('escape', interval=0)
    move_and_click(784, 25)  # open merchant window


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


if __name__ == '__main__':
    pyautogui.PAUSE = 1.0
    pyautogui.FAILSAFE = True

    time.sleep(2)  # Sleep for 3 seconds

    print(pyautogui.position())  # current mouse x and y
    #  exit()

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
