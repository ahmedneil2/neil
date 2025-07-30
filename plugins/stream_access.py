# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

# Stream Access Control Commands
# Created by: AI Assistant for enhanced bot functionality

import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.users_chats_db import db
from info import ADMINS, STREAM_ACCESS_CONTROL, STREAM_ACCESS_USERS
from utils import temp

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("add_stream") & filters.user(ADMINS))
async def add_stream_user(client, message):
    """Add user to stream access list"""
    if len(message.command) < 2:
        await message.reply(
            "<b>ব্যবহার:</b> <code>/add_stream user_id</code>\n\n"
            "<b>উদাহরণ:</b> <code>/add_stream 123456789</code>"
        )
        return
    
    try:
        user_id = int(message.command[1])
        
        # Check if user already has stream access
        if await db.has_stream_access(user_id):
            await message.reply(f"<b>ইউজার {user_id} এর ইতিমধ্যে স্ট্রিম অ্যাক্সেস আছে!</b>")
            return
        
        # Add user to stream access
        await db.add_stream_user(user_id)
        
        # Try to get user info
        try:
            user = await client.get_users(user_id)
            user_mention = user.mention
            user_name = f"({user.first_name})"
        except:
            user_mention = f"<code>{user_id}</code>"
            user_name = ""
        
        await message.reply(
            f"<b>✅ স্ট্রিম অ্যাক্সেস যোগ করা হয়েছে!</b>\n\n"
            f"<b>ইউজার:</b> {user_mention} {user_name}\n"
            f"<b>ইউজার আইডি:</b> <code>{user_id}</code>\n\n"
            f"<b>এখন এই ইউজার স্ট্রিমিং ফিচার ব্যবহার করতে পারবে।</b>"
        )
        
        # Notify user if possible
        try:
            await client.send_message(
                user_id,
                "<b>🎉 অভিনন্দন!</b>\n\n"
                "<b>আপনার স্ট্রিমিং অ্যাক্সেস চালু করা হয়েছে!</b>\n\n"
                "<b>এখন আপনি ফাইল ডাউনলোড এবং স্ট্রিমিং দুটোই করতে পারবেন।</b>"
            )
        except:
            pass
            
    except ValueError:
        await message.reply("<b>❌ ভুল ইউজার আইডি! সংখ্যা দিন।</b>")
    except Exception as e:
        await message.reply(f"<b>❌ এরর:</b> <code>{str(e)}</code>")

@Client.on_message(filters.command("remove_stream") & filters.user(ADMINS))
async def remove_stream_user(client, message):
    """Remove user from stream access list"""
    if len(message.command) < 2:
        await message.reply(
            "<b>ব্যবহার:</b> <code>/remove_stream user_id</code>\n\n"
            "<b>উদাহরণ:</b> <code>/remove_stream 123456789</code>"
        )
        return
    
    try:
        user_id = int(message.command[1])
        
        # Check if user has stream access
        if not await db.has_stream_access(user_id):
            await message.reply(f"<b>ইউজার {user_id} এর স্ট্রিম অ্যাক্সেস নেই!</b>")
            return
        
        # Remove user from stream access
        await db.remove_stream_user(user_id)
        
        # Try to get user info
        try:
            user = await client.get_users(user_id)
            user_mention = user.mention
            user_name = f"({user.first_name})"
        except:
            user_mention = f"<code>{user_id}</code>"
            user_name = ""
        
        await message.reply(
            f"<b>❌ স্ট্রিম অ্যাক্সেস সরানো হয়েছে!</b>\n\n"
            f"<b>ইউজার:</b> {user_mention} {user_name}\n"
            f"<b>ইউজার আইডি:</b> <code>{user_id}</code>\n\n"
            f"<b>এখন এই ইউজার শুধু ফাইল ডাউনলোড করতে পারবে।</b>"
        )
        
        # Notify user if possible
        try:
            await client.send_message(
                user_id,
                "<b>⚠️ বিজ্ঞপ্তি!</b>\n\n"
                "<b>আপনার স্ট্রিমিং অ্যাক্সেস বন্ধ করা হয়েছে!</b>\n\n"
                "<b>এখন আপনি শুধু ফাইল ডাউনলোড করতে পারবেন।</b>"
            )
        except:
            pass
            
    except ValueError:
        await message.reply("<b>❌ ভুল ইউজার আইডি! সংখ্যা দিন।</b>")
    except Exception as e:
        await message.reply(f"<b>❌ এরর:</b> <code>{str(e)}</code>")

@Client.on_message(filters.command("stream_users") & filters.user(ADMINS))
async def list_stream_users(client, message):
    """List all users with stream access"""
    try:
        # Get users from database
        db_users = await db.get_all_stream_users()
        
        # Get users from config
        config_users = STREAM_ACCESS_USERS if STREAM_ACCESS_CONTROL else []
        
        # Combine and remove duplicates
        all_users = list(set(db_users + config_users + ADMINS))
        
        if not all_users:
            await message.reply("<b>কোন ইউজারের স্ট্রিম অ্যাক্সেস নেই!</b>")
            return
        
        text = f"<b>📊 স্ট্রিম অ্যাক্সেস ইউজার লিস্ট</b>\n\n"
        text += f"<b>মোট ইউজার:</b> {len(all_users)}\n\n"
        
        for i, user_id in enumerate(all_users[:20], 1):  # Show max 20 users
            try:
                user = await client.get_users(user_id)
                name = user.first_name
                username = f"@{user.username}" if user.username else "No username"
                text += f"<b>{i}.</b> <a href='tg://user?id={user_id}'>{name}</a> ({username})\n"
                text += f"    <code>{user_id}</code>\n\n"
            except:
                text += f"<b>{i}.</b> <code>{user_id}</code> (Unknown User)\n\n"
        
        if len(all_users) > 20:
            text += f"<b>... এবং আরো {len(all_users) - 20} জন ইউজার</b>"
        
        # Add management buttons
        buttons = [
            [InlineKeyboardButton("🔄 রিফ্রেশ", callback_data="refresh_stream_users")],
            [InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
        ]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
        
    except Exception as e:
        await message.reply(f"<b>❌ এরর:</b> <code>{str(e)}</code>")

@Client.on_message(filters.command("stream_status") & filters.user(ADMINS))
async def stream_status(client, message):
    """Show stream access control status"""
    try:
        db_count = await db.get_stream_users_count()
        config_count = len(STREAM_ACCESS_USERS) if STREAM_ACCESS_CONTROL else 0
        admin_count = len(ADMINS)
        
        status_text = "🟢 চালু" if STREAM_ACCESS_CONTROL else "🔴 বন্ধ"
        
        text = f"<b>📊 স্ট্রিম অ্যাক্সেস স্ট্যাটাস</b>\n\n"
        text += f"<b>নিয়ন্ত্রণ:</b> {status_text}\n\n"
        text += f"<b>📈 পরিসংখ্যান:</b>\n"
        text += f"• ডাটাবেস ইউজার: {db_count}\n"
        text += f"• কনফিগ ইউজার: {config_count}\n"
        text += f"• অ্যাডমিন: {admin_count}\n"
        text += f"• মোট: {db_count + config_count + admin_count}\n\n"
        
        if STREAM_ACCESS_CONTROL:
            text += "<b>✅ স্ট্রিম অ্যাক্সেস নিয়ন্ত্রণ চালু আছে</b>\n"
            text += "<b>শুধুমাত্র অনুমোদিত ইউজাররা স্ট্রিমিং করতে পারবে</b>"
        else:
            text += "<b>⚠️ স্ট্রিম অ্যাক্সেস নিয়ন্ত্রণ বন্ধ আছে</b>\n"
            text += "<b>সবাই স্ট্রিমিং করতে পারবে</b>"
        
        buttons = [
            [InlineKeyboardButton("👥 ইউজার লিস্ট", callback_data="show_stream_users")],
            [InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
        ]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
        
    except Exception as e:
        await message.reply(f"<b>❌ এরর:</b> <code>{str(e)}</code>")

@Client.on_message(filters.command("check_stream") & filters.user(ADMINS))
async def check_stream_access(client, message):
    """Check if a specific user has stream access"""
    if len(message.command) < 2:
        await message.reply(
            "<b>ব্যবহার:</b> <code>/check_stream user_id</code>\n\n"
            "<b>উদাহরণ:</b> <code>/check_stream 123456789</code>"
        )
        return
    
    try:
        user_id = int(message.command[1])
        has_access = await db.has_stream_access(user_id)
        
        # Try to get user info
        try:
            user = await client.get_users(user_id)
            user_mention = user.mention
            user_name = f"({user.first_name})"
        except:
            user_mention = f"<code>{user_id}</code>"
            user_name = ""
        
        status = "✅ আছে" if has_access else "❌ নেই"
        
        text = f"<b>🔍 স্ট্রিম অ্যাক্সেস চেক</b>\n\n"
        text += f"<b>ইউজার:</b> {user_mention} {user_name}\n"
        text += f"<b>ইউজার আইডি:</b> <code>{user_id}</code>\n"
        text += f"<b>স্ট্রিম অ্যাক্সেস:</b> {status}\n\n"
        
        if has_access:
            text += "<b>এই ইউজার স্ট্রিমিং এবং ডাউনলোড দুটোই করতে পারবে।</b>"
        else:
            text += "<b>এই ইউজার শুধু ফাইল ডাউনলোড করতে পারবে।</b>"
        
        await message.reply(text)
        
    except ValueError:
        await message.reply("<b>❌ ভুল ইউজার আইডি! সংখ্যা দিন।</b>")
    except Exception as e:
        await message.reply(f"<b>❌ এরর:</b> <code>{str(e)}</code>")

# Callback Query Handlers for Stream Access Management
@Client.on_callback_query(filters.regex("^refresh_stream_users$"))
async def refresh_stream_users_callback(client, query):
    """Refresh stream users list"""
    if query.from_user.id not in ADMINS:
        await query.answer("❌ আপনার এই অ্যাকশনের অনুমতি নেই!", show_alert=True)
        return

    try:
        # Get users from database
        db_users = await db.get_all_stream_users()

        # Get users from config
        config_users = STREAM_ACCESS_USERS if STREAM_ACCESS_CONTROL else []

        # Combine and remove duplicates
        all_users = list(set(db_users + config_users + ADMINS))

        if not all_users:
            text = "<b>কোন ইউজারের স্ট্রিম অ্যাক্সেস নেই!</b>"
            buttons = [[InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]]
        else:
            text = f"<b>📊 স্ট্রিম অ্যাক্সেস ইউজার লিস্ট</b>\n\n"
            text += f"<b>মোট ইউজার:</b> {len(all_users)}\n\n"

            for i, user_id in enumerate(all_users[:20], 1):  # Show max 20 users
                try:
                    user = await client.get_users(user_id)
                    name = user.first_name
                    username = f"@{user.username}" if user.username else "No username"
                    text += f"<b>{i}.</b> <a href='tg://user?id={user_id}'>{name}</a> ({username})\n"
                    text += f"    <code>{user_id}</code>\n\n"
                except:
                    text += f"<b>{i}.</b> <code>{user_id}</code> (Unknown User)\n\n"

            if len(all_users) > 20:
                text += f"<b>... এবং আরো {len(all_users) - 20} জন ইউজার</b>"

            buttons = [
                [InlineKeyboardButton("🔄 রিফ্রেশ", callback_data="refresh_stream_users")],
                [InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
            ]

        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        await query.answer("✅ তালিকা আপডেট হয়েছে!")

    except Exception as e:
        await query.answer(f"❌ এরর: {str(e)}", show_alert=True)

@Client.on_callback_query(filters.regex("^show_stream_users$"))
async def show_stream_users_callback(client, query):
    """Show stream users list from status command"""
    if query.from_user.id not in ADMINS:
        await query.answer("❌ আপনার এই অ্যাকশনের অনুমতি নেই!", show_alert=True)
        return

    try:
        # Get users from database
        db_users = await db.get_all_stream_users()

        # Get users from config
        config_users = STREAM_ACCESS_USERS if STREAM_ACCESS_CONTROL else []

        # Combine and remove duplicates
        all_users = list(set(db_users + config_users + ADMINS))

        if not all_users:
            text = "<b>কোন ইউজারের স্ট্রিম অ্যাক্সেস নেই!</b>"
            buttons = [
                [InlineKeyboardButton("🔙 ফিরে যান", callback_data="back_to_status")],
                [InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
            ]
        else:
            text = f"<b>📊 স্ট্রিম অ্যাক্সেস ইউজার লিস্ট</b>\n\n"
            text += f"<b>মোট ইউজার:</b> {len(all_users)}\n\n"

            for i, user_id in enumerate(all_users[:15], 1):  # Show max 15 users in callback
                try:
                    user = await client.get_users(user_id)
                    name = user.first_name[:20]  # Limit name length
                    text += f"<b>{i}.</b> <a href='tg://user?id={user_id}'>{name}</a>\n"
                    text += f"    <code>{user_id}</code>\n\n"
                except:
                    text += f"<b>{i}.</b> <code>{user_id}</code>\n\n"

            if len(all_users) > 15:
                text += f"<b>... এবং আরো {len(all_users) - 15} জন</b>\n\n"
                text += "<b>সম্পূর্ণ তালিকার জন্য /stream_users কমান্ড ব্যবহার করুন</b>"

            buttons = [
                [InlineKeyboardButton("🔄 রিফ্রেশ", callback_data="show_stream_users")],
                [InlineKeyboardButton("🔙 ফিরে যান", callback_data="back_to_status")],
                [InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
            ]

        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        await query.answer(f"❌ এরর: {str(e)}", show_alert=True)

@Client.on_callback_query(filters.regex("^back_to_status$"))
async def back_to_status_callback(client, query):
    """Go back to stream status"""
    if query.from_user.id not in ADMINS:
        await query.answer("❌ আপনার এই অ্যাকশনের অনুমতি নেই!", show_alert=True)
        return

    try:
        db_count = await db.get_stream_users_count()
        config_count = len(STREAM_ACCESS_USERS) if STREAM_ACCESS_CONTROL else 0
        admin_count = len(ADMINS)

        status_text = "🟢 চালু" if STREAM_ACCESS_CONTROL else "🔴 বন্ধ"

        text = f"<b>📊 স্ট্রিম অ্যাক্সেস স্ট্যাটাস</b>\n\n"
        text += f"<b>নিয়ন্ত্রণ:</b> {status_text}\n\n"
        text += f"<b>📈 পরিসংখ্যান:</b>\n"
        text += f"• ডাটাবেস ইউজার: {db_count}\n"
        text += f"• কনফিগ ইউজার: {config_count}\n"
        text += f"• অ্যাডমিন: {admin_count}\n"
        text += f"• মোট: {db_count + config_count + admin_count}\n\n"

        if STREAM_ACCESS_CONTROL:
            text += "<b>✅ স্ট্রিম অ্যাক্সেস নিয়ন্ত্রণ চালু আছে</b>\n"
            text += "<b>শুধুমাত্র অনুমোদিত ইউজাররা স্ট্রিমিং করতে পারবে</b>"
        else:
            text += "<b>⚠️ স্ট্রিম অ্যাক্সেস নিয়ন্ত্রণ বন্ধ আছে</b>\n"
            text += "<b>সবাই স্ট্রিমিং করতে পারবে</b>"

        buttons = [
            [InlineKeyboardButton("👥 ইউজার লিস্ট", callback_data="show_stream_users")],
            [InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
        ]

        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        await query.answer(f"❌ এরর: {str(e)}", show_alert=True)
