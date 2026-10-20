import os
import sys
import logging

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from generator import generate_vcc
from fsub import check_all_membership, build_fsub_message_and_keyboard, is_admin

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Defaults & Config
DEFAULT_BIN = os.getenv("DEFAULT_BIN", "5279262291")
GOOGLE_WALLET_URL = os.getenv("GOOGLE_WALLET_URL", "https://wallet.google.com/")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "aifreemium42").lstrip("@")
OWNER_ID = os.getenv("OWNER_ID", "8958371948")
OWNER_NAME = os.getenv("OWNER_NAME", "adnan a")

# Per-user active BIN memory & state
user_bins = {}
user_awaiting_bin = set()


def get_user_bin(user_id: int) -> str:
    return user_bins.get(user_id, DEFAULT_BIN)


def build_card_message(cards: list) -> str:
    count = len(cards)
    
    # Format each card inside mono-space / code tags for easy 1-tap copy
    cards_text = "\n".join([f"`{card['formatted']}`" for card in cards])
    
    message = (
        f"💳 *Cards Successfully Generated ({count} Cards)*\n\n"
        f"{cards_text}\n\n"
        f"_Tap or click the number above to copy._\n\n"
        f"🌐 *How to use in Google Wallet:*\n"
        f"1. Click *Open Google Wallet* below\n"
        f"2. Select *Add a payment method*\n"
        f"3. Enter the 16-digit card number, Expiry date, and 3-digit CVV\n"
        f"4. Fill in any name & address, then Save"
    )
    return message


def get_generated_keyboard(count: int = 1) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🌐 Open Google Wallet", url=GOOGLE_WALLET_URL)
        ],
        [
            InlineKeyboardButton(f"🔄 Generate Again ({count})", callback_data=f"gen_{count}"),
            InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("💳 Generate (1 Card)", callback_data="gen_1"),
            InlineKeyboardButton("💳 Generate (5 Cards)", callback_data="gen_5")
        ],
        [
            InlineKeyboardButton("⚙️ Set Custom BIN", callback_data="set_bin"),
            InlineKeyboardButton("ℹ️ How to Use", callback_data="help_menu")
        ],
        [
            InlineKeyboardButton("🌐 Open Google Wallet", url=GOOGLE_WALLET_URL)
        ],
        [
            InlineKeyboardButton("👑 Owner & Support", callback_data="owner_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def send_main_menu(target, current_bin: str, is_edit: bool = False):
    text = (
        f"👋 *Welcome to VCC Generator Bot*\n\n"
        f"📌 *Current BIN:* `{current_bin}`\n\n"
        f"Generate test virtual credit cards formatted with Luhn algorithm.\n"
        f"Select an option below to get started:"
    )
    if is_edit:
        await target.edit_message_text(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await target.reply_text(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )


async def owner_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    owner_url = f"https://t.me/{OWNER_USERNAME}"
    text = (
        "👑 *Bot Owner & Information*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"• *Owner:* [{OWNER_NAME}]({owner_url}) (`@{OWNER_USERNAME}`)\n"
        f"• *ID:* `{OWNER_ID}`\n"
        "• *Registered:* [Check Date](https://t.me/m/ECxXXcW-YWM0)\n\n"
        "🧠 *Free AI Partner:*\n"
        "• [DeepSeek](https://t.me/deepseek_gidbot)\n"
        "• [ChatGPT](https://t.me/chatgpt_gidbot)\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Chat Owner", url=owner_url)],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")]
    ])
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return

    # Cek verifikasi FSub
    is_ok, status_list = await check_all_membership(context.bot, user.id)
    if not is_ok:
        msg, kb = build_fsub_message_and_keyboard(status_list)
        await update.message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    current_bin = get_user_bin(user.id)
    await send_main_menu(update.message, current_bin)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user:
        is_ok, status_list = await check_all_membership(context.bot, user.id)
        if not is_ok:
            msg, kb = build_fsub_message_and_keyboard(status_list)
            if update.callback_query:
                await update.callback_query.edit_message_text(msg, reply_markup=kb, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            else:
                await update.message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return

    help_text = (
        "ℹ️ *VCC Generator Bot Help*\n\n"
        "• Klik tombol *Generate* untuk langsung menghasilkan kartu.\n"
        "• Tekan nomor kartu yang dihasilkan untuk menyalin (1-tap copy).\n"
        "• Perintah cepat:\n"
        "  `/gen` - Generate 1 kartu dengan BIN aktif\n"
        "  `/gen <bin>` - Generate kartu dengan BIN khusus (contoh: `/gen 527926`)\n"
        "  `/gen <bin> <jumlah>` - Generate beberapa kartu (contoh: `/gen 527926 5`)\n"
        "  `/bin <nomor_bin>` - Mengubah BIN default Anda\n"
        "  `/owner` - Informasi pemilik bot\n"
        "  `/menu` - Kembali ke menu utama"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Owner & Support", callback_data="owner_menu")],
        [InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")]
    ])
    if update.callback_query:
        await update.callback_query.edit_message_text(
            help_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            help_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )


async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return

    # Cek verifikasi FSub
    is_ok, status_list = await check_all_membership(context.bot, user.id)
    if not is_ok:
        msg, kb = build_fsub_message_and_keyboard(status_list)
        await update.message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    args = context.args
    bin_to_use = get_user_bin(user.id)
    count = 1

    if args:
        custom_bin = "".join(filter(str.isdigit, args[0]))
        if custom_bin:
            bin_to_use = custom_bin
        if len(args) > 1 and args[1].isdigit():
            count = min(max(int(args[1]), 1), 20)  # Max 20 kartu per batch

    cards = generate_vcc(bin_prefix=bin_to_use, count=count)
    msg = build_card_message(cards)
    await update.message.reply_text(
        msg,
        reply_markup=get_generated_keyboard(count=count),
        parse_mode=ParseMode.MARKDOWN
    )


async def bin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return

    # Cek verifikasi FSub
    is_ok, status_list = await check_all_membership(context.bot, user.id)
    if not is_ok:
        msg, kb = build_fsub_message_and_keyboard(status_list)
        await update.message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "⚠️ Gunakan format: `/bin <nomor_bin>`\nContoh: `/bin 5279262291`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    new_bin = "".join(filter(str.isdigit, args[0]))
    if len(new_bin) < 4:
        await update.message.reply_text("❌ BIN minimal 4 digit angka.")
        return

    user_bins[user.id] = new_bin
    await update.message.reply_text(
        f"✅ BIN berhasil diubah ke: `{new_bin}`",
        reply_markup=get_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = query.from_user
    data = query.data

    # Handler khusus tombol verifikasi FSub
    if data == "check_fsub":
        is_ok, status_list = await check_all_membership(context.bot, user.id)
        if is_ok:
            await query.answer("✅ Verifikasi berhasil! Selamat datang 🎉", show_alert=True)
            current_bin = get_user_bin(user.id)
            await send_main_menu(query, current_bin, is_edit=True)
        else:
            await query.answer(
                "⚠️ Anda belum bergabung/mengaktifkan semua channel & bot wajib!\n"
                "Silakan cek tautan bertanda ❌ di atas.",
                show_alert=True
            )
            msg, kb = build_fsub_message_and_keyboard(status_list)
            try:
                await query.edit_message_text(msg, reply_markup=kb, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            except Exception:
                pass
        return

    # Untuk callback lainnya, pastikan FSub sudah lolos
    is_ok, status_list = await check_all_membership(context.bot, user.id)
    if not is_ok:
        await query.answer("🔒 Silakan selesaikan verifikasi wajib terlebih dahulu!", show_alert=True)
        msg, kb = build_fsub_message_and_keyboard(status_list)
        try:
            await query.edit_message_text(msg, reply_markup=kb, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        except Exception:
            pass
        return

    await query.answer()

    if data == "main_menu":
        current_bin = get_user_bin(user.id)
        await send_main_menu(query, current_bin, is_edit=True)

    elif data == "owner_menu":
        await owner_command(update, context)

    elif data.startswith("gen_"):
        try:
            count = int(data.split("_")[1])
        except (IndexError, ValueError):
            count = 1
        
        current_bin = get_user_bin(user.id)
        cards = generate_vcc(bin_prefix=current_bin, count=count)
        msg = build_card_message(cards)
        
        await query.edit_message_text(
            msg,
            reply_markup=get_generated_keyboard(count=count),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "set_bin":
        user_awaiting_bin.add(user.id)
        text = (
            "⚙️ *Set Custom BIN*\n\n"
            "Kirimkan 6 sampai 10 digit BIN yang ingin Anda gunakan.\n"
            "Contoh: `527926` atau `5279262291`"
        )
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Cancel", callback_data="main_menu")
            ]]),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "help_menu":
        await help_command(update, context)


async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return

    text = update.message.text.strip()

    # Jika sedang menunggu input BIN baru
    if user.id in user_awaiting_bin:
        user_awaiting_bin.remove(user.id)
        clean_bin = "".join(filter(str.isdigit, text))
        if len(clean_bin) >= 4:
            user_bins[user.id] = clean_bin
            await update.message.reply_text(
                f"✅ BIN berhasil disimpan: `{clean_bin}`",
                reply_markup=get_main_menu_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "❌ BIN tidak valid. Harus minimal 4 digit angka.",
                reply_markup=get_main_menu_keyboard()
            )
        return


def main():
    if not BOT_TOKEN:
        print("❌ Error: BOT_TOKEN belum diatur!")
        print("Silakan isi file .env dengan token dari @BotFather:")
        print("BOT_TOKEN=your_telegram_bot_token_here")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("owner", owner_command))
    application.add_handler(CommandHandler("gen", gen_command))
    application.add_handler(CommandHandler("bin", bin_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    print("🚀 VCC Generator Telegram Bot sedang berjalan dengan info Owner & FSub...")
    application.run_polling()


if __name__ == "__main__":
    main()
