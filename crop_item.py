import pyautogui
import glob
import os

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_item(im):
    width, height = im.size

    upper_horizontal = pyautogui.locate('line_horizontal.png', im)
    if upper_horizontal is None:
        return
    #  print(upper_horizontal)

    lower_horizontal = pyautogui.locate('line_horizontal.png', im, region=(upper_horizontal.left, upper_horizontal.top + 1, 128, height - upper_horizontal.top - 1))
    if lower_horizontal is None:
        return
    #  print(lower_horizontal)

    right_vertical = pyautogui.locate('line_vertical.png', im, region=(upper_horizontal.left + 128, upper_horizontal.top, width - upper_horizontal.left - 128, upper_horizontal.top + 128))
    if right_vertical is None:
        return
    #  print(right_vertical)

    return (upper_horizontal.left + 1, upper_horizontal.top + 1, right_vertical.left, lower_horizontal.top)


if __name__ == '__main__':
    pyautogui.PAUSE = 1.0
    pyautogui.FAILSAFE = True

    #  print(pyautogui.position())  # current mouse x and y

    screenshot_list = glob.glob(r'C:\Users\nilsg\Documents\Diablo II\Screenshots\Screenshot*.png')

    for filename in screenshot_list:
        im = Image.open(filename)
        box = extract_item(im)
        if box is None:
            continue
        target_filename = os.path.dirname(filename) + '\\item_' + os.path.basename(filename)
        im.crop(box).save(target_filename)

    exit()
