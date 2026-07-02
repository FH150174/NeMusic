"""VLC-based audio player for NeMusic."""
import time
import threading
import vlc


class Player:
    """Audio player wrapping VLC MediaPlayer."""

    def __init__(self):
        self._instance = vlc.Instance("--no-video --network-caching=800")
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
        self._paused = False

    def set_callback(self, name, func):
        if name in self._callbacks:
            self._callbacks[name] = func

    def play(self, url, song_info=None):
        self._current_url = url
        self._current_song = song_info or {}
        self._running = True
        self._paused = False

        media = self._instance.media_new(url)
        self._player.set_media(media)
        self._player.play()

        self._start_position_timer()
        self._notify_state("playing")

    def pause(self):
        self._player.pause()
        self._paused = True
        self._notify_state("paused")

    def resume(self):
        self._player.play()
        self._paused = False
        self._notify_state("playing")

    def toggle_play_pause(self):
        if self._player.is_playing():
            self.pause()
        else:
            self.resume()

    def stop(self):
        self._running = False
        self._paused = False
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
        self._position_timer = None

    def _position_loop(self):
        last_pos = -1
        while self._running:
            time.sleep(0.3)
            if not self._running:
                break

            state = self._player.get_state()

            # Skip position check if paused (VLC returns stale position)
            if state == vlc.State.Paused:
                continue

            # Only check song-end when actually ended (not paused/stopped)
            if state == vlc.State.Ended:
                self._running = False
                if self._callbacks["on_song_end"]:
                    try:
                        self._callbacks["on_song_end"]()
                    except Exception:
                        pass
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

    # --- Playback state persistence ---

    def save_state(self):
        """Return dict with current playback state for later restore."""
        if self._current_song:
            current, total = self.get_position()
            return {
                "song": self._current_song,
                "position": current,
                "total": total,
                "paused": self._paused,
            }
        return {}

    def restore_state(self, state):
        """Restore playback from saved state. Returns True on success."""
        if not state or not state.get("song"):
            return False
        song = state["song"]
        pos = state.get("position", 0)
        self.play_song_state(song, pos)
        return True

    def play_song_state(self, song_info, position=0):
        """Special play that seeks to position after start. Used internally."""
        self._current_song = song_info or {}
        self._running = True
        self._paused = False

        url = self._current_url  # URL must be set externally

    # --- Playback state persistence ---
    def save_state_data(self):
        """Return dict with current playback state."""
        if not self._current_song:
            return None
        current, total = self.get_position()
        return {
            "song": self._current_song,
            "position": current,
            "total": total,
            "volume": self.get_volume(),
        }

    def restore_state_data(self, state):
        """Return (song_info, position, volume) from saved state."""
        if not state:
            return None, 0, 70
        return (
            state.get("song"),
            state.get("position", 0),
            state.get("volume", 70),
        )

    def destroy(self):
        self._running = False
        self._stop_position_timer()
        self._player.stop()
        self._player.release()
        self._instance.release()
