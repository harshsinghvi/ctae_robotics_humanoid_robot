import face_recognition
import pickle
import numpy as np
all_face_encodings = {}


img1 = face_recognition.load_image_file("kalpana jain.jpeg")
all_face_encodings["Kalpana Jain"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("naveen choudhary.jpeg")
all_face_encodings["Doctor Naveen Choudhary"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("navneet agarwal.jpeg")
all_face_encodings["Doctor Navneet Agarwal"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("sunil joshi.jpeg")
all_face_encodings["Doctor Sunil Joshi"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("ajay sharma.jpeg")
all_face_encodings["Doctor Ajay Sharma"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("anupam bhatnakar.jpeg")
all_face_encodings["Doctor Anupam Bhatnakar"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("b l salvi.jpeg")
all_face_encodings["Doctor B L Salvi"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("chitranjan agarwal.jpeg")
all_face_encodings["Doctor Chitranjan Agarwal"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("jai kumar.jpeg")
all_face_encodings["Doctor Jai Kumar Meharchandani"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("manjeet singh.jpeg")
all_face_encodings["Manjeet Singh"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("narendra rathore.jpeg")
all_face_encodings["Doctor Narendra Singh Rathore"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("naveen jain.jpeg")
all_face_encodings["Doctor Naveen Jain"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("p k singh.jpeg")
all_face_encodings["Doctor P K Singh"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("ranveer singh.jpeg")
all_face_encodings["Ranveer Singh"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("s r bhakar.jpeg")
all_face_encodings["Doctor S R Bhakar"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("vinod yadav.jpeg")
all_face_encodings["Doctor Vinod Yadav"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("virendra singh solanki.jpeg")
all_face_encodings["Doctor Virendra Singh Solanki"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("narendra rathore1.jpeg")
all_face_encodings["Doctor Narendra Singh Rathore"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("narendra rathore2.jpeg")
all_face_encodings["Doctor Narendra Singh Rathore"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("sunil joshi1.jpeg")
all_face_encodings["Doctor Sunil Joshi"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("naveen jain1.jpeg")
all_face_encodings["Doctor Naveen Jain"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("vikramaditya dave.jpeg")
all_face_encodings["Doctor vikramaditya dave"] = face_recognition.face_encodings(img1)[0]
img1 = face_recognition.load_image_file("sunil joshi2.jpeg")
all_face_encodings["Doctor Sunil Joshi"] = face_recognition.face_encodings(img1)[0]

with open('dataset_faces.dat', 'wb') as f:
    pickle.dump(all_face_encodings, f)
with open('dataset_faces.dat', 'rb') as f:
    all_face_encodings = pickle.load(f)
# Load a sample picture and learn how to recognize it.
known_face_names = list(all_face_encodings.keys())
known_face_encodings = np.array(list(all_face_encodings.values()))
#print(known_face_encodings)
print(known_face_names)
#print(all_face_encodings)
#all_face_encodings.pop("bhuvan3 SH")
'''
all_face_encodings.pop("Harshit")
all_face_encodings.pop("Papa")
all_face_encodings.pop("Harshit Agarwal")
#all_face_encodings.pop("Surbhi Agrawal")
print("******************")
print(all_face_encodings)
with open('dataset_faces.dat', 'wb') as f:
    pickle.dump(all_face_encodings, f)
'''
