# imports
if __name__ == "__main__":
    from configs import config
    from configs.detection import detect_people
else:
    from .configs import config
    from .configs.detection import detect_people

from scipy.spatial import distance as dist 
import numpy as np
from argparse import ArgumentParser
from imutils import resize
import cv2
import os
from dataclasses import dataclass

__net           = None
__LABELS        = None
__ln            = None

@dataclass(frozen=True)
class Args:
    input   : str
    output  : str
    target  : str
    display : bool

@dataclass(frozen=True)
class FrameArgs:
    input   : str
    path    : str
    target  : str

def getArgs() -> Args:
    """
    Construct the argument parser and parse the arguments
    """
    ap = ArgumentParser(description=
    """
    Program that gets a video file from disk and uses the YOLO-Coco network 
    """)
    ap.add_argument("input"     , type=str  , help="path to input video file")
    ap.add_argument("-o", "--output"    , type=str  , default="",   help="path to output video file")
    ap.add_argument("-t", "--target"    , type=str  , nargs="?",    default="person",  help="target tag to look for in the video stream DEFAULTS TO 'person'")
    ap.add_argument("-d", "--display"   , type=bool , nargs="?",    default=False,     const=True, help="whether or not output frame should be displayed")

    temp = ap.parse_args()
    return Args(temp.input, temp.output, temp.target, temp.display)

def setUpNN():
    global __net, __LABELS, __ln
    # load the COCO class labels the YOLO model was trained on
    labelsPath = os.path.sep.join([config.MODEL_PATH, "coco.names"])
    __LABELS = open(labelsPath).read().strip().split("\n")

    # derive the paths to the YOLO weights and model configuration
    weightsPath = os.path.sep.join([config.MODEL_PATH, "yolov3.weights"])
    configPath  = os.path.sep.join([config.MODEL_PATH, "yolov3.cfg"])

    # load the YOLO object detector trained on COCO dataset (80 classes)
    print("[INFO] loading YOLO from disk...")
    __net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
    

    # check if GPU is to be used or not
    if config.USE_GPU:
        # set CUDA s the preferable backend and target
        print("[INFO] setting preferable backend and target to CUDA...")
        __net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        # print(f"cv2.dnn.DNN_BACKEND_CUDA {cv2.dnn.DNN_BACKEND_CUDA}")
        __net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        # print(f"cv2.dnn.DNN_TARGET_CUDA {cv2.dnn.DNN_TARGET_CUDA}")

    # determine only the "output" layer names that we need from YOLO
    ln = __net.getLayerNames()
    __ln = [ln[i[0] - 1] for i in __net.getUnconnectedOutLayers()]

def video_stream_parser(vs, target: str, display=False):
    global __net, __ln, __LABELS
    # loop over the frames from the video stream
    while True:
        # read the next frame from the input video
        (grabbed, frame) = vs.read()

        # if the frame was not grabbed, then that's the end fo the stream 
        if not grabbed:
            print("[INFO] Video Stream has ended")
            yield False, None
            break

        # resize the frame and then detect people (only people) in it
        frame   = resize(frame, width=700)
        results = detect_people(frame, __net, __ln, personIdx=__LABELS.index(target))

        # initialize the set of indexes that violate the minimum social distance
        violate = set()

        # ensure there are at least two people detections (required in order to compute the
        # the pairwise distance maps)
        if len(results) >= 2:
            # extract all centroids from the results and compute the Euclidean distances
            # between all pairs of the centroids
            centroids = np.array([r[2] for r in results])
            D = dist.cdist(centroids, centroids, metric="euclidean")

            # loop over the upper triangular of the distance matrix
            for i in range(0, D.shape[0]):
                for j in range(i+1, D.shape[1]):
                    # check to see if the distance between any two centroid pairs is less
                    # than the configured number of pixels
                    if D[i, j] < config.MIN_DISTANCE:
                        # update the violation set with the indexes of the centroid pairs
                        violate.add(i)
                        violate.add(j)
        
        # loop over the results
        for (i, (prob, bbox, centroid)) in enumerate(results):
            # extract the bounding box and centroid coordinates, then initialize the color of the annotation
            (startX, startY, endX, endY) = bbox
            (cX, cY) = centroid
            color = (0, 255, 0)
            #result_text -> 'Low risk'

            # if the index pair exists within the violation set, then update the color
            if i in violate:
                color = (0, 0, 255)
                #result_text -> 'High Risk'

            # draw (1) a bounding box around the person 
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            cv2.circle(frame, (cX, cY), 5, color, 1)

        # draw the total number of social distancing violations on the output frame
        text = "Social Distancing Violations: {}".format(len(violate))
        cv2.putText(frame, text, (10, frame.shape[0] - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

        # check to see if the output frame should be displayed to the screen
        if display:
            # show the output frame
            cv2.imshow("Output", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the 'q' key is pressed, break from the loop
            if key == ord("q"):
                yield False, None
                break
        
        yield True, frame

def main(args : Args):
    # initialize the video stream and pointer to output video file
    print("[INFO] accessing video stream...")
    # open input video if available else webcam stream
    vs = cv2.VideoCapture(args.input)
    writer = None

    streamer = video_stream_parser(vs, args.target, args.display)

    while True:

        cont, frame = next(streamer)

        if not cont:
            break

        # if an output video file path has been supplied and the video writer has not been 
        # initialized, do so now
        if args.output != "" and writer is None:
            # initialize the video writer
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(args.output, fourcc, 25, (frame.shape[1], frame.shape[0]), True)

        # if the video writer is not None, write the frame to the output video file
        if writer is not None:
            writer.write(frame)

def predictFrames(args : FrameArgs):
    # initialize the video stream and pointer to output video file
    print("[INFO] accessing video stream...")
    # open input video if available else webcam stream
    vs = cv2.VideoCapture(args.input)

    streamer = video_stream_parser(vs, args.target)

    count = 0

    # loop over the frames from the video stream
    while True:
        
        cont, frame = next(streamer)

        if not cont:
            break

        cv2.imwrite(f"{args.path}frame{count}.jpg",frame)
        count += 1

# Regardless of the case we setup the NN for further use.
setUpNN()

if __name__ == "__main__":
    # main(getArgs())
    predictFrames(FrameArgs("pedestrians.mp4", "frames/", "person"))