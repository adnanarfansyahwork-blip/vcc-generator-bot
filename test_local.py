import sys
import os

# Ensure UTF-8 stdout on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from generator import generate_vcc
from fsub import get_required_targets, build_fsub_message_and_keyboard


def test_fsub_simulation():
    print("=" * 60)
    print("     SIMULASI GATE VERIFIKASI WAJIB (FSUB GATE)")
    print("=" * 60)
    
    # Ambil konfigurasi target wajib
    targets = get_required_targets()
    
    # Simulasi status pengguna baru (belum join/start apa pun)
    simulated_status = [
        {**targets[0], "joined": False},
        {**targets[1], "joined": False},
        {**targets[2], "joined": False},
        {**targets[3], "joined": False},
    ]
    
    msg, kb = build_fsub_message_and_keyboard(simulated_status)
    print("\n[PESAN GATE KE PENGGUNA BARU]:")
    print("-" * 50)
    print(msg)
    print("-" * 50)
    print("[TOMBOL INLINE TELEGRAM]:")
    for row in kb.inline_keyboard:
        btn_texts = " | ".join([f"[{btn.text}]" for btn in row])
        print(btn_texts)
    print("=" * 60)
    
    # Simulasi setelah pengguna join & verifikasi berhasil
    print("\n[SIMULASI SETELAH USER JOIN SEMUA & KLIK VERIFIKASI]:")
    print("Status: ✅ Berhasil diverifikasi -> Menu Utama / Generate Kartu Terbuka!")


def simulate_telegram_output(bin_prefix: str = "5279262291"):
    print("\n" + "=" * 60)
    print("      SIMULASI TAMPILAN KARTU TER-GENERATE")
    print("=" * 60)
    
    cards = generate_vcc(bin_prefix=bin_prefix, count=1)
    card = cards[0]
    
    print(f"💳 Cards Successfully Generated (1 Cards)\n")
    print(f"  {card['formatted']}\n")
    print(f"Tap or click the number above to copy.\n")
    print(f"🌐 How to use in Google Wallet:")
    print(f"1. Click Open Google Wallet below")
    print(f"2. Select Add a payment method")
    print(f"3. Enter the 16-digit card number, Expiry date, and 3-digit CVV")
    print(f"4. Fill in any name & address, then Save")
    print("-" * 50)
    print("[ 🌐 Open Google Wallet (Link) ]")
    print("[ 🔄 Generate Again (1) ]  [ « Back to Main Menu ]")
    print("=" * 60)


if __name__ == "__main__":
    test_fsub_simulation()
    simulate_telegram_output("5279262291")
