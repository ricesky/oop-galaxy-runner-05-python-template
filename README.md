# oop-galaxy-runner-python

## Capaian Pembelajaran

Setelah menyelesaikan seluruh tahapan, mahasiswa diharapkan mampu:

1. Memodelkan permainan 2D sederhana menggunakan **pemrograman berorientasi objek** (class, object, composition, encapsulation, inheritance, polymorphism) di Python.
2. Menggunakan **PyGame** untuk membangun game 2D dengan beberapa komponen: player, musuh (enemy), background, skor, dan UI dasar.
3. Menerapkan **multimedia** (gambar, sprite animation, suara) di dalam game.
4. Mengelola **beberapa screen** (main menu, game screen, high score) menggunakan Screen Manager berbasis OOP.
5. Menerapkan **perilaku AI sederhana** pada musuh (enemy) dan mengatur tingkat kesulitan permainan.

---

## Lingkungan Pengembangan

1. Platform: Python **3.12+** (boleh 3.13 selama PyGame berjalan)
2. Bahasa: Python
3. Editor/IDE yang disarankan:

   * VS Code + Python Extension
   * Terminal
4. Library:

   * `pygame 2.6.1`
   * `pytest`

---

## Cara Menjalankan Project

```bash
python -m src.main
```

---

# Tahap 5 — High Score Persistence + Simple Enemy AI

**Tujuan Tahap 5**

1. Mahasiswa memahami cara:

   * menyimpan & membaca **high score** dari file (JSON),
   * menampilkan high score di `HighScoreScreen`.
2. Mahasiswa melihat contoh **AI sederhana** di game:

   * musuh yang bergerak mendekati posisi player.

---

## 0. Struktur Folder Baru (Data High Score)

Kita tambahkan satu folder baru untuk menyimpan high score:

```text
assets/
├─ images/
├─ sounds/
└─ data/
   └─ high_scores.json      # akan dibuat otomatis saat runtime
```

Dan satu file Python baru:

```text
src/
└─ core/
   └─ high_scores.py
```

---

## 1. HighScoreManager — Menyimpan & Membaca High Score

### 1.1. Buat `core/high_scores.py`

**File baru:** `src/core/high_scores.py`

Isinya:

```python
import os
import json
from typing import List, Dict, Any


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(ASSETS_DIR, "data")
HIGH_SCORE_PATH = os.path.join(DATA_DIR, "high_scores.json")


class HighScoreManager:
    def __init__(self, max_entries: int = 10):
        self.max_entries = max_entries
        os.makedirs(DATA_DIR, exist_ok=True)
        self.scores: List[Dict[str, Any]] = self._load_scores()

    def _load_scores(self) -> List[Dict[str, Any]]:
        if not os.path.exists(HIGH_SCORE_PATH):
            return []
        try:
            with open(HIGH_SCORE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass
        return []

    def _save_scores(self):
        with open(HIGH_SCORE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=2)

    def add_score(self, name: str, score: int):
        self.scores.append({"name": name, "score": int(score)})
        # Urutkan dari score terbesar ke terkecil
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        # Batasi jumlah entri
        self.scores = self.scores[: self.max_entries]
        self._save_scores()

    def get_top_scores(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.scores[:limit]
```

Ini sudah cukup untuk:

* pertama kali jalan → file belum ada → list kosong
* setelah game selesai → kita `add_score(...)` → file JSON tersimpan

---

## 2. Integrasi High Score dengan Game & Screen

Kita ingin alur seperti ini:

1. Player bermain di **GameScreen**.
2. Ketika **player kehabisan nyawa**:

   * tandai `game_over = True`,
   * simpan skor ke high score,
   * pindah ke **HighScoreScreen**, menampilkan skor terakhir dan daftar top scores.

---

### 2.1. Tambahkan flag `game_over` ke `Game`

**File:** `src/core/game.py`

#### a) Tambah atribut `game_over` di `__init__`

Di dalam `Game.__init__`, setelah inisialisasi player:

```python
        self.player = Player(
            x=screen_width / 2,
            y=screen_height - 60,
            speed=300,
            screen_width=screen_width,
            lives=3,
        )

        self.game_over = False
```

#### b) Update `update()` supaya cek game over

Di method `update(self, dt: float)`, setelah:

```python
        self.starfield.update(dt)
        self.player.update(dt)

        for enemy in self.enemies:
            enemy.update(dt, self.player.x)
            if enemy.is_off_screen():
                enemy.reset()
                self.player.add_score(10)
                self.score_sound.play()

        self._check_collisions()
```

Tambahkan:

```python
        if self.player.is_dead():
            self.game_over = True
```

---

### 2.2. GameScreen: simpan skor & pindah ke HighScoreScreen

**File:** `src/screens/game_screen.py`

#### a) Import `HighScoreManager`

Di bagian import paling atas:

```python
from ..core.game import Game
from ..ui.button import Button
from ..core.high_scores import HighScoreManager
```

#### b) Inisialisasi HighScoreManager di `__init__`

Di `__init__` `GameScreen`, tambahkan:

```python
        self.high_score_manager = HighScoreManager()
        self._handled_game_over = False
```

#### c) Cek game_over di `update()`

Di method `update(self, dt: float)`:

Sebelumnya:

```python
    def update(self, dt: float):
        self.game.update(dt)
```

Ubah menjadi:

```python
    def update(self, dt: float):
        self.game.update(dt)

        if self.game.game_over and not self._handled_game_over:
            self._handled_game_over = True

            final_score = self.game.player.score

            # Untuk sementara, nama pemain kita isi default "PLAYER"
            self.high_score_manager.add_score("PLAYER", final_score)

            from .high_score import HighScoreScreen
            new_screen = HighScoreScreen(
                self.manager,
                self.screen_width,
                self.screen_height,
                recent_score=final_score,
            )
            self.manager.switch_to(new_screen)
```

> `self._handled_game_over` mencegah kode dipanggil berkali-kali (loop 60 FPS).

---

### 2.3. HighScoreScreen: Tampilkan High Score dari File

**File:** `src/screens/high_score.py`

#### a) Ubah `__init__` agar menerima `recent_score`

Ubah signature constructor:

```python
from ..core.high_scores import HighScoreManager
```

Lalu di class:

```python
class HighScoreScreen(BaseScreen):
    def __init__(self, manager, screen_width: int, screen_height: int, recent_score: int | None = None):
        super().__init__(manager, screen_width, screen_height)

        self.background_color = (20, 10, 40)
        self.title_font = pygame.font.SysFont(None, 48)
        self.text_font = pygame.font.SysFont(None, 28)

        self.back_button = Button(
            pygame.Rect(20, screen_height - 70, 160, 40),
            "Back to Menu",
            self.text_font,
        )

        self.recent_score = recent_score
        self.high_score_manager = HighScoreManager()
```

> Kita tidak lagi pakai `self.dummy_scores`.

#### b) Ubah `draw()` untuk menampilkan skor asli

Ganti isi `draw()` kurang-lebih seperti ini:

```python
    def draw(self, surface: pygame.Surface):
        surface.fill(self.background_color)

        # Judul
        title_surf = self.title_font.render("High Scores", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 60))
        surface.blit(title_surf, title_rect)

        y = 120

        # Jika ada skor terbaru, tampilkan di atas
        if self.recent_score is not None:
            recent_text = f"Last run score: {self.recent_score}"
            recent_surf = self.text_font.render(recent_text, True, (200, 220, 255))
            recent_rect = recent_surf.get_rect(center=(self.screen_width // 2, y))
            surface.blit(recent_surf, recent_rect)
            y += 40

        # Tampilkan daftar high scores
        scores = self.high_score_manager.get_top_scores(limit=10)
        if scores:
            for idx, entry in enumerate(scores, start=1):
                line = f"{idx}. {entry['name']} - {entry['score']}"
                line_surf = self.text_font.render(line, True, (230, 230, 230))
                line_rect = line_surf.get_rect(center=(self.screen_width // 2, y))
                surface.blit(line_surf, line_rect)
                y += 30
        else:
            no_data = self.text_font.render("Belum ada high score.", True, (200, 200, 200))
            no_data_rect = no_data.get_rect(center=(self.screen_width // 2, y))
            surface.blit(no_data, no_data_rect)
            y += 30

        self.back_button.draw(surface)
```

Sekarang HighScoreScreen menampilkan:

* “Last run score: X”
* Daftar high score dari file `high_scores.json`.

---

## 3. Simple Enemy AI — SmartEnemy Mengikuti Player

Sekarang tambah elemen **AI sederhana**: sebagian musuh akan:

* jatuh ke bawah **+**
* sedikit bergeser ke kiri/kanan untuk mengejar posisi `x` player.

### 3.1. Ubah Enemy.update menerima `player_x`

**File:** `src/core/enemy.py`

Ubah signature `update`:

Sebelumnya kurang lebih:

```python
    def update(self, dt: float):
        self.y += self.speed * dt
```

Jadi:

```python
    def update(self, dt: float, player_x: float | None = None):
        self.y += self.speed * dt
        # Enemy biasa mengabaikan player_x (AI ada di subclass)
```

> Ini mempersiapkan polymorphism: subclass bisa memanfaatkan `player_x`.

---

### 3.2. Tambahkan SmartEnemy (subclass Enemy)

Masih di `enemy.py`, di bawah class `Enemy`, tambahkan:

```python
class SmartEnemy(Enemy):
    """
    Enemy dengan AI sederhana:
    - tetap jatuh ke bawah
    - tetapi x-nya bergerak pelan mendekati posisi player
    """

    def __init__(self, screen_width: int, screen_height: int, tracking_speed: float = 80.0):
        super().__init__(screen_width, screen_height)
        self.tracking_speed = tracking_speed

    def update(self, dt: float, player_x: float | None = None):
        # Tetap panggil update() parent untuk gerakan vertikal
        super().update(dt, player_x)

        if player_x is None:
            return

        # Gerakan horizontal menuju player_x
        if player_x < self.x:
            self.x -= self.tracking_speed * dt
        elif player_x > self.x:
            self.x += self.tracking_speed * dt
```

---

### 3.3. Gunakan kombinasi Enemy & SmartEnemy di Game

**File:** `src/core/game.py`

#### a) Import SmartEnemy

Di bagian import:

```python
from .enemy import Enemy, SmartEnemy
```

#### b) Modifikasi `_create_enemies()`

Cari method `_create_enemies` (yang membuat beberapa enemy):

Sebelum:

```python
    def _create_enemies(self):
        self.enemies.clear()
        for _ in range(self.enemy_count):
            self.enemies.append(Enemy(self.screen_width, self.screen_height))
```

Ubah jadi kombinasi:

```python
    def _create_enemies(self):
        self.enemies.clear()
        for i in range(self.enemy_count):
            if i < self.enemy_count - 2:
                # Sebagian besar enemy biasa (jatuh lurus)
                self.enemies.append(Enemy(self.screen_width, self.screen_height))
            else:
                # Dua enemy terakhir adalah SmartEnemy dengan AI sederhana
                self.enemies.append(SmartEnemy(self.screen_width, self.screen_height, tracking_speed=90.0))
```

#### c) Update loop di `update()` agar kirim `player_x`

Di method `update(self, dt: float)`, di loop enemy:

Sebelum:

```python
        for enemy in self.enemies:
            enemy.update(dt)

            if enemy.is_off_screen():
                enemy.reset()
                self.player.add_score(10)
                self.score_sound.play()
```

Ubah jadi:

```python
        for enemy in self.enemies:
            enemy.update(dt, self.player.x)

            if enemy.is_off_screen():
                enemy.reset()
                self.player.add_score(10)
                self.score_sound.play()
```

> Sekarang:
>
> * Enemy biasa: hanya jatuh lurus (mengabaikan `player_x`).
> * SmartEnemy: override `update` → bergerak horizontal menuju `player_x`.

---

## 4. Menjalankan Tahap 5

Jalankan seperti biasa:

```bash
python -m src.main
```

**Perilaku yang diharapkan:**

1. Main Menu muncul seperti Tahap 4.
2. Start Game → GameScreen:

   * musuh biasa jatuh lurus,
   * beberapa musuh “pintar” bergerak mengejar posisi player.
3. Saat nyawa habis:

   * game otomatis pindah ke HighScoreScreen,
   * skor terakhir muncul sebagai “Last run score”,
   * high_scores.json ter-update dan daftar high score tampil.
4. HighScoreScreen → Back to Menu → bisa main lagi, high score bertambah.

---

