# Social Distancing Detector

- [Social Distancing Detector](#social-distancing-detector)
  - [Description](#description)
  - [Motivation](#motivation)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Demo :movie_camera:](#demo-movie_camera)
  - [License :key:](#license-key)
    - [Original Repository and License](#original-repository-and-license)

## Description

A social distancing detector built with OpenCV using YOLO(COCO model) object detector.

Reformated for another way of initializing the Network and printing the results, as a module.

## Motivation

This is a repository of a bigger project that I had to do for school and thought about sharing with whomever needs some orientation.

My motiviation is not to take credit of the work done here. But to contribute to the development of OpenSource Software. Therefore the original LICENSE & Readme file are in the folder **originalFiles**. 

Also here is the [link](https://github.com/aibenStunner/social-distancing-detector) to the original repository.

## Installation

1. Clone the repo

```bash
   $ git clone https://github.com/JOmarCuenca/social-distancing-detector
   $ cd social-distancing-detector
```

2. Install dependencies in a virtual env.

```bash
   $ python3 -m venv env && source env/bin/activate
   $ pip install -r requirements.txt
```

3. Run the main social distancing detector file. (set display to 1 if you want to see output video as processing occurs)
```bash
   $ python3 social_distancing_detector.py --input pedestrians.mp4 --output output.avi --display
```

3.1. If you need more info, you can always run the help flag.
```bash
   $ python3 social_distancing_detector.py -h
```

## Usage 

 - YOLO COCO weights\
The weight file exceeds the github limits but can be download from <a href="https://pjreddie.com/media/files/yolov3.weights">here</a>.\
Add the weight file to the yolo-coco folder.

 - GPU **(Highly Recommended)**\
Provided you already have OpenCV installed with NVIDIA GPU support, all you need to do is set ```USE_GPU=True``` in your ```config.py``` file.

   - [Installation for windos of OpenCV with Cuda Support](https://youtu.be/YsmhKar8oOc)

## Demo :movie_camera:
![raw-vid](res/demo0.gif "Unprocessed video") ![processed-vid](res/demo1.gif "Processed video")


## License :key:

MIT &copy; Jesus Omar Cuenca Espino

### Original Repository and License

MIT &copy; Gadri Ebenezer

[Original Repository](https://github.com/aibenStunner/social-distancing-detector)