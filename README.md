# 🐍 Gesture Controlled Snake Game

A modern take on the classic Nokia Snake game, powered by real-time hand gesture recognition using computer vision.
Control the snake using your **index finger movements** via webcam—no keyboard required!
---

## 🚀 Features

* ✋ **Gesture-Based Controls**

  * Move your finger in 4 directions (UP, DOWN, LEFT, RIGHT)
  * Center position keeps the snake moving straight

* 🎯 **Smooth & Stable Tracking**

  * Noise reduction using position averaging
  * Dead zone to prevent accidental moves
  * Stable direction switching logic

* 🐍 **Classic Snake Gameplay**

  * Grid-based movement
  * Score tracking
  * Collision detection (walls & self)

* 🐢 **Beginner-Friendly Speed**

  * Slower snake movement for better control
  * Ideal for gesture-based gameplay

* 🎨 **Clean UI**

  * Minimal design
  * Smooth animations
  * Real-time camera feedback

---

## 🧠 Tech Stack

* Python
* OpenCV (for webcam input)
* MediaPipe (for hand tracking)
* Pygame (for game rendering)
* NumPy

---

## 📦 Installation

### Option 1: Automatic Setup

Run the setup script:

```bash
python setup.py
```

### Option 2: Manual Installation

Install dependencies manually:

```bash
pip install -r requirements.txt
```

---

## ▶️ How to Run

```bash
python main.py
```

---

## 🎮 Controls

### ✋ Gesture Controls

* Move finger **UP** → Snake moves up
* Move finger **DOWN** → Snake moves down
* Move finger **LEFT** → Snake moves left
* Move finger **RIGHT** → Snake moves right
* Keep finger in center → Continue straight

### ⌨️ Keyboard Controls

* `R` → Restart game
* `ESC` → Quit game
* `Q` → Quit camera window

---

## 📁 Project Structure

```
gesture-snake-game/
│
├── main.py                 # Main game loop + threading
├── snake_game.py          # Snake game logic (Pygame)
├── gesture_controller.py  # Hand tracking & gesture detection
├── setup.py               # Dependency installer
├── requirements.txt       # Required packages
└── README.md              # Project documentation
```

---

## ⚙️ Requirements

* Python 3.8+
* Webcam (required for gesture control)

---

## 💡 How It Works

1. Webcam captures live video using OpenCV
2. MediaPipe detects hand landmarks
3. Index fingertip position is tracked
4. Screen divided into directional zones
5. Snake moves based on finger position

---

## 👨‍💻 Connect with Me

Feel free to reach out for collaborations, projects, or just a chat!

* 📧 Email: **[rprasoon11@gmail.com](mailto:rprasoon11@gmail.com)**
* 💼 LinkedIn: **https://linkedin.com/in/prasoon-ranjan-2049572b0**

---

## 🤝 Contributing

Feel free to fork this repo and improve it!

---

## ⭐ Show Your Support

If you like this project, give it a ⭐ on GitHub!

---