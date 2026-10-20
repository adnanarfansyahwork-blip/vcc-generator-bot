# VCC / Test Card Generator Telegram Bot (@myvccgen_bot)

Bot Telegram untuk generate nomor kartu virtual / test card (Luhn Algorithm) dengan format dan tampilan persis seperti pada tangkapan layar, dilengkapi proteksi **Force Subscription (FSub Gate)** dan info **Owner & Support**.

---

## 📸 Fitur Utama

- 💳 **Luhn MOD 10 Compliant:** Format kartu valid standar industri `NOMOR|MM|YYYY|CVV`.
- 📋 **1-Tap Copy:** Format *monospace* mempermudah penyalinan di aplikasi Telegram cukup sekali klik.
- 🌐 **Panduan Google Wallet:** Dilengkapi petunjuk penggunaan dan tombol instan ke Google Wallet.
- 🔒 **FSub Gate Protection:** Wajib bergabung ke channel, grup komunitas, dan start bot partner resmi sebelum mengakses generator.
- 👑 **Owner & Support:** Menampilkan informasi pemilik bot dan partner AI gratis.
- ⚙️ **Custom BIN:** Pengguna dapat mengganti BIN default kapan saja.

---

## 👑 Owner & Informasi Bot

* **Owner:** [adnan a](https://t.me/aifreemium42) (`@aifreemium42`)
* **ID:** `8958371948`
* **First:** adnan, **Last:** a
* **Bot Username:** [@myvccgen_bot](https://t.me/myvccgen_bot)

🧠 **Explanations and answers:**
Free AI → [DeepSeek](https://t.me/deepseek_gidbot) & [ChatGPT](https://t.me/chatgpt_gidbot)


---

## 🚀 Panduan Menjalankan

### 1. Salin Konfigurasi Environment
Salin file `.env.example` menjadi `.env`:
```bash
cp .env.example .env
```

Isi konfigurasi pada file `.env`:
```env
BOT_TOKEN=token_bot_anda
ADMIN_IDS=8958371948
DEFAULT_BIN=5279262291
REQUIRED_CHANNEL=@NetflixbotNotif
REQUIRED_GROUP=@FreemiumAi
PARTNER_BOT_1_USERNAME=netflixprogen_bot
PARTNER_BOT_2_USERNAME=aifreemium_bot
```

### 2. Pasang Dependensi
```bash
pip install -r requirements.txt
```

### 3. Jalankan Bot
```bash
python bot.py
```

### 4. Perintah Bot
* `/start` - Buka bot dan menu utama (setelah lolos FSub)
* `/gen` - Generate 1 kartu dengan BIN aktif
* `/gen <bin>` - Generate kartu dengan custom BIN (misal `/gen 527926`)
* `/gen <bin> <jumlah>` - Generate beberapa kartu (misal `/gen 527926 5`)
* `/bin <nomor_bin>` - Mengubah BIN default
* `/owner` - Menampilkan info pemilik dan support
* `/help` - Panduan lengkap penggunaan bot
