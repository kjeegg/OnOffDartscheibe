import numpy as np
import cv2
import time
from picamera2 import Picamera2, Preview
from libcamera import Transform, controls

# height of line in px
# h_line = 2

# Startwert, wird unten noch an den Maximalwert angepasst
# threshold_red = 50



# Wo ist die Linie
# Richtiges auskommentieren


# Scheibe 1
'''
y_offset = 575
x_offset = 1020
h_line = 7
w_line =700
'''

# Scheibe 2

y_offset = 613
x_offset = 1000
h_line = 6
w_line = 650

windowFrame = 30

framecount = 0
PICAM_FRAMERATE = 30
FEEDBACK_REFRESH_PERIOD = 30  # number of frames

lineCoordinates = np.index_exp[y_offset:(y_offset+h_line), x_offset:(x_offset+w_line)]
#lineCoordinates = np.index_exp[620:635, 1070:1570]
#lineCoordinates = np.index_exp[650:660,1000:1600]

#Testbild laden
#frame = cv2.imread("D:/Dart-IP/test_tesafilm_cam2_7.jpg")
#frame = cv2.imread("D:/Dart-IP/testklein2.jpg")
#def initCamera() -> Picamera2:
picam = Picamera2()
#config = picam.create_still_configuration(main={"size": (4608, 2592)})
config = picam.create_video_configuration(main={"size": (2304, 1296)})
picam.align_configuration(config)
picam.configure(config)
picam.set_controls({
    "AfMetering":controls.AfMeteringEnum.Windows,
    "AfWindows":[(x_offset,y_offset,w_line,h_line)], # A list of rectangles (tuples of 4 numbers denoting x_offset, y_offset, width and height). The rectangle units refer to the maximum scaler crop window (please refer to the ScalerCropMaximum value in the camera_properties property).
    "AeMeteringMode": controls.AeMeteringModeEnum.Spot,
    # added these (untested)
    "FrameDurationLimits": (1000000//PICAM_FRAMERATE, 1000000//PICAM_FRAMERATE),
    "AeConstraintMode": controls.AeConstraintModeEnum.Highlight
})

picam.start(show_preview=False)
'''
with picam.controls as controls:
    controls.ExposureTime = 10000
    controls.AnalogueGain = 1.0
'''
#    return picam

#time.sleep(2)
def lineCheck(mode: str = 'full_frame', thresh_quota: float = 0.95, divisor_for_threshold: float = 1.25, algorithm: str = 'count') -> bool:
    """Check camera feed for intact red line at given position in the picture

    arguments:
    mode -- 'full_frame' to check the whole given area for redness (default)
            'any_in_column' needs just one pixel per column to be red
    thresh_quota -- how much of the frame/how many of the columns have to be red for it to be considered full
    divisor_for_threshold -- reference value divided by this = threshold
    returns:
    True if the line is intact (player did not step over), otherwise False
    """
    #picam = initCamera()
    global frame_red_line_only
    global framecount
    frame = picam.capture_array()  # aktuelles Bild aus dem picam-Buffer abrufen
    if algorithm == 'edge':
        frame = frame[(y_offset-windowFrame):(y_offset+h_line+windowFrame), x_offset:(x_offset+w_line)]
        edges = cv2.Canny(frame, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=w_line, maxLineGap=10)
        if lines is not None:
            return True
        else:
            return False
    else:
        frame_red = frame[:, :, 0]  # Picam speichert RGB, dritter Index = 0 ist der Rot-Kanal
        frame_red_line_only = frame_red[lineCoordinates]  # auf vorgegebenes Linien-Rechteck zuschneiden
        #index_max_red_per_column = frame_red_line_only.argmax(0) # Index des Maximalwertes entlang Axis 0 (oben-unten)
        #value_max_red_per_column = frame_red_line_only.max(0) # Maximalwert entlang Axis 0 (oben-unten), array mit <Breite> Werten
        #reference_red = np.percentile(frame_red_line_only, 95)
        reference_red = np.max(frame_red_line_only)
        # print('reference_red=')
        # print(reference_red)
        threshold_red = reference_red // divisor_for_threshold  # "//" dividiert und rundet auf int ab
        filterframe_red = frame_red_line_only > threshold_red  # ergibt für jeden Pixel True oder False

        if mode == 'any_in_column':
            # einer der Pixel dieser Spalte ist hell genug (= hat Linie)?
            column_has_line = np.any(filterframe_red, axis=0)
        else:
            column_has_line = filterframe_red
        lineQuota = np.sum(column_has_line) / np.size(column_has_line)
        framecount += 1
        if framecount >= FEEDBACK_REFRESH_PERIOD: # don't show for every frame
            cv2.imshow("frame_red_line_only", frame_red_line_only)
            print(f"{lineQuota} liegen über {threshold_red}/255 Rotwert")
            framecount = 0
        if lineQuota > thresh_quota:
            return True
        else:
            return False


def set_framerate(rate: int):
    global PICAM_FRAMERATE
    PICAM_FRAMERATE = rate
    picam.set_controls({"FrameDurationLimits": (1000000 // PICAM_FRAMERATE, 1000000 // PICAM_FRAMERATE)})
def oldSandbox():
    """Remnants of messing around ("experimenting") with the system. Just Ignore.
    I might still want to use parts though, so keep for now.
    """
    #while True:
    for framecount in range(1):
        frame = picam.capture_array()
        frame_red = frame[:, :, 0]
        cv2.imwrite("beleuchtung.jpg", cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))
        thresh_quota = 0.9
        divisor_for_threshold = 1.2
        #print(frame)
        #print(frame.shape)

        # Bild von picam2 ist RGB

        # in HSV (Hue, Saturation, Value) konvertieren
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        # Frame zuschneiden
        # Die rote Linie sollte stets im gleichen Bereich liegen, also können Teile des Bildes entfernt werden
        #frame_red = frame_red[((frame_red.shape[0]>>1)+100):(3*frame_red.shape[0]>>2),((frame_red.shape[1]>>2)+280):((frame_red.shape[1]>>2)+900)]
        #frame_red = frame_red[((frame_red.shape[0]>>1)+498):((3*frame_red.shape[0]>>2)-100),((frame_red.shape[1]>>2)+300):((frame_red.shape[1]>>2)+320)]
        frame_red_line_only = frame_red[lineCoordinates]  # auf vorgegebenes Linien-Rechteck zuschneiden
        #frame_red = frame_red[lineCoordinates]
        hsv = hsv[lineCoordinates]

        # Experimente zur automatischen Erkennung der Linienposition
        # Index des Maximums entlang Achse 0, also oben-unten für jede Spalte finden
        '''
        print("frame_red.shape=")
        print(frame_red.shape)
        '''
        #index_max_red_per_column = frame_red.argmax(0)  # Index des Maximalwertes entlang Axis 0 (oben-unten)
        '''
        print("Maximum an x=")
        print(index_max_red)
        '''
        print("Betrag des Maximums")
    
        maxvalue_per_column = frame_red.max(0)
        print(frame_red.max(0))
        #huemap = hsv[:,:,0]
        #print(hsv)

        # schneidet auf die Ausmaße der Linie zu
        # passt noch nicht ganz
        #frame_red_line_only = np.array(frame_red [np.min(index_max_red):np.max(index_max_red)],dtype=np.uint8)
        #frame_red_line_only = np.array(frame_red [(np.mean(index_max_red)-(h_line//2)).astype(int):(np.mean(index_max_red)+(h_line//2)).astype(int)],dtype=np.uint8)
        # Alternative: vorgegebene Werte nehmen
        #frame_red_line_only = frame_red
        print("frame_red_line_only.shape=")
        print(frame_red_line_only.shape)
        print("hsv.shape=")
        print(hsv.shape)
        #cv2.imshow("line only",frame_red_line_only)
        #cv2.imshow("red frame",frame_red)

        # Definiere den Farbbereich für Rot
        lower_red = np.array([165, 60, 60])
        upper_red = np.array([180, 255, 255])

        # Maske für rote Pixel erstellen
        mask = cv2.inRange(hsv, lower_red, upper_red)

        # "//" dividiert und rundet auf int ab

        threshold_red = np.max(maxvalue_per_column) // divisor_for_threshold

        # Schwellwert auf ganze linie anwenden
        filteframe_red = frame_red > threshold_red

        # einer der Pixel dieser Spalte ist hell genug (= hat Linie)?
        column_has_line = np.any(filteframe_red, axis=0)
        column_has_lineHSV = np.any(mask, axis=0)

        lineQuota = np.sum(column_has_line) / np.size(column_has_line)
        print("red: lineQuota")
        print(lineQuota)

        if lineQuota > thresh_quota:
            print("red: line is good")
        else:
            print("red: line is not good")

        lineQuotaHSV = np.sum(column_has_lineHSV) / np.size(column_has_lineHSV)
        print("hsv: lineQuota")
        print(lineQuotaHSV)

        if lineQuotaHSV > thresh_quota:
            print("hsv: line is good")
        else:
            print("hsv: line is not good")

        #print(frame_red)
        """
        print ("column_has_line")
        print (column_has_line)
    
        print("filteframe_red")
        print(filteframe_red)
        #print("frame_red[0]")
        #print(frame_red[0])
        #print("filteframe_red[0]")
        #print(filteframe_red[0])
        '''
        print("for x in filteframe_red:")
        for x in filteframe_red:
            print (x)
        print("for x in filteframe_red[:,0]:")
        for x in filteframe_red[:,0]:
            print (x)
        #print (frame_red)
        '''
        """
        cv2.imshow("frame_red_line_only", frame_red_line_only)
        #k = cv2.waitKey(0) # Wait for a keystroke in the window
        if (cv2.waitKey(1000) & 0xFF) == ord('q'):
            break

    # release camera
    #picam.stop()

    # Idee, die leider nur mit ununterbrochener, guter Linie funktioniert
    # links senkrecht nach sehr roter Zone suchen

    # wenn gefunden, rechts in selber Zone +- einige Pixel suchen

    # Mitte zu Mitte Bresenham und prüfen, ob Linie durchgängig
    # sprich: Linie verfolgen und abspeichern, wie viele Pixel nicht rot sind.
    # Wenn rechts angekommen und <Schwellwert, ist die Linie durchgängig
'''
while True:
    lineCheck(mode='any_in_column')
    cv2.imshow("frame_red_line_only", frame_red_line_only)
    oldSandbox()
    #k = cv2.waitKey(0) # Wait for a keystroke in the window
    if (cv2.waitKey(1000) & 0xFF) == ord('q'):
        picam.stop()
        break
    

'''
