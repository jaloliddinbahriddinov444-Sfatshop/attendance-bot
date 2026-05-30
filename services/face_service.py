"""Yuz tanish va kodlash xizmati"""
import io
import pickle
import logging
from typing import Optional, Tuple

import face_recognition
import numpy as np
from PIL import Image, ImageOps

from config import FACE_MATCH_TOLERANCE

logger = logging.getLogger(__name__)


def encode_face_from_bytes(image_bytes: bytes) -> Tuple[Optional[bytes], str]:
    """
    Rasm baytlaridan yuz kodini chiqaradi.
    Qaytaradi: (encoding_bytes, error_message)
    Muvaffaqiyatli bo'lsa error_message = ""
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        # EXIF orientation yorlig'ini qo'llash (iPhone selfilarida muhim)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        # Juda katta rasmlarni kichraytirish (tezlik uchun)
        if max(img.size) > 1200:
            img.thumbnail((1200, 1200), Image.LANCZOS)
        img_array = np.array(img)
    except Exception as e:
        logger.exception("Image load failed")
        return None, f"Rasmni o'qib bo'lmadi: {e}"

    # Yuzlarni topish
    face_locations = face_recognition.face_locations(img_array, model="hog")

    if len(face_locations) == 0:
        return None, "no_face"
    if len(face_locations) > 1:
        return None, "multiple_faces"

    encodings = face_recognition.face_encodings(img_array, face_locations)
    if not encodings:
        return None, "no_face"

    # numpy array ni baytlarga aylantiramiz (SQLite ga saqlash uchun)
    return pickle.dumps(encodings[0]), ""


def compare_faces(known_encoding_bytes: bytes, image_bytes: bytes) -> Tuple[bool, float, str]:
    """
    Saqlangan yuz kodi bilan yangi rasmni solishtiradi.
    Qaytaradi: (mos_keladi, mosllik_darajasi_0_1, error)
    """
    try:
        known = pickle.loads(known_encoding_bytes)
    except Exception as e:
        return False, 0.0, f"Saqlangan yuz kodini o'qib bo'lmadi: {e}"

    new_encoding, err = encode_face_from_bytes(image_bytes)
    if err == "no_face":
        return False, 0.0, "no_face"
    if err == "multiple_faces":
        return False, 0.0, "multiple_faces"
    if err:
        return False, 0.0, err

    new_arr = pickle.loads(new_encoding)
    # face_distance: 0 = aynan o'xshash, 1 = umuman boshqa
    distance = float(face_recognition.face_distance([known], new_arr)[0])
    # Mosllik darajasini foizga aylantiramiz (yaqinroq = balandroq foiz)
    similarity = max(0.0, 1.0 - distance)
    is_match = distance <= FACE_MATCH_TOLERANCE
    return is_match, similarity, ""
