# base path to YOLO directory
MODEL_PATH = "social_distancing/yolo-coco"

# initialize minimum probability to filter weak detections along with the
# threshold when applying non-maxim suppression
MIN_CONF = 0.3
NMS_THRESH = 0.3

# should NVIDIA CUDA GPU be used?
USE_GPU = True

# define the minimum safe distance (in pixels) that two people can be from each other
MIN_DISTANCE = 50

