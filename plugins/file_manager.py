# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

# File ID Management System
# Created by: AI Assistant for persistent streaming links

import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from database.users_chats_db import db
from info import ADMINS, LOG_CHANNEL
from utils import get_name

logger = logging.getLogger(__name__)

async def handle_file_upload(client: Client, message: Message):
    """
    Handle file upload and update file mapping if file already exists
    This ensures persistent links work even after file re-upload
    """
    try:
        if not message.media:
            return
        
        # Get file info
        file_info = getattr(message, message.media.value)
        file_id = file_info.file_id
        file_name = get_name(message)
        file_size = file_info.file_size
        mime_type = getattr(file_info, 'mime_type', None)
        
        # Check if this file ID already exists in database
        existing_mapping = await db.get_file_mapping(file_id)
        
        if existing_mapping:
            # File already exists, update the message ID
            await db.update_file_mapping(file_id, message.id)
            logger.info(f"Updated file mapping for {file_id}: old_msg_id={existing_mapping['message_id']}, new_msg_id={message.id}")
            
            # Notify admins about the update
            if message.chat.id == LOG_CHANNEL:
                try:
                    await client.send_message(
                        LOG_CHANNEL,
                        f"<b>📁 File Mapping Updated</b>\n\n"
                        f"<b>File:</b> <code>{file_name}</code>\n"
                        f"<b>File ID:</b> <code>{file_id}</code>\n"
                        f"<b>Old Message ID:</b> <code>{existing_mapping['message_id']}</code>\n"
                        f"<b>New Message ID:</b> <code>{message.id}</code>\n\n"
                        f"<b>✅ Persistent links will continue to work!</b>",
                        reply_to_message_id=message.id
                    )
                except:
                    pass
        else:
            # New file, create mapping
            await db.add_file_mapping(
                file_id=file_id,
                message_id=message.id,
                file_name=file_name,
                file_size=file_size,
                mime_type=mime_type
            )
            logger.info(f"Created new file mapping for {file_id}: msg_id={message.id}")
            
    except Exception as e:
        logger.error(f"Error in handle_file_upload: {e}")

@Client.on_message(filters.chat(LOG_CHANNEL) & (filters.document | filters.video | filters.audio | filters.photo))
async def log_channel_file_handler(client: Client, message: Message):
    """Handle files uploaded to log channel"""
    await handle_file_upload(client, message)

@Client.on_message(filters.command("file_stats") & filters.user(ADMINS))
async def file_statistics(client: Client, message: Message):
    """Show file mapping statistics"""
    try:
        all_mappings = await db.get_all_file_mappings()
        total_files = len(all_mappings)
        
        if total_files == 0:
            await message.reply("<b>কোন ফাইল ম্যাপিং পাওয়া যায়নি!</b>")
            return
        
        # Calculate total size
        total_size = 0
        video_count = 0
        document_count = 0
        audio_count = 0
        other_count = 0
        
        for mapping in all_mappings:
            total_size += mapping.get('file_size', 0)
            mime_type = mapping.get('mime_type', '')
            
            if mime_type.startswith('video/'):
                video_count += 1
            elif mime_type.startswith('audio/'):
                audio_count += 1
            elif mime_type.startswith('application/') or mime_type.startswith('text/'):
                document_count += 1
            else:
                other_count += 1
        
        # Convert size to human readable format
        def format_size(size_bytes):
            if size_bytes == 0:
                return "0 B"
            size_names = ["B", "KB", "MB", "GB", "TB"]
            import math
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            return f"{s} {size_names[i]}"
        
        text = f"<b>📊 ফাইল ম্যাপিং পরিসংখ্যান</b>\n\n"
        text += f"<b>মোট ফাইল:</b> {total_files}\n"
        text += f"<b>মোট সাইজ:</b> {format_size(total_size)}\n\n"
        text += f"<b>📁 ফাইল টাইপ:</b>\n"
        text += f"• ভিডিও: {video_count}\n"
        text += f"• অডিও: {audio_count}\n"
        text += f"• ডকুমেন্ট: {document_count}\n"
        text += f"• অন্যান্য: {other_count}\n\n"
        text += f"<b>✅ সব ফাইলের জন্য persistent links তৈরি!</b>"
        
        await message.reply(text)
        
    except Exception as e:
        await message.reply(f"<b>❌ এরর:</b> <code>{str(e)}</code>")

@Client.on_message(filters.command("cleanup_mappings") & filters.user(ADMINS))
async def cleanup_file_mappings(client: Client, message: Message):
    """Clean up invalid file mappings"""
    try:
        all_mappings = await db.get_all_file_mappings()
        cleaned_count = 0
        
        for mapping in all_mappings:
            try:
                # Try to get the message to check if it still exists
                msg = await client.get_messages(LOG_CHANNEL, mapping['message_id'])
                if not msg or not msg.media:
                    # Message doesn't exist or has no media, remove mapping
                    await db.delete_file_mapping(mapping['file_id'])
                    cleaned_count += 1
            except:
                # Message not found, remove mapping
                await db.delete_file_mapping(mapping['file_id'])
                cleaned_count += 1
        
        await message.reply(
            f"<b>🧹 ক্লিনআপ সম্পন্ন!</b>\n\n"
            f"<b>মুছে ফেলা ম্যাপিং:</b> {cleaned_count}\n"
            f"<b>বাকি ম্যাপিং:</b> {len(all_mappings) - cleaned_count}"
        )
        
    except Exception as e:
        await message.reply(f"<b>❌ এরর:</b> <code>{str(e)}</code>")

@Client.on_message(filters.command("check_file") & filters.user(ADMINS))
async def check_file_mapping(client: Client, message: Message):
    """Check file mapping for a specific file ID"""
    if len(message.command) < 2:
        await message.reply(
            "<b>ব্যবহার:</b> <code>/check_file file_id</code>\n\n"
            "<b>উদাহরণ:</b> <code>/check_file BAADBAADGwADBREAAR8X...</code>"
        )
        return
    
    try:
        file_id = message.command[1]
        mapping = await db.get_file_mapping(file_id)
        
        if not mapping:
            await message.reply(f"<b>❌ ফাইল আইডি পাওয়া যায়নি:</b> <code>{file_id}</code>")
            return
        
        # Try to get the actual message
        try:
            msg = await client.get_messages(LOG_CHANNEL, mapping['message_id'])
            status = "✅ সক্রিয়" if msg and msg.media else "❌ নিষ্ক্রিয়"
        except:
            status = "❌ নিষ্ক্রিয়"
        
        text = f"<b>🔍 ফাইল ম্যাপিং তথ্য</b>\n\n"
        text += f"<b>ফাইল আইডি:</b> <code>{file_id}</code>\n"
        text += f"<b>মেসেজ আইডি:</b> <code>{mapping['message_id']}</code>\n"
        text += f"<b>ফাইল নাম:</b> <code>{mapping.get('file_name', 'Unknown')}</code>\n"
        text += f"<b>ফাইল সাইজ:</b> <code>{mapping.get('file_size', 0)} bytes</code>\n"
        text += f"<b>MIME টাইপ:</b> <code>{mapping.get('mime_type', 'Unknown')}</code>\n"
        text += f"<b>স্ট্যাটাস:</b> {status}\n"
        text += f"<b>তৈরি:</b> <code>{mapping.get('created_at', 'Unknown')}</code>\n"
        
        if mapping.get('updated_at'):
            text += f"<b>আপডেট:</b> <code>{mapping['updated_at']}</code>\n"
        
        # Generate persistent links
        from urllib.parse import quote_plus
        from info import URL
        file_name = quote_plus(mapping.get('file_name', 'file'))
        
        text += f"\n<b>🔗 Persistent Links:</b>\n"
        text += f"<b>Download:</b> <code>{URL}f_{file_id}/{file_name}</code>\n"
        text += f"<b>Stream:</b> <code>{URL}watch/f_{file_id}/{file_name}</code>"
        
        await message.reply(text)
        
    except Exception as e:
        await message.reply(f"<b>❌ এরর:</b> <code>{str(e)}</code>")

@Client.on_message(filters.command("regenerate_mapping") & filters.user(ADMINS))
async def regenerate_file_mapping(client: Client, message: Message):
    """Regenerate file mapping from log channel messages"""
    if len(message.command) < 3:
        await message.reply(
            "<b>ব্যবহার:</b> <code>/regenerate_mapping start_id end_id</code>\n\n"
            "<b>উদাহরণ:</b> <code>/regenerate_mapping 1000 2000</code>\n\n"
            "<b>⚠️ সতর্কতা:</b> এটি অনেক সময় নিতে পারে!"
        )
        return
    
    try:
        start_id = int(message.command[1])
        end_id = int(message.command[2])
        
        if end_id - start_id > 1000:
            await message.reply("<b>❌ একবারে সর্বোচ্চ ১০০০ মেসেজ প্রসেস করা যাবে!</b>")
            return
        
        status_msg = await message.reply(f"<b>🔄 ম্যাপিং রিজেনারেট করা হচ্ছে...</b>\n\n<b>রেঞ্জ:</b> {start_id} - {end_id}")
        
        processed = 0
        created = 0
        updated = 0
        
        for msg_id in range(start_id, end_id + 1):
            try:
                msg = await client.get_messages(LOG_CHANNEL, msg_id)
                if msg and msg.media:
                    await handle_file_upload(client, msg)
                    processed += 1
                    
                    if processed % 50 == 0:
                        await status_msg.edit_text(
                            f"<b>🔄 ম্যাপিং রিজেনারেট করা হচ্ছে...</b>\n\n"
                            f"<b>রেঞ্জ:</b> {start_id} - {end_id}\n"
                            f"<b>প্রসেস:</b> {processed}/{end_id - start_id + 1}"
                        )
            except:
                continue
        
        await status_msg.edit_text(
            f"<b>✅ ম্যাপিং রিজেনারেট সম্পন্ন!</b>\n\n"
            f"<b>রেঞ্জ:</b> {start_id} - {end_id}\n"
            f"<b>প্রসেস করা মেসেজ:</b> {processed}\n\n"
            f"<b>🎉 এখন সব ফাইলের persistent links কাজ করবে!</b>"
        )
        
    except ValueError:
        await message.reply("<b>❌ ভুল মেসেজ আইডি! সংখ্যা দিন।</b>")
    except Exception as e:
        await message.reply(f"<b>❌ এরর:</b> <code>{str(e)}</code>")
