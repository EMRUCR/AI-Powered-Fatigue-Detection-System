import cv2
import mediapipe as mp
import pygame
import time
import serial
import math
import tkinter as tk
from tkinter import messagebox


# necessary functions
def calculateEarDistances(eye_points):
    p1, p2, p3, p4, p5, p6 = eye_points

    vertical_1 = distance(p2, p6)
    vertical_2 = distance(p3, p5)
    horizontal = distance(p1, p4)

    EAR = (vertical_1 + vertical_2) / (2 * horizontal)

    return EAR


def distance(p1, p2):
    return math.dist(p1, p2)


def overlay_warning(frame, warning_img):
    if warning_img is None:
        return frame

    frame_h, frame_w = frame.shape[:2]

    warning_w = int(frame_w * 0.35)
    warning_h = int(warning_img.shape[0] * warning_w / warning_img.shape[1])

    warning_resized = cv2.resize(warning_img, (warning_w, warning_h))

    x = (frame_w - warning_w) // 2
    y = 150

    if y + warning_h > frame_h:
        warning_h = frame_h - y
        warning_resized = cv2.resize(warning_resized, (warning_w, warning_h))

    if warning_resized.shape[2] == 4:
        alpha = warning_resized[:, :, 3] / 255.0

        for c in range(3):
            frame[y:y+warning_h, x:x+warning_w, c] = (
                alpha * warning_resized[:, :, c] +
                (1 - alpha) * frame[y:y+warning_h, x:x+warning_w, c]
            )

    else:
        frame[y:y+warning_h, x:x+warning_w] = warning_resized[:, :, :3]

    return frame


def show_last_warning():
    root = tk.Tk()
    root.withdraw()

    messagebox.showwarning(
        "Yorgunluk Uyarısı",
        "Uyku hali tespit edildi!\nDinlenmeye ihtiyacınız var."
    )

    root.destroy()


# timing and lighting
esp32 = serial.Serial(
    port="COM3",
    baudrate=115200,
    timeout=1
)

time.sleep(2)


def send_led_command(command):
    esp32.write(f"{command}\n".encode("utf-8"))
    print("LED komutu:", command)


send_led_command("OPENING")

send_led_command("NORMAL")

led_state = "NORMAL"


eye_closed_start_time = None
eye_opened_start_time = None

is_alarm_playing = False

ALARM_DELAY_AFTER_OPEN = 2
CLOSED_TIME_LIMIT = 4


pygame.mixer.init()
pygame.mixer.music.load("warning.mp3")


# warning settings
warning_img = cv2.imread("warning.png", cv2.IMREAD_UNCHANGED)

warning_count = 0
max_warning_count = 3


# eye points in mediapipe
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]


mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


cap = cv2.VideoCapture(0)


while True:
    ret, frame = cap.read()

    if not ret:
        print("Error.")
        break

    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]

        # calculate left eye points
        left_eye_points = []

        for index in LEFT_EYE:
            landmark = face_landmarks.landmark[index]

            x = int(landmark.x * w)
            y = int(landmark.y * h)

            left_eye_points.append((x, y))

            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)


        # calculate right eye points
        right_eye_points = []

        for index in RIGHT_EYE:
            landmark = face_landmarks.landmark[index]

            x = int(landmark.x * w)
            y = int(landmark.y * h)

            right_eye_points.append((x, y))

            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)


        LEFT_EYE_EAR = calculateEarDistances(left_eye_points)
        RIGHT_EYE_EAR = calculateEarDistances(right_eye_points)

        AVG_EYE_EAR = (LEFT_EYE_EAR + RIGHT_EYE_EAR) / 2

        print("AVG EAR:", AVG_EYE_EAR)


        EAR_THRESHOLD = 0.21
        current_time = time.time()


        # if eyes are closed
        if AVG_EYE_EAR < EAR_THRESHOLD:

            # reset the open duration if the eyes close again
            eye_opened_start_time = None

            # start the timer when the eyes close
            if eye_closed_start_time is None:
                eye_closed_start_time = current_time

            # calculate how long the eyes have been closed
            closed_duration = current_time - eye_closed_start_time


            # if the alarm has not started
            if not is_alarm_playing:

                # eyes have been closed for less than two seconds
                if closed_duration < 2:
                    pass

                # switch to orange after two seconds
                elif closed_duration < CLOSED_TIME_LIMIT:

                    if led_state == "NORMAL":
                        send_led_command("NORMAL_TO_ORANGE")
                        led_state = "ORANGE"

                # switch to the red alarm after four seconds
                else:

                    if led_state == "ORANGE":
                        send_led_command("ORANGE_TO_RED")
                        led_state = "RED"

                    pygame.mixer.music.play(-1)

                    is_alarm_playing = True
                    warning_count = warning_count + 1


        # if eyes are open
        else:
            eye_closed_start_time = None


            # if the audible alarm is active
            if is_alarm_playing:

                # the first moment the eyes open
                if eye_opened_start_time is None:
                    eye_opened_start_time = current_time

                # calculate how long the eyes have been open
                opened_duration = current_time - eye_opened_start_time


                # stop the alarm after the eyes remain open for two seconds
                if opened_duration >= ALARM_DELAY_AFTER_OPEN:

                    pygame.mixer.music.stop()

                    is_alarm_playing = False
                    eye_opened_start_time = None

                    if led_state == "RED":
                        send_led_command("RED_TO_NORMAL")
                        led_state = "NORMAL"


            # if the eyes open during the orange stage before the alarm starts
            else:
                eye_opened_start_time = None

                if led_state == "ORANGE":
                    send_led_command("ORANGE_TO_NORMAL")
                    led_state = "NORMAL"


        # blink the warning image during the alarm
        if is_alarm_playing:
            if int(current_time * 2) % 2 == 0:
                frame = overlay_warning(frame, warning_img)


        if warning_count == max_warning_count:
            show_last_warning()
            break


    cv2.imshow("Yorgunluk Tespiti", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# return the system to normal when the program closes
pygame.mixer.music.stop()
send_led_command("NORMAL")

cap.release()
face_mesh.close()
esp32.close()

cv2.destroyAllWindows()