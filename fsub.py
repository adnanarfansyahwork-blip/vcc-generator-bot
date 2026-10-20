import os
import time
import logging
from typing import Tuple, List, Dict
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden, TelegramError

logger = logging.getLogger(__name__)

# Cache hasil verifikasi (user_id -> expiry_timestamp)
_VERIFIED_CACHE: Dict[int, float] = {}
CACHE_TTL = 300  # 5 menit

# Cache hasil check partner bot ((bot_username, user_id) -> expiry_timestamp)
_PARTNER_OK_CACHE: Dict[Tuple[str, int], float] = {}
PARTNER_CACHE_TTL = 600  # 10 menit

# Cache instance telegram Bot partner
_PARTNER_CLIENTS: Dict[str, Bot] = {}


def get_required_targets() -> List[Dict]:
    """
    Daftar channel, grup, dan bot yang wajib di-join / di-start.
    """
    targets = [
        {
            "type": "channel",
            "id": os.getenv("REQUIRED_CHANNEL", "@NetflixbotNotif"),
            "title": "Channel Pemberitahuan",
            "username": os.getenv("REQUIRED_CHANNEL", "@NetflixbotNotif").lstrip("@"),
            "url": "https://t.me/NetflixbotNotif",
        },
        {
            "type": "group",
            "id": os.getenv("REQUIRED_GROUP", "@FreemiumAi"),
            "title": "Grup Komunitas Freemium AI",
            "username": os.getenv("REQUIRED_GROUP", "@FreemiumAi").lstrip("@"),
            "url": "https://t.me/FreemiumAi",
        },
        {
            "type": "bot",
            "username": os.getenv("PARTNER_BOT_1_USERNAME", "netflixprogen_bot").lstrip("@"),
            "title": "Start @netflixprogen_bot",
            "url": "https://t.me/netflixprogen_bot",
            "token": os.getenv("PARTNER_BOT_1_TOKEN", ""),
        },
        {
            "type": "bot",
            "username": os.getenv("PARTNER_BOT_2_USERNAME", "aifreemium_bot").lstrip("@"),
            "title": "Start @aifreemium_bot",
            "url": "https://t.me/aifreemium_bot",
            "token": os.getenv("PARTNER_BOT_2_TOKEN", "8355074804:AAH01FDj5tnDSLFv9D7A1DvuEnYT27N8OZg"),
        },
    ]
    return targets


def is_admin(user_id: int) -> bool:
    admin_ids_raw = os.getenv("ADMIN_IDS", "")
    admin_ids = [int(i.strip()) for i in admin_ids_raw.split(",") if i.strip().isdigit()]
    return user_id in admin_ids


async def check_bot_started(bot_username: str, token: str, user_id: int) -> bool:
    """
    Cek apakah user sudah menekan Start di bot partner.
    Menggunakan teknik send_chat_action(action='typing'):
    Jika user belum start / memblokir bot, Telegram menolak dengan Forbidden / BadRequest.
    """
    if not token:
        # Jika token partner tidak diisi di .env, loloskan secara graceful (fail-open)
        return True

    now = time.time()
    cache_key = (bot_username, user_id)
    if _PARTNER_OK_CACHE.get(cache_key, 0) > now:
        return True

    try:
        client = _PARTNER_CLIENTS.get(bot_username)
        if client is None:
            client = Bot(token=token)
            _PARTNER_CLIENTS[bot_username] = client
        await client.send_chat_action(chat_id=user_id, action="typing")
        _PARTNER_OK_CACHE[cache_key] = now + PARTNER_CACHE_TTL
        return True
    except (Forbidden, BadRequest):
        return False
    except Exception as exc:
        logger.warning("Cek bot @%s untuk user %s fail-open: %s", bot_username, user_id, exc)
        return True


async def check_all_membership(bot: Bot, user_id: int) -> Tuple[bool, List[Dict]]:
    """
    Cek status keanggotaan pengguna di semua target wajib.
    """
    # Bypass jika mode testing DISABLE_FSUB=1 atau user adalah Admin
    if os.getenv("DISABLE_FSUB", "0") == "1" or is_admin(user_id):
        targets = get_required_targets()
        return True, [{**t, "joined": True} for t in targets]

    # Cek cache verifikasi penuh
    now = time.time()
    if _VERIFIED_CACHE.get(user_id, 0) > now:
        targets = get_required_targets()
        return True, [{**t, "joined": True} for t in targets]

    targets = get_required_targets()
    status_list = []
    all_ok = True

    for item in targets:
        target_type = item["type"]
        is_joined = False

        if target_type in ("channel", "group"):
            target_id = item["id"]
            clean_id = target_id if target_id.startswith(("@", "-100")) else f"@{target_id}"
            try:
                member = await bot.get_chat_member(chat_id=clean_id, user_id=user_id)
                if member.status in ("creator", "administrator", "member", "restricted"):
                    is_joined = True
            except BadRequest as exc:
                err_str = str(exc).lower()
                if "participant_id_invalid" in err_str or "user not found" in err_str:
                    is_joined = False
                elif "chat_admin_required" in err_str or "member list is inaccessible" in err_str:
                    logger.warning(
                        "⚠️ Bot belum dijadikan Admin di %s! Silakan jadikan bot sebagai admin.",
                        clean_id
                    )
                    # Jika bot belum admin, jangan kunci user selamanya (fail-open)
                    is_joined = True
                else:
                    logger.warning("Error cek chat %s: %s", clean_id, exc)
                    is_joined = False
            except Exception as exc:
                logger.warning("Gagal cek chat %s: %s", clean_id, exc)
                is_joined = False

        elif target_type == "bot":
            is_joined = await check_bot_started(
                bot_username=item["username"],
                token=item.get("token", ""),
                user_id=user_id
            )

        if not is_joined:
            all_ok = False

        status_list.append({**item, "joined": is_joined})

    if all_ok:
        _VERIFIED_CACHE[user_id] = now + CACHE_TTL

    return all_ok, status_list


def build_fsub_message_and_keyboard(status_list: List[Dict]) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Render pesan FSub Gate beserta tombol interaktif join/start dan verifikasi.
    """
    lines = [
        "🔒 *Akses Terkunci — Verifikasi Wajib*",
        "━━━━━━━━━━━━━━━━━━━━",
        "Untuk menggunakan *VCC Generator Bot*, Anda **wajib bergabung & mengaktifkan** semua tautan resmi kami di bawah ini:\n",
    ]

    keyboard = []
    for idx, item in enumerate(status_list, 1):
        icon = "✅" if item["joined"] else "❌"
        target_type = item["type"]
        
        if target_type == "channel":
            type_label = "📢 Channel"
        elif target_type == "group":
            type_label = "👥 Grup"
        else:
            type_label = "🤖 Bot"

        title = item["title"]
        url = item["url"]
        lines.append(f"{idx}. {type_label}: [{title}]({url}) {icon}")
        keyboard.append([InlineKeyboardButton(f"{type_label}: {title}", url=url)])

    lines.append("\n━━━━━━━━━━━━━━━━━━━━")
    lines.append("💡 _Setelah join dan start semua di atas, tekan tombol verifikasi di bawah:_")

    keyboard.append([
        InlineKeyboardButton("🔄 Sudah Join & Start — Verifikasi", callback_data="check_fsub")
    ])

    return "\n".join(lines), InlineKeyboardMarkup(keyboard)
