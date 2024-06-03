import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np
from googletrans import Translator
import cv2

def analyze_image(image_path):
    model = MobileNetV2(weights='imagenet')
    img = image.load_img(image_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    results = decode_predictions(preds, top=3)[0]
    
    translator = Translator()
    result_texts = []
    for (imagenet_id, desc, prob) in results:
        desc_ko = translator.translate(desc, src='en', dest='ko').text
        result_texts.append(f"{desc_ko}: {round(prob * 100, 2)}%")
    
    result_text = ', '.join(result_texts)
    return result_text

def compare_images(image1_path, image2_path):
    image1 = cv2.imread(os.path.join('uploads', image1_path))
    image2 = cv2.imread(os.path.join('uploads', image2_path))

    if image1.shape != image2.shape:
        raise ValueError("Images must have the same dimensions for comparison")

    diff = cv2.absdiff(image1, image2)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(diff_gray, 30, 255, cv2.THRESH_BINARY)
    diff_image_path = 'uploads/diff.png'
    cv2.imwrite(diff_image_path, thresh)

    return 'diff.png'
