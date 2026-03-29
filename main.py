"""
Main entry point for the gesture-controlled snake game
Combines the existing snake game with webcam finger tracking
"""

import threading
import time

import cv2
import pygame

from gesture_controller import GestureController
from snake_game import SnakeGame


class GameManager:
    def __init__(self):
        """Initialize the game manager."""
        self.game = SnakeGame()
        self.gesture_controller = GestureController()
        self.cap = None
        self.running = True
        self.gesture_thread = None
        self.current_gesture = None
        self.frame_lock = threading.Lock()

    def initialize_camera(self):
        """Initialize the webcam."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return True

    def gesture_detection_loop(self):
        """Run hand tracking in a separate thread to keep the game responsive."""
        while self.running and self.cap is not None:
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            gesture, annotated_frame = self.gesture_controller.detect_gestures(frame)

            with self.frame_lock:
                self.current_gesture = gesture

            cv2.imshow("Gesture Snake - Camera", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.running = False
                break

            # Small sleep helps keep tracking smooth without wasting CPU.
            time.sleep(0.01)

    def run(self):
        """Run the game with slow, fixed-interval snake updates."""
        if not self.initialize_camera():
            print("Failed to initialize camera. Exiting...")
            return

        self.gesture_thread = threading.Thread(target=self.gesture_detection_loop, daemon=True)
        self.gesture_thread.start()

        print("Gesture Snake started")
        print("Move your index finger into the top, bottom, left, or right zone")
        print("Keep your finger near the center to continue straight")
        print("Press R to restart or ESC to quit")

        accumulator = 0.0
        previous_time = time.perf_counter()

        while self.running:
            current_time = time.perf_counter()
            delta_time = current_time - previous_time
            previous_time = current_time
            accumulator += min(delta_time, 0.1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.game.reset_game()
                        self.gesture_controller.reset_gesture_state()

            with self.frame_lock:
                current_gesture = self.current_gesture

            if current_gesture:
                self.game.change_direction(current_gesture)

            while accumulator >= self.game.get_update_interval():
                self.game.update()
                accumulator -= self.game.get_update_interval()

            self.game.draw()
            self.game.clock.tick(60)

        self.cleanup()

    def cleanup(self):
        """Release resources."""
        self.running = False

        if self.cap is not None:
            self.cap.release()

        cv2.destroyAllWindows()
        self.game.quit()

        if self.gesture_thread and self.gesture_thread.is_alive():
            self.gesture_thread.join(timeout=1.0)


def main():
    """Main function."""
    try:
        game_manager = GameManager()
        game_manager.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as exc:
        print(f"An error occurred: {exc}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
