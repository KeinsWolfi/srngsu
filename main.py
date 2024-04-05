from typing import Tuple
import pyautogui
import time
from PIL import Image
import pytesseract
from discord_webhook import DiscordWebhook, DiscordEmbed
import keyboard
import autoit
import win32gui
import cv2 as cv
from pathlib import Path
import threading
import customtkinter as ctk

running = False

def main():
    global running
    running = True
    threading.Thread(target=main_func).start()
    threading.Thread(target=update_time).start()

def exit_app():
    global running
    running = False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sol's RNG")
        self.geometry("600x400")
        self.grid_columnconfigure(1 , weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.frame_buttons = ctk.CTkFrame(self, width=100)
        self.frame_buttons.grid(row = 0, column = 0, sticky = "nsew", rowspan = 2, padx = 10, pady = 10)
        self.start_button = ctk.CTkButton(self.frame_buttons, text = "Start", command = main)
        self.start_button.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = "ew")
        self.stop_button = ctk.CTkButton(self.frame_buttons, text = "Stop", command = exit_app)
        self.stop_button.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = "ew")

        self.label_frame = ctk.CTkFrame(self)
        self.label_frame.grid(row = 0, column = 1, sticky = "nsew", padx = 10, pady = 10)
        self.label_frame.grid_columnconfigure(0, weight = 1)

        self.time_caption_label = ctk.CTkLabel(self.label_frame, text = "Time")
        self.time_caption_label.grid(row = 0, column = 0, padx = 10, pady = (10, 2), sticky = "ew")
        self.time_label= ctk.CTkLabel(self.label_frame, text = "0 s")
        self.time_label.grid(row = 1, column = 0, padx = 10, pady = (2, 5), sticky = "ew")

        self.money_caption_label = ctk.CTkLabel(self.label_frame, text = "Money")
        self.money_caption_label.grid(row = 2, column = 0, padx = 10, pady = (5, 2), sticky = "ew")
        self.money_label= ctk.CTkLabel(self.label_frame, text = "0 out of needed 0")
        self.money_label.grid(row = 3, column = 0, padx = 10, pady = (2, 5), sticky = "ew")

        self.console_frame = ctk.CTkFrame(self)
        self.console_frame.grid(row = 1, column = 1, sticky = "nsew", padx = 10, pady = 10)
        self.console_frame.grid_rowconfigure(0, weight = 1)
        self.console_frame.grid_columnconfigure(0, weight = 1)

        self.console_listbox = ctk.CTkTextbox(self.console_frame)
        self.console_listbox.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = "nsew")
        self.console_listbox.configure(state = "disabled")

class Logger:
        def __init__(self, filename, console : ctk.CTkTextbox = None):
            Path("logs").mkdir(parents=True, exist_ok=True)
            self.filename = "logs/" + filename
            self.file = open(self.filename, "a+")
            self.file.seek(0)
            self.content = self.file.read()
            self.file.close()
            self.console = console

            self.console.configure(state = "normal")
            self.console.insert("end", "[" + time.strftime("%Y-%m-%d_%H-%M-%S") + "] " + "Script starting!\n")
            self.console.see("end")
            self.console.configure(state = "disabled")

        def write(self, content):
            self.file = open(self.filename, "a+")
            self.file.write("[" + time.strftime("%Y-%m-%d_%H-%M-%S") + "] " + content + "\n")

            self.console.configure(state = "normal")
            self.console.insert("end", "[" + time.strftime("%Y-%m-%d_%H-%M-%S") + "] " + content + "\n")
            self.console.see("end")
            self.console.configure(state = "disabled")

            self.file.close()

        def read(self):
            self.file = open(self.filename, "r")
            self.content = self.file.read()
            self.file.close()
            return self.content

        def clear(self):
            self.file = open(self.filename, "w")
            self.file.close()

        def error(self, content):
            self.file = open(self.filename, "a+")
            self.file.write("[ERROR] [" + time.strftime("%Y-%m-%d_%H-%M-%S") + "] " + content + "\n")

            self.console.configure(state = "normal")
            self.console.insert("end", "[ERROR] [" + time.strftime("%Y-%m-%d_%H-%M-%S") + "] " + content + "\n")
            self.console.see("end")
            self.console.configure(state = "disabled")

            self.file.close()
        
        def warn(self, content):
            self.file = open(self.filename, "a+")
            self.file.write("[WARNING] [" + time.strftime("%Y-%m-%d_%H-%M-%S") + "] " + content + "\n")

            self.console.configure(state = "normal")
            self.console.insert("end", "[WARNING] [" + time.strftime("%Y-%m-%d_%H-%M-%S") + "] " + content + "\n")
            self.console.see("end")
            self.console.configure(state = "disabled")

            self.file.close()

        def getpath(self):
            return self.filename
        
        def get_last_error(self):
            self.file = open(self.filename, "r")
            lines = self.file.readlines()
            for line in reversed(lines):
                if("[ERROR]" in line):
                    return line
            return "No errors found."

def update_time():
    global running
    start_time = time.time()
    while running:
        now = time.time()
        elapsed_time = now - start_time
        elapsed_time_sec = elapsed_time % 60
        elapsed_time_min = elapsed_time / 60
        elapsed_time_hour = elapsed_time / 3600
        app.time_label.configure(text = f'{elapsed_time_hour:.2f} h / {elapsed_time_min:.2f} m and {elapsed_time_sec:.1f} s')

def main_func():
    global running

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    webhookfile = open("webhook.txt", "a+")
    webhookfile.seek(0)
    webhook_url = webhookfile.readline()
    if(webhook_url == ""):
        webhook_url = input("Please enter your webhook url: ")
        webhookfile.write(webhook_url)
        webhookfile.close()

    webhook = DiscordWebhook(url=webhook_url)
    webhook.username = "Sol's RNG Status Update"

    embed = DiscordEmbed()

    starttime = time.time()

    change = 0
    oldNum1 = 0

    buttonRowX = 40

    def remove_non_digits(s):
        return ''.join(filter(str.isdigit, s))

    logger = Logger("log_" + time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt", app.console_listbox)

    def collectItem(times : int = 1):
        for i in range(times):
            keyboard.press_and_release('f')
            time.sleep(0.2)

    def walkforward(duration):
        keyboard.press('w')
        time.sleep(duration)
        keyboard.release('w')

    def walkbackward(duration):
        keyboard.press('s')
        time.sleep(duration)
        keyboard.release('s')

    def walkleft(duration):
        keyboard.press('a')
        time.sleep(duration)
        keyboard.release('a')

    def walkright(duration):
        keyboard.press('d')
        time.sleep(duration)
        keyboard.release('d')

    def jump():
        keyboard.press('space')
        time.sleep(0.05)
        keyboard.release('space')

    def reset():
        keyboard.press_and_release('esc')
        time.sleep(0.3)
        keyboard.press_and_release('r')
        time.sleep(0.3)
        keyboard.press_and_release('enter')
        time.sleep(4)
        walkforward(0.2)
        walkleft(5)
        time.sleep(3)

    def openInventory(privateServer : bool = True):
        closeInventory(privateServer)
        if privateServer:
            autoit.mouse_click("left", 40, 320)
        else:
            autoit.mouse_click("left", 40, 360)

    def closeInventory(privateServer : bool = True):
        if privateServer:
            autoit.mouse_click("left", 40, 670)
            autoit.mouse_click("left", 40, 320)
            autoit.mouse_click("left", 40, 320)
        else:
            autoit.mouse_click("left", 40, 700)
            autoit.mouse_click("left", 40, 360)
            autoit.mouse_click("left", 40, 360)

    def openShopGilded(craft : int = 1):
        reset()
        walkforward(3)
        walkright(2)
        walkforward(1)
        collectItem()
        time.sleep(4)
        autoit.mouse_click("left", 600, 880)
        time.sleep(1)
        autoit.mouse_move(300, 500)
        autoit.mouse_wheel("down", 4)
        time.sleep(1)
        autoit.mouse_move(550, 875)
        for i in range(craft):
            print("Crafting... (stage: " + str(i+1) + ", left:" + str(craft - (i+1)) + ")")
            autoit.mouse_click("left", 1234, 450)
            autoit.mouse_click("left", 1000, 675)
        autoit.mouse_click("left", 300, 90)

    def walkSpot(spot : int = 1):
        walktimestart = time.time()
        reset()
        if(spot == 1):
            walkleft(4.3)
            walkforward(0.7)
            collectItem(5)
            walkright(0.5)
            walkbackward(4.7)
            walkleft(0.4)
        elif(spot == 2):
            walkforward(2)
            walkright(4.1)
            walkforward(1.1)
        elif(spot == 3):
            walkbackward(0.55)
            jump()
            walkbackward(0.75)
            walkright(0.35)
            jump()
            walkright(0.5)
            jump()
            walkright(0.4)
            walkbackward(0.3)
            jump()
            walkbackward(1)
            walkleft(0.5)
            collectItem(5)
            walkright(1.9)
            walkbackward(1.25)
            walkleft(0.8)
        else:
            logger.warn(f'Invalid spot number ({spot}) or spot not implemented yet.')
            print(f'Invalid spot number ({spot}) or spot not implemented yet.')
        walktimeend = time.time()
        walktimefinal = walktimeend - walktimestart
        print(f'Walked to spot {spot} in {walktimefinal} seconds.')
            

    def focusRBLX():
        w = win32gui.FindWindow(None, 'Roblox')
        win32gui.SetForegroundWindow(w)

    def useCoins():
        autoit.mouse_click("left", buttonRowX, 460)
        time.sleep(0.5)
        try:
            coinloc = pyautogui.locateOnScreen('coin.png', confidence=0.9)
            print(f'Coins found at {coinloc.left}, {coinloc.top}')
            autoit.mouse_click("left", coinloc.left+5, coinloc.top+5)
            pyautogui.screenshot('coincount.png', region=(int(coinloc.left+(coinloc.width-30)), int(coinloc.top+coinloc.height), 46, 28))
            autoit.mouse_click("left", 460, 600)
            imageCoins = Image.open('coincount.png')
            ammount = pytesseract.image_to_string(imageCoins)
            ammount = ammount.split('x')[1]
            print(f'Coins: {ammount}')
            pyautogui.typewrite(ammount)
            autoit.mouse_click("left", 600, 600)
            closeInventory()
        except:
            logger.write("Coins not found.")
            print("Coins not found.")

    def useGCoins():
        autoit.mouse_click("left", buttonRowX, 460)
        time.sleep(0.5)
        try:
            gcoinloc = pyautogui.locateOnScreen('gcoin.png', confidence=0.9)
            print(f'GCoins found at {gcoinloc.left}, {gcoinloc.top}')
            autoit.mouse_click("left", gcoinloc.left+5, gcoinloc.top+5)
            pyautogui.screenshot('gcoincount.png', region=(int(gcoinloc.left+(gcoinloc.width-40)), int(gcoinloc.top+gcoinloc.height), 46, 28))
            autoit.mouse_click("left", 460, 600)
            imageGCoins = Image.open('gcoincount.png')
            gammount = pytesseract.image_to_string(imageGCoins)
            gammount = gammount.split('x')[1]
            print(f'GCoins: {gammount}')
            pyautogui.typewrite(gammount)
            autoit.mouse_click("left", 600, 600)
            closeInventory()
        except:
            logger.write("GCoins not found.")
            print("GCoins not found.")

    def upgradeInv():
        openInventory()
        pyautogui.screenshot('money.png', region=(20, 1002, 120-20, 1028-1000))
        pyautogui.screenshot('neededtoupgrade.png', region=(420, 811, 620-420, 840-811))

        moneyImage = cv.imread('money.png')
        moneyImageGray = cv.cvtColor(moneyImage, cv.COLOR_BGR2GRAY)
        moneyImageBlur = cv.GaussianBlur(moneyImageGray, (3, 3), 0)
        moneyImageThreshold = cv.threshold(moneyImageBlur, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
        money = pytesseract.image_to_string(moneyImageThreshold, config='--psm 10').lower()

        money = remove_non_digits(money)
        
        try:
            money = int(money)
        except:
            logger.error(f'Money is not a number ({money})')
            print(f'Money is not a number ({money}) THIS SHOULDNT HAPPEN AS ALL NON DIGITS HAVE BEEN REMOVED.')

        neededImage = cv.imread('neededtoupgrade.png')
        neededImageGray = cv.cvtColor(neededImage, cv.COLOR_BGR2GRAY)
        neededImageBlur = cv.GaussianBlur(neededImageGray, (3, 3), 0)
        neededImageThreshold = cv.threshold(neededImageBlur, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
        needed = pytesseract.image_to_string(neededImageThreshold).lower()
        
        needed = remove_non_digits(needed)

        try:
            needed = int(needed)
        except:
            logger.error(f'Needed is not a number ({needed})')
            print(f'Needed is not a number ({needed}) THIS SHOULDNT HAPPEN AS ALL NON DIGITS HAVE BEEN REMOVED.')

        app.money_label.configure(text = f'{money} out of needed {needed}')
            
        autoit.mouse_click("left", 420, 811)

        return(money, needed)

    money = "No money detected yet."

    #Set Roblox as the foreground window
    focusRBLX()

    auraTimeOut = 0

    logger.write("Starting...")

    while running:
        focusRBLX()
        cd = 60 * 10
        openInventory()

        time.sleep(1)
        #sends the webhook with the screenshot and the embed
        try:
            #Screenshot the whole screen and the auras (auras not displayed yet)
            pyautogui.screenshot('screen.png')
            pyautogui.screenshot('auras.png', region=(980, 180, 1250-980, 225-180))

            current_time = time.time()
            finalCurr = current_time - starttime

            secTime = finalCurr % 60
            secTime = str("%.2f" % secTime)
            minTime = finalCurr / 60
            minTime = str("%.2f" % minTime)
            hourTime = finalCurr / 3600
            hourTime = str("%.2f" % hourTime)
            dayTime = finalCurr / 86400
            dayTime = str("%.2f" % dayTime)

            #opens the auras image and reads the text from it
            imah = Image.open('auras.png')
            text = pytesseract.image_to_string(imah)

            #tries to split the text to get the numbers
            try:
                text = text.split("[")
                text = text[1].split("]")
                text = text[0].split("/")
                num1 = text[0]
                num2 = text[1]

                change = int(num1) - oldNum1

                if((num1 == num2) or (int(num1) >= (int(num2) - 4))):
                    logger.warn("Aura Inv full or close to full.")
                    webhook.set_content(content="@everyone AURA INV FULL OR CLOSE TO FULL!")
                    if(change != 0):
                        embed.set_description(description="Aura Inv: " + num1 + "/" + num2 + " (" + str(change) + ")")
                    else:
                        embed.set_description(description="Aura Inv: " + num1 + "/" + num2)
                else:
                    webhook.content = None
                    if(change != 0):
                        embed.add_embed_field(name="Aura Inv", value=str(num1) + "/" + str(num2) + " (" + str(change) + ")")
                    else:
                        embed.add_embed_field(name="Aura Inv", value=str(num1) + "/" + str(num2))
            except:
                logger.warn("Aura Inv not open or no auras detected.")
                print("Inventory not open or no auras detected at " + time.strftime("%Y-%m-%d : %H:%M:%S", time.localtime()))
                embed.add_embed_field(name="Aura Inv", value="No auras detected")
                auraTimeOut+=1


            #sets the title and footer of the embed
            embed.set_title(title='Sol\'s RNG')
            embed.set_footer(text="Taken at: " + time.strftime("%Y-%m-%d : %H:%M:%S", time.localtime()) + " and has been running for " + dayTime + "d/ " + hourTime + "h/ " + minTime + "m and " + secTime + "s")

            if(money == "No money detected yet."):
                embed.add_embed_field(name="Money", value=str(money))
            else:
                embed.add_embed_field(name="Money", value=str(money[0]) + " (" + str(money[1]) + " needed)")

            embed.add_embed_field(name="Last Error", value=logger.get_last_error())

            #adds the screenshot and embed to the webhook
            with open('screen.png', 'rb') as f:
                file_data_img = f.read()
            webhook.add_file(file=file_data_img, filename='screen.png')
            with open(logger.getpath(), 'rb') as f:
                file_data_log = f.read()
            webhook.add_file(file=file_data_log, filename=logger.getpath())
            webhook.add_embed(embed)

            r = webhook.execute()

            webhook.remove_embeds()
            webhook.remove_files()
            fields = embed.get_embed_fields()
            embed.fields.clear()
        except Exception as e:
            print(e)
            pass

        closeInventory()
        for i in range(3):
            walkSpot(i+1)
            logger.write(f'Walked to spot {i+1}')
            collectItem(3)
        openShopGilded(5)
        useCoins()
        useGCoins()
        money = upgradeInv()
        try:
            oldNum1 = int(num1)
        except:
            logger.error("No auras detected at script start so this failed, retrying now.")
            pass

        if(auraTimeOut >= 5):
            logger.error("Aura timeout reached. Need to reconnect.")
            print("Aura timeout reached. Need to reconnect.")
            autoit.mouse_click("left", 1000, 600)
            auraTimeOut = 0

ctk.set_default_color_theme("dark-blue")
ctk.set_appearance_mode("dark")

app = App()
app.mainloop()