"""VLC-based audio player for NeMusic."""
import time
import threading
import vlc


class Player:
    """Audio player wrapping VLC MediaPlayer."""

    def __init__(self):
        self._instance = vlc.Instance("--no-video")
        self._player = self._instance.media_player_new()
        self._callbacks = {
            "on_position_change": None,
            "on_state_change": None,
            "on_song_end": None,
            "on_error": None,
        }
        self._current_url = None
        self._current_song = None
        self._position_timer = None
        self._running = False

    def set_callback(self, name, func):
        if name in self._callbacks:
            self._callbacks[name] = func

    def play(self, url, song_info=None):
        self._current_url = url
        self._current_song = song_info or {}
        self._running = True

        media = self._instance.media_new(url)
        self._player.set_media(media)
        self._player.play()

        self._start_position_timer()
        self._notify_state("playing")

    def pause(self):
        self._player.pause()
        self._notify_state("paused")

    def resume(self):
        self._player.play()
        self._notify_state("playing")

    def toggle_play_pause(self):
        if self._player.is_playing():
            self.pause()
        else:
            self.resume()

    def stop(self):
        self._running = False
        self._stop_position_timer()
        self._player.stop()

    def seek(self, position_sec):
        self._player.set_time(int(position_sec * 1000))

    def set_volume(self, volume):
        self._player.audio_set_volume(int(volume))

    def get_volume(self):
        return self._player.audio_get_volume()

    def get_position(self):
        current_ms = self._player.get_time()
        total_ms = self._player.get_length()
        current = current_ms / 1000.0 if current_ms > 0 else 0
        total = total_ms / 1000.0 if total_ms > 0 else 0
        return current, total

    def get_current_song(self):
        return self._current_song

    def is_playing(self):
        return self._player.is_playing() == 1

    def _start_position_timer(self):
        self._stop_position_timer()
        self._position_timer = threading.Thread(
            target=self._position_loop, daemon=True
        )
        self._position_timer.start()

    def _stop_position_timer(self):
        if self._position_timer and self._position_timer.is_alive():
            self._position_timer = None

    def _position_loop(self):
        last_pos = -1
        while self._running:
            time.sleep(0.5)
            if not self._running:
                break

            current, total = self.get_position()
            curr_int = int(current)

            if curr_int != last_pos and self._callbacks["on_position_change"]:
                last_pos = curr_int
                pct = (current / total * 100) if total > 0 else 0
                try:
                    self._callbacks["on_position_change"](
                        current_sec=current, total_sec=total, percentage=pct
                    )
                except Exception:
                    pass

            if not self.is_playing() and current > 1 and total > 0:
                self._running = False
                if self._callbacks["on_song_end"]:
                    try:
                        self._callbacks["on_song_end"]()
                    except Exception:
                        pass
                break

    def _notify_state(self, state):
        if self._callbacks["on_state_change"]:
            try:
                self._callbacks["on_state_change"](state=state)
            except Exception:
                pass

    def _notify_error(self, code, message):
        if self._callbacks["on_error"]:
            try:
                self._callbacks["on_error"](code=code, message=message)
            except Exception:
                pass

    def destroy(self):
        self._running = False
        self._stop_position_timer()
        self._player.stop()
        self._player.release()
        self._instance.release()
