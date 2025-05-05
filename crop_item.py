import pyautogui
import glob
import os
from PIL import Image

# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_item(im: Image.Image) -> tuple[int, int, int, int] | None:
    width, height = im.size

    line_horizontal_width, line_horizontal_height = 128, 1
    line_vertical_width, line_vertical_height = 1, 128
    border_color = (86, 86, 86) # (80, 80, 80)
    line_horizontal = Image.new("RGB", (line_horizontal_width, line_horizontal_height), border_color)
    line_vertical = Image.new("RGB", (line_vertical_width, line_vertical_height), border_color)

    try:
        upper_horizontal = pyautogui.locate(line_horizontal, im)
    except pyautogui.ImageNotFoundException:
        return
    # print(upper_horizontal)

    try:
        lower_horizontal = pyautogui.locate(line_horizontal, im, region=(upper_horizontal.left, upper_horizontal.top + 1, 128, height - upper_horizontal.top - 1))
    except pyautogui.ImageNotFoundException:
        return
    # print(lower_horizontal)

    try:
        right_vertical = pyautogui.locate(line_vertical, im, region=(upper_horizontal.left + 128, upper_horizontal.top, width - upper_horizontal.left - 128, upper_horizontal.top + 128))
    except pyautogui.ImageNotFoundException:
        return
    # print(right_vertical)

    return upper_horizontal.left + 1, upper_horizontal.top + 1, right_vertical.left, lower_horizontal.top


if __name__ == '__main__':
    pyautogui.PAUSE = 1.0
    pyautogui.FAILSAFE = True

    #  print(pyautogui.position())  # current mouse x and y

    screenshot_list = glob.glob(r'C:\Users\nilsg\Documents\Diablo II\Screenshots\Screenshot*.png')

    for filename in screenshot_list:
        # print(filename)
        im = Image.open(filename)
        box = extract_item(im)
        if box is None:
            continue
        target_filename = os.path.dirname(filename) + '\\item_' + os.path.basename(filename)
        im.crop(box).save(target_filename)
        print("Wrote " + target_filename)

    exit()
