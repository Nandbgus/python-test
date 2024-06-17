import cv2
import numpy as np
import mediapipe as mp

# Inisialisasi Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Variabel untuk kanvas
canvas = None

# Warna dan ukuran brush
brush_color = (255, 255, 255)
brush_size = 5
remove_brush = 20

# Status menggambar dan mode
drawing = False
erase_mode = False

# Variabel untuk smoothing
previous_point = None
smoothing_factor = 0.5

# Fungsi untuk menghitung jarak antara dua titik
def distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

# Fungsi untuk mendeteksi tangan dan menggambar di kanvas
def draw_on_canvas(image, results):
    global canvas, drawing, previous_point, erase_mode

    # Buat kanvas jika belum ada
    if canvas is None:
        canvas = np.zeros_like(image)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Ambil koordinat landmark ujung jari
            middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            h, w, _ = image.shape
            middle_point = (int(middle_finger_tip.x * w), int(middle_finger_tip.y * h))
            index_point = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))
            thumb_point = (int(thumb_tip.x * w), int(thumb_tip.y * h))

            # Hitung jarak antara jari tengah dan jari telunjuk
            distance_middle_index = distance(middle_point, index_point)

            # Hitung jarak antara jari jempol dan jari telunjuk
            distance_thumb_index = distance(thumb_point, index_point)

            # Tentukan mode berdasarkan jarak
            if distance_middle_index < 50:  # Threshold untuk mode hapus
                erase_mode = True
                drawing = True
            elif distance_thumb_index < 50:  # Threshold untuk mode menggambar
                erase_mode = False
                drawing = True
            else:
                drawing = False

            if drawing:
                if not erase_mode:
                    # Menggambar dengan smoothing
                    current_point = index_point
                    if previous_point is not None:
                        smoothed_point = (
                            int(previous_point[0] * (1 - smoothing_factor) + current_point[0] * smoothing_factor),
                            int(previous_point[1] * (1 - smoothing_factor) + current_point[1] * smoothing_factor)
                        )
                        cv2.line(image, previous_point, smoothed_point, brush_color, brush_size)
                        cv2.line(canvas, previous_point, smoothed_point, brush_color, brush_size)
                        # Menambahkan dot biru pada posisi saat ini
                        cv2.circle(image, current_point, brush_size // 2, (255, 0, 0), -1)
                        cv2.circle(canvas, current_point, brush_size // 2, (255, 0, 0), -1)
                    previous_point = current_point
                else:
                    # Mode hapus
                    cv2.circle(canvas, index_point, remove_brush, (0, 0, 0), -1)
                    previous_point = None

            # Gambarkan garis antara titik-titik (untuk debugging)
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    return image

def main():
    global drawing

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        # Membalik gambar untuk tampilan seperti cermin
        image = cv2.flip(image, 1)

        # Konversi warna BGR ke RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Proses deteksi tangan
        results = hands.process(image_rgb)

        # Gambarkan di kanvas
        image = draw_on_canvas(image, results)

        # Gabungkan gambar asli dengan kanvas
        combined_image = cv2.addWeighted(image, 0.5, canvas, 0.5, 0)

        # Tampilkan gambar
        cv2.imshow('Air Canvas', combined_image)

        # Keluar saat menekan tombol 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
