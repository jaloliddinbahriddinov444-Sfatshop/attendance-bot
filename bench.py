import time, numpy as np
import face_recognition
from face_recognition.api import face_encoder, pose_predictor_68_point
import dlib

# 1) HOG yuz topish — turli oʻlchamlarda
for sz in (1200, 800, 640, 480):
    img = (np.random.rand(sz, sz, 3)*255).astype(np.uint8)
    t = time.time()
    face_recognition.face_locations(img, model="hog")
    print(f"HOG detect {sz}x{sz}: {time.time()-t:.2f}s")

# 2) ResNet yuz kodlash (150x150 chip, asosiy ogʻir qism)
img = (np.random.rand(150,150,3)*255).astype(np.uint8)
rect = dlib.rectangle(0,0,150,150)
shape = pose_predictor_68_point(img, rect)
t = time.time()
n = 3
for _ in range(n):
    face_encoder.compute_face_descriptor(img, shape)
print(f"ResNet encode (1 yuz): {(time.time()-t)/n:.2f}s  <-- asosiy")
