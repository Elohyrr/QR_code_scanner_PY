# coding: utf-8
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import requests
import json

# Configuration du webhook Discord
webhook_url = 'https://discord.com/api/webhooks/1150729103843020862/Bf_Pq02jI_EfrJE9OG8Kb4TK2OYF_jqoh2R4IFoyV3E4px4OP7ubtyNn7dG1Ssxbbu-n'

def send_to_discord(message):
    data = {
        'content': message
    }
    json_data = json.dumps(data)
    response = requests.post(webhook_url, data=json_data, headers={'Content-Type': 'application/json'})
    if response.status_code == 204:
        print("Message envoye avec succes a Discord")
    else:
        print("echec de l'envoi du message a Discord")
        print(response.text)

def process_frame(frame):
    barcodes = pyzbar.decode(frame)
    found_barcodes = set()

    for barcode in barcodes:
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        found_barcodes.add(barcodeData)
        print(f"QR Code Data: {barcodeData}")

        # Envoi des données au webhook Discord
        send_to_discord(barcodeData)

    return found_barcodes, barcodes

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
                help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())

vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
csv = open(args["output"], "w")
found = set()
scanning = True

# Ajout d'un délai entre chaque trame pour améliorer la fluidité
frame_delay = 0.01  # 10 millisecondes de délai
last_frame_time = time.time()

while scanning:
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    found_barcodes, barcodes = process_frame(frame)

    for barcode in barcodes:
        barcodeData = barcode.data.decode("utf-8")

        if barcodeData not in found:
            csv.write("{},{}\n".format(datetime.datetime.now(), barcodeData))
            csv.flush()
            found.add(barcodeData)
            scanning = False  # Arrêtez la boucle après avoir trouvé un code QR

    cv2.imshow("Barcode Reader", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        break

    # Attendez le délai entre les trames
    current_time = time.time()
    elapsed_time = current_time - last_frame_time
    if elapsed_time < frame_delay:
        time.sleep(frame_delay - elapsed_time)

    last_frame_time = current_time

print("[INFO] Nettoyage en cours...")
csv.close()
cv2.destroyAllWindows()
vs.stop()