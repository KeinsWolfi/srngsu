import pyautogui
import time
from PIL import Image
import pytesseract
from discord_webhook import DiscordWebhook, DiscordEmbed
import keyboard

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

while True:
    cd = 60 * 10
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

        imah = Image.open('auras.png')

        text = pytesseract.image_to_string(imah)
        

        try:
            text = text.split("[")
            text = text[1].split("]")
            text = text[0].split("/")
            num1 = text[0]
            num2 = text[1]

            change = int(num1) - oldNum1

            if((num1 == num2) or (int(num1) >= (int(num2) - 4))):
                webhook.set_content(content="@everyone AURA INV FULL OR CLOSE TO FULL!")
                if(change != 0):
                    embed.set_description(description="Aura Inv: " + num1 + "/" + num2 + " (" + str(change) + ")")
                else:
                    embed.set_description(description="Aura Inv: " + num1 + "/" + num2)
            else:
                webhook.content = None
                if(change != 0):
                    embed.set_description(description="Aura Inv: " + num1 + "/" + num2 + " (" + str(change) + ")")
                else:
                    embed.set_description(description="Aura Inv: " + num1 + "/" + num2)
        except:
            print("Inventory not open or no auras detected at " + time.strftime("%Y-%m-%d : %H:%M:%S", time.localtime()))
            webhook.set_content(content="Inventory not open or no auras detected at " + time.strftime("%Y-%m-%d : %H:%M:%S", time.localtime()))

        embed.set_title(title='Sol\'s RNG')
        embed.set_footer(text="Taken at: " + time.strftime("%Y-%m-%d : %H:%M:%S", time.localtime()) + " and has been running for " + dayTime + "d/ " + hourTime + "h/ " + minTime + "m and " + secTime + "s")

        with open('screen.png', 'rb') as f:
            file_data = f.read()
        webhook.add_file(file=file_data, filename='screen.png')
        
        webhook.add_embed(embed)

        r = webhook.execute()

        webhook.remove_embeds()
        webhook.remove_files()
    except Exception as e:
        print(e)
        pass
    while cd > 0:
        time.sleep(0.1)
        cd -= 1
        if(keyboard.is_pressed('q')):

            endtime = time.time()
            finaltime = endtime - starttime
            
            secTime = finaltime % 60
            secTime = str("%.2f" % secTime)
            minTime = finaltime / 60
            minTime = str("%.2f" % minTime)
            hourTime = finaltime / 3600
            hourTime = str("%.2f" % hourTime)
            dayTime = finaltime / 86400
            dayTime = str("%.2f" % dayTime)

            print("Ran for " + dayTime + "d/ " + hourTime + "h/ " + minTime + "m and " + secTime + "s")

            embed.set_title(title='Sol\'s RNG')
            embed.set_description(description="Ran for " + dayTime + "d/ " + hourTime + "h/ " + minTime + "m and " + secTime + "s")
            embed.set_footer(text="Ran for " + dayTime + "d/ " + hourTime + "h/ " + minTime + "m and " + secTime + "s")

            webhook.content = None
            webhook.add_embed(embed)
            webhook.execute()
            webhook.remove_embeds()

            exit()
    oldNum1 = int(num1)