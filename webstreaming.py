# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# import the necessary packages
from pyimagesearch.motion_detection import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response, redirect, url_for
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2
import os
from time import sleep
from flask import request
from flask import send_file


# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
isVideoSave = False
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vs = cv2.VideoCapture(0)
time.sleep(2.0)

# Global variables pan and tilt definition and initialization
global panServoAngle
global tiltServoAngle
#panServoAngle = 0
#tiltServoAngle = 0

panPin = 27
tiltPin = 17


@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

def detect_motion(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock, namafile, timestamp

	# initialize the motion detector and the total number of frames
	# read thus far
	md = SingleMotionDetector(accumWeight=0.1)
	total = 0

	# loop over frames from the video stream
	while True:
		#print('masok')
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		#frame = vs.read()
		#frame = imutils.resize(frame, width=800)
		check, frame = vs.read()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)

		# grab the current timestamp and draw it on the frame
		timestamp = datetime.datetime.now()
		namafile = timestamp.strftime("%A %d %B %Y (%I.%M.%S %p)")
		#print(waktufoto)

		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		# if the total number of frames has reached a sufficient
		# number to construct a reasonable background model, then
		# continue to process the frame
		if total > frameCount:
			# detect motion in the image
			motion = md.detect(gray)

			# cehck to see if motion was found in the frame
			if motion is not None:
				# unpack the tuple and draw the box surrounding the
				# "motion area" on the output frame
				(thresh, (minX, minY, maxX, maxY)) = motion
				cv2.rectangle(frame, (minX, minY), (maxX, maxY),
					(0, 0, 255), 2)
		
		# update the background model and increment the total number
		# of frames read thus far
		md.update(gray)
		total += 1

		# acquire the lock, set the output frame, and release the
		# lock
		with lock:
			outputFrame = frame.copy()
	
def generate():
	print('Start Generate')
	# grab global references to the output frame and lock variables
	global outputFrame, lock, isVideoSave

	# loop over frames from the output stream
	while True:
		#print(isVideoSave)

		if isVideoSave==True :
			#print("rekam")
			out.write(outputFrame)

		#print("Generating")
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


#Capture Foto
@app.route("/capture")
def snapPhoto():
	global namafile, namafiledwn
	print("Photo Taken")
	namafiledwn = namafile
	namafile = namafile + '.jpg'
	cv2.imwrite(namafile, img=outputFrame)
	return redirect(url_for('index'))

#Download Foto
@app.route("/downloadfoto")
def downloadPhoto():
	global namafiledwn
	path = namafiledwn + '.jpg'
	return send_file(path, as_attachment=True)
	
#Rekam Video
@app.route("/startrecord")
def snapVideo():
	global isVideoSave, out, namafile, namafiledwn
	print("Rekam = True")
	isVideoSave = True
	fourcc = cv2.VideoWriter_fourcc(*'XVID') 
	namafiledwn = namafile
	namafile = namafile + '.avi'
	out = cv2.VideoWriter(namafile, fourcc, 100.0, (640, 480))
	return redirect(url_for('index'))

#Stop Rekam Video
@app.route("/stoprecord")
def stopVideo():
	global out, isVideoSave
	isVideoSave = False
	out.release()
	return redirect(url_for('index'))

#Download Video
@app.route("/downloadvideo")
def downloadVideo():
	global namafiledwn
	path = namafiledwn +'.avi'
	return send_file(path, as_attachment=True)
	

#PanTiltCam
@app.route("/<servo>/<angle>")
def move(servo, angle):
	global panServoAngle
	global tiltServoAngle
	if servo == 'pan':
		if angle == '+':
			panServoAngle = panServoAngle + 10
		else:
			panServoAngle = panServoAngle - 10
		os.system("python3 angleServo1Ctrl.py " + str(panPin) + " " + str(panServoAngle))
	if servo == 'tilt':
		if angle == '+':
			tiltServoAngle = tiltServoAngle + 10
		else:
			tiltServoAngle = tiltServoAngle - 10
		os.system("python3 angleServo2Ctrl.py " + str(tiltPin) + " " + str(tiltServoAngle))
	
	templateData = {
      'panServoAngle'	: panServoAngle,
      'tiltServoAngle'	: tiltServoAngle
	}
	return redirect(url_for('index'))

# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())

	# start a thread that will perform motion detection
	t = threading.Thread(target=detect_motion, args=(
		args["frame_count"],))
	t.daemon = True
	t.start()

	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)

# release the video stream pointer
vs.release()