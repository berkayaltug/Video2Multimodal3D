# pipeline/pose_utils.py
import os
import json
import cv2
import numpy as np
from PIL import Image
import time
import re

POSE_MERGED_JSON = False
CAPTION_MERGED_JSON = False
TAGS_MERGED_JSON = False

CAPTION_DELETE_AFTER_MERGE = False  # ← sadece True yaparsan siler
POSE_DELETE_AFTER_MERGE = False  # ← sadece True yaparsan siler
TAGS_DELETE_AFTER_MERGE = False  # ← sadece True yaparsan siler

# COCO_CONNECTIONS = [
#     (0, 1),  # Nose → Left Eye
#     (0, 2),  # Nose → Right Eye
#     (1, 3),  # Left Eye → Left Ear
#     (2, 4),  # Right Eye → Right Ear
#     (0, 5),  # Nose → Left Shoulder
#     (0, 6),  # Nose → Right Shoulder
#     (5, 7),  # Left Shoulder → Left Elbow
#     (7, 9),  # Left Elbow → Left Wrist
#     (6, 8),  # Right Shoulder → Right Elbow
#     (8, 10), # Right Elbow → Right Wrist
#     (5, 6),  # Left Shoulder → Right Shoulder (omuz çizgisi)
#     (5, 11), # Left Shoulder → Left Hip
#     (6, 12), # Right Shoulder → Right Hip
#     (11, 12),# Left Hip → Right Hip (kalça çizgisi)
#     (11, 13),# Left Hip → Left Knee
#     (13, 15),# Left Knee → Left Ankle
#     (12, 14),# Right Hip → Right Knee
#     (14, 16) # Right Knee → Right Ankle
# ]
COCO_CONNECTIONS = {
    "head":     {"links": [(0,1), (0,2), (1,3), (2,4)],        "color": (0, 255, 0)},   # Yeşil
    "shoulders":{"links": [(5,6)],                             "color": (255, 255, 0)}, # Sarı
    "left_arm": {"links": [(5,7), (7,9)],                      "color": (255, 165, 0)}, # Turuncu
    "right_arm":{"links": [(6,8), (8,10)],                     "color": (255, 165, 0)}, # Turuncu
    "torso":    {"links": [(5,11), (6,12), (11,12)],           "color": (0, 128, 255)}, # Mavi
    "left_leg": {"links": [(11,13), (13,15)],                  "color": (128, 0, 255)}, # Mor
    "right_leg":{"links": [(12,14), (14,16)],                  "color": (128, 0, 255)}  # Mor
}

def draw_keypoints_grouped(image_pil: Image.Image, keypoints: np.ndarray) -> Image.Image:
    """
    YOLOv8 pose keypoint sonuçlarını (17x3) içeren bir tensörü kullanarak,
    COCO bağlantılarına göre çizim yapan fonksiyon.
    """
    image = np.array(image_pil.convert("RGB"))  # PIL → NumPy RGB
    for group_name, group_data in COCO_CONNECTIONS.items():
        color = group_data["color"]
        links = group_data["links"]
        for start_idx, end_idx in links:
            x1, y1, c1 = keypoints[start_idx]
            x2, y2, c2 = keypoints[end_idx]
            if c1 > 0.3 and c2 > 0.3:  # güven skoru düşük olanları atla
                pt1 = (int(x1), int(y1))
                pt2 = (int(x2), int(y2))
                cv2.line(image, pt1, pt2, color=color, thickness=3, lineType=cv2.LINE_AA)

    # İsteğe bağlı: keypoint noktalarını da çiz
    for x, y, conf in keypoints:
        if conf > 0.3:
            cv2.circle(image, (int(x), int(y)), radius=4, color=(255, 255, 255), thickness=-1)

    return Image.fromarray(image)

# === RGBA Oluşturma Fonksiyonu ===
def create_rgba_image(rgb_img_pil, mask_pil):
    """
    rgb_img_pil: PIL.Image in RGB mode
    mask_pil: PIL.Image in mode 'L' or '1' (binary mask)
    Returns: PIL.Image in RGBA mode
    """
    # Mask kanalını normalize et (0 veya 255 olsun)
    mask_pil = mask_pil.convert("L").point(lambda x: 255 if x > 127 else 0)

    # RGBA birleştir
    rgba_img = rgb_img_pil.convert("RGBA")
    rgba_img.putalpha(mask_pil)

    return rgba_img

# === Pose Image Filter ===
def apply_warm_filter(image: Image.Image) -> Image.Image:
    # 1. RGB array'e dönüştür
    img_np = np.array(image).astype(np.float32)

    # 2. Kanal ağırlıklarını ayarla (sarımsı efekt için)
    r = np.clip(img_np[..., 0] * 1.35, 0, 255)
    g = np.clip(img_np[..., 1] * 1.15, 0, 255)
    b = np.clip(img_np[..., 2] * 0.75, 0, 255)

    # 3. Birleştir
    warm_np = np.stack([r, g, b], axis=-1).astype(np.uint8)

    # 4. RGBA varsa alpha'yı koru
    if image.mode == "RGBA":
        alpha = np.array(image)[..., 3:4]
        warm_np = np.concatenate([warm_np, alpha], axis=-1)

    return Image.fromarray(warm_np, mode=image.mode)

# === Yolo Pose Merged Json ===
def pose_merged_json(POSE_JSON_DIR="output_layers/pose_json", target_filename="merged_pose.json"):
    if not POSE_MERGED_JSON:
       # print("\033[96m[!]\033[0m → [Pose json birleştirme devre dışı, \033[96mişlem atlandı.\033[0m]")
        return
    print("===> Tüm pose keypoint JSON dosyaları birleştiriliyor...")
    merged_path = os.path.join(POSE_JSON_DIR, target_filename)
    
    # Bütün JSON dosyalarını birleştirmek için liste
    merged_data = []
    to_remove = []

    # Her bir _pose.json dosyasını sırayla oku
    for file in sorted(os.listdir(POSE_JSON_DIR)):
        if file.endswith("_pose.json") and file != "merged_pose.json":
            file_path = os.path.join(POSE_JSON_DIR, file)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    merged_data.append(data)
                    to_remove.append(file_path)
            except Exception as e:
                print(f"\033[91m[HATA]\033[0m {file} birleşiminde hata: {e}")

    # Birleştirilmiş veriyi yeni dosyaya yaz
    try:        
        with open(merged_path, 'w') as f:
            json.dump(merged_data, f, indent=4)
        print(f"\033[32m[✓]\033[0m{target_filename} → JSON birleştirme tamamlandı.")
                
        if not POSE_DELETE_AFTER_MERGE:
        # Diğer JSON dosyalarını sil
            for path in to_remove:
                if path != merged_path:
                    os.remove(path)
                    #print(f"[✓] {len(to_remove)} dosya silindi, yalnızca {merged_filename} kaldı.")
                    return
                print(f"\033[91m[HATA]\033[0m pose_merged.json yazılırken hata oluştu: {e}")
    except Exception as e:
        print(f"\033[91m[HATA]\033[0m {file} birleşiminde hata: {e}")
        
# === WaifuDiffusion Tags Merged JSON ===
def merge_tags_json_files(tags_json_dir="output_layers/tags", target_filename="merged_tags.json"):
    if not TAGS_MERGED_JSON:
       # print("\033[96m[!]\033[0m → [Tags json birleştirme devre dışı, \033[96mişlem atlandı.\033[0m]")
        return
    #######################################################################
    target_filename = "merged_tags.json"
    target_path = os.path.join(tags_json_dir, target_filename)

    if os.path.exists(target_path):
        print(f"\033[96m[!]\033[0m '{target_filename}' \033[96mzaten mevcut. Bu adım atlanıyor.\033[0m")
        return
    else:
        print(f"\033[33m[!]\033[0m '{target_filename}' \033[33mbulunamadı, işlem başlatılıyor...\033[0m")
    #######################################################################
    print("===> Tüm WaifuDiffusion Tag JSON dosyaları birleştiriliyor...")
    merged_path = os.path.join(tags_json_dir, target_filename)

    merged_data = []
    to_remove = []

    for file in sorted(os.listdir(tags_json_dir)):
        if file.endswith('_tags.json'):
            file_path = os.path.join(tags_json_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    merged_data.append(data)
                    to_remove.append(file_path)
            except Exception as e:
                print(f"\033[91m[HATA]\033[0m {file} birleştirilirken: {e}")

    try:
        with open(merged_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        print(f"[✓] {target_filename} → JSON birleştirme tamamlandı.")

        # Diğer JSON dosyalarını sil
    #     for path in to_remove:
    #         if path != merged_path:
    #             os.remove(path)
    #     #print(f"[✓] {len(to_remove)} dosya silindi, yalnızca {merged_filename} kaldı.")
    # except Exception as e:
    #     print(f"\033[91m[HATA]\033[0m JSON birleştirme işlemi sırasında: {e}")
        if not TAGS_DELETE_AFTER_MERGE:
            # Diğer JSON dosyalarını sil
                for path in to_remove:
                    if path != merged_path:
                        os.remove(path)
                        #print(f"[✓] {len(to_remove)} dosya silindi, yalnızca {merged_filename} kaldı.")
                        return
                    print(f"\033[91m[HATA]\033[0m merged_tags.json yazılırken hata oluştu: {e}")
    except Exception as e:
        print(f"\033[91m[HATA]\033[0m {file} birleşiminde hata: {e}")
    
    

# === BLIP Caption Merged JSON ===
def merge_caption_json_files():
    if not CAPTION_MERGED_JSON:
       # print("\033[96m[!]\033[0m → [Caption json birleştirme devre dışı, \033[96mişlem atlandı.\033[0m]")
        return
    CAPTION_DIR = "output_layers/captions"
    #######################################################################
    target_filename = "merged_captions.json"
    target_path = os.path.join(CAPTION_DIR, target_filename)

    if os.path.exists(target_path):
        print(f"\033[96m[!]\033[0m '{target_filename}' \033[96mzaten mevcut. Bu adım atlanıyor.\033[0m")
        return
    else:
        print(f"\033[33m[!]\033[0m '{target_filename}' \033[33mbulunamadı, işlem başlatılıyor...\033[0m")
    #######################################################################
    print("===> Tüm caption JSON dosyaları birleştiriliyor...")
    merged_data = []
    # 1. Verileri oku ve birleştir
    caption_files = sorted([
        f for f in os.listdir(CAPTION_DIR)
        if f.endswith('_caption.json') and f != "merged_captions.json"
    ])

    for file in caption_files:
        file_path = os.path.join(CAPTION_DIR, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    merged_data.append(data)
                elif isinstance(data, list):
                    merged_data.extend(data)
                else:
                    print(f"[UYARI] {file} → JSON formatı beklenmedik: {type(data)}")

        except Exception as e:
            print(f"\033[91m[HATA]\033[0m {file} okuma sırasında: {e}")

    # 2. Merged dosyayı kaydet
    merged_path = os.path.join(CAPTION_DIR, "merged_captions.json")
    try:
        with open(merged_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=4)
        print(f"\033[32m[✓]\033[0m {merged_path} oluşturuldu → {len(merged_data)} caption içeriyor.")
    except Exception as e:
        print(f"\033[91m[HATA]\033[0m {merged_path} yazılamadı: {e}")

    if CAPTION_DELETE_AFTER_MERGE:
        for file in caption_files:
        
        # İsteğe bağlı olarak geçici caption dosyalarını sil
            for file in os.listdir(CAPTION_DIR):
                if file.endswith('_caption.json') and file != "merged_captions.json":
                    try:
                        os.remove(os.path.join(CAPTION_DIR, file))
                    except Exception as e:
                        print(f"\033[91m[HATA]\033[0m {file} silinemedi: {e}")

