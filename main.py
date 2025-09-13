import os, json, asyncio, re, string, random, aiohttp, time, concurrent.futures
from os import system, path
from time import sleep
from random import choice, randint
from base64 import b64decode

import aiohttp
from bs4 import BeautifulSoup as S
from fake_useragent import UserAgent
from datetime import datetime

from telethon import TelegramClient, functions, errors, events, types
from telethon.tl.functions.account import CheckUsernameRequest, UpdateUsernameRequest
from telethon.tl.functions.channels import CreateChannelRequest, UpdateUsernameRequest as UpdateChannelUsername
from telethon.tl.functions.channels import DeleteChannelRequest, EditPhotoRequest, GetChannelsRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.sessions import StringSession
from telethon.tl.types import InputChatUploadedPhoto

# ألوان للواجهة
class Colors:
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    MAGENTA = '\033[1;35m'
    CYAN = '\033[1;36m'
    WHITE = '\033[1;37m'
    RESET = '\033[0m'

# إعدادات API
api_id = '26619062'
api_hash = 'b4b0bceacb5c6719d5d6617a0f826f32'

# معلومات المطور
developer = "@ra_a_a"
support_channel = "@ra_a_a"

class UltraUsernameClaimer:
    def __init__(self):
        self.client = None
        self.phone = None
        self.names = set()
        self.clicks = 0
        self.start_time = datetime.now()
        self.available_usernames = []
        self.premium_usernames = []
        self.is_running = True
        self.session = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        
        # بيانات الجلسة للتسجيل التلقائي - سيتم قراءتها من ملف
        self.session_string = self.load_session_from_file()
        
        # إنشاء مجلدات التصفية
        self.filter_dir = "فلترة_اليوزرات"
        os.makedirs(self.filter_dir, exist_ok=True)
        
        # ملفات حفظ اليوزرات المعيبة
        self.banned_file = os.path.join(self.filter_dir, "فلترة_banned.txt")
        self.unknown_file = os.path.join(self.filter_dir, "فلترة_unknown.txt")
        self.invalid_file = os.path.join(self.filter_dir, "فلترة_invalid.txt")
        
        # تحميل اليوزرات المصفاة مسبقاً
        self.filtered_usernames = set()
        self.banned_usernames = self.load_filtered_usernames(self.banned_file)
        self.unknown_usernames = self.load_filtered_usernames(self.unknown_file)
        self.invalid_usernames = self.load_filtered_usernames(self.invalid_file)
        
        # دمج جميع المجموعات
        self.filtered_usernames.update(self.banned_usernames)
        self.filtered_usernames.update(self.unknown_usernames)
        self.filtered_usernames.update(self.invalid_usernames)
        
        print(f"{Colors.GREEN}📊 تم تحميل {len(self.filtered_usernames)} يوزر مصفى مسبقاً{Colors.RESET}")
        
        # مجموعة لتتبع اليوزرات المحفوظة
        self.saved_usernames = set()

    def load_session_from_file(self):
        """قراءة الجلسة من ملف glshhhh"""
        session_file = "glshhhh"
        try:
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_string = f.read().strip()
                    print(f"{Colors.GREEN}✅ تم تحميل الجلسة من ملف {session_file}{Colors.RESET}")
                    return session_string
            else:
                print(f"{Colors.YELLOW}⚠️  ملف الجلسة {session_file} غير موجود{Colors.RESET}")
                return ""
        except Exception as e:
            print(f"{Colors.RED}❌ خطأ في قراءة ملف الجلسة: {e}{Colors.RESET}")
            return ""

    async def auto_login_with_session(self):
        """تسجيل الدخول التلقائي باستخدام جلسة موجودة"""
        try:
            if not self.session_string:
                print(f"{Colors.RED}❌ لا توجد جلسة متاحة للتسجيل التلقائي{Colors.RESET}")
                return False
                
            print(f"{Colors.CYAN}🔐 محاولة تسجيل الدخول التلقائي...{Colors.RESET}")
            
            # فك تشفير الجلسة إذا كانت مشفرة
            session_string = self.session_string
            if session_string.startswith("1"):
                try:
                    session_string = b64decode(session_string).decode('utf-8')
                except:
                    pass
            
            # إنشاء العميل باستخدام جلسة السلسلة
            self.client = TelegramClient(StringSession(session_string), api_id, api_hash)
            await self.client.start()
            
            # الحصول على معلومات المستخدم
            me = await self.client.get_me()
            self.phone = me.phone
            
            print(f"{Colors.GREEN}✅ تم تسجيل الدخول التلقائي بنجاح إلى: {self.phone}{Colors.RESET}")
            
            # إعداد نظام الأوامر
            self.setup_event_handler()
            
            # الانضمام إلى قناة المطور
            try:
                await self.client(functions.channels.JoinChannelRequest("ra_a_a"))
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ فشل التسجيل التلقائي: {e}{Colors.RESET}")
            return False

    async def login_with_phone(self):
        """تسجيل الدخول باستخدام رقم الهاتف (الطريقة اليدوية)"""
        print(f"{Colors.CYAN}📱 تسجيل الدخول برقم الهاتف{Colors.RESET}")
        
        while True:
            try:
                self.phone = input(f"{Colors.YELLOW}⌨️  أدخل رقم الهاتف (مع رمز الدولة): {Colors.RESET}")
                
                if not self.phone:
                    print(f"{Colors.RED}❌ يجب إدخال رقم هاتف صحيح{Colors.RESET}")
                    continue
                
                # إنشاء عملي جديد
                self.client = TelegramClient(f"sessions/{self.phone}", api_id, api_hash)
                
                # بدء الجلسة
                await self.client.start(phone=self.phone)
                
                print(f"{Colors.GREEN}✅ تم تسجيل الدخول بنجاح إلى: {self.phone}{Colors.RESET}")
                
                # إعداد نظام الأوامر
                self.setup_event_handler()
                
                # الانضمام إلى قناة المطور
                try:
                    await self.client(functions.channels.JoinChannelRequest("ra_a_a"))
                except:
                    pass
                
                return True
                
            except SessionPasswordNeededError:
                print(f"{Colors.YELLOW}🔒 الحساب محمي بكلمة مرور ثنائية{Colors.RESET}")
                password = input(f"{Colors.YELLOW}⌨️  أدخل كلمة المرور: {Colors.RESET}")
                try:
                    await self.client.start(phone=self.phone, password=password)
                    print(f"{Colors.GREEN}✅ تم تسجيل الدخول بنجاح{Colors.RESET}")
                    return True
                except Exception as e:
                    print(f"{Colors.RED}❌ كلمة المرور خاطئة: {e}{Colors.RESET}")
                    continue
                    
            except Exception as e:
                print(f"{Colors.RED}❌ خطأ في تسجيل الدخول: {e}{Colors.RESET}")
                retry = input(f"{Colors.YELLOW}⌨️  هل تريد المحاولة مرة أخرى؟ (y/n): {Colors.RESET}")
                if retry.lower() != 'y':
                    return False

    def load_filtered_usernames(self, filename):
        """تحميل اليوزرات المعيبة من ملف"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return set(line.strip().lower() for line in f if line.strip())
            return set()
        except Exception as e:
            print(f"{Colors.RED}❌ خطأ في تحميل الملف {filename}: {e}{Colors.RESET}")
            return set()

    def save_filtered_username(self, username, filename):
        """حفظ اليوزر المعيب في ملف"""
        try:
            username_lower = username.lower()
            
            if username_lower in self.saved_usernames:
                return
            
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(username_lower + '\n')
            
            self.filtered_usernames.add(username_lower)
            self.saved_usernames.add(username_lower)
            
        except Exception as e:
            print(f"{Colors.RED}❌ خطأ في حفظ اليوزر: {e}{Colors.RESET}")

    def setup_event_handler(self):
        """إعداد معالج الأحداث للأوامر"""
        
        @self.client.on(events.NewMessage(pattern=r'\.فحص'))
        async def check_handler(event):
            await self.check_status(event)
        
        @self.client.on(events.NewMessage(pattern=r'\.الاحصائيات'))
        async def stats_handler(event):
            await self.detailed_stats(event)
        
        @self.client.on(events.NewMessage(pattern=r'\.المساعدة'))
        async def help_handler(event):
            await self.show_help(event)
        
        @self.client.on(events.NewMessage(pattern=r'\.اليوزرات'))
        async def usernames_handler(event):
            await self.show_usernames(event)
        
        @self.client.on(events.NewMessage(pattern=r'\.ايقاف'))
        async def stop_handler(event):
            await self.stop_bot(event)
        
        @self.client.on(events.NewMessage(pattern=r'\.تشغيل'))
        async def start_handler(event):
            await self.start_bot(event)
        
        @self.client.on(events.NewMessage(pattern=r'\.تصفية'))
        async def filter_stats_handler(event):
            await self.show_filter_stats(event)
        
        @self.client.on(events.NewMessage(pattern=r'\.المجلد'))
        async def folder_handler(event):
            await self.show_folder_location(event)
        
        @self.client.on(events.NewMessage(pattern=r'\.حذف_unknown'))
        async def delete_unknown_handler(event):
            await self.delete_unknown_file(event)
        
        @self.client.on(events.NewMessage(pattern=r'\.قنواتي'))
        async def my_channels_handler(event):
            await self.show_my_channels(event)
        
        print(f"{Colors.GREEN}✅ نظام الأوامر مفعل - اكتب (.المساعدة) لرؤية الأوامر{Colors.RESET}")

    async def check_status(self, event):
        """فحص حالة البوت"""
        current_time = datetime.now()
        uptime = current_time - self.start_time
        hours, remainder = divmod(uptime.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        filtered_count = len(self.banned_usernames) + len(self.unknown_usernames) + len(self.invalid_usernames)
        
        status_message = (
            f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}\n"
            f"{Colors.YELLOW}  ⚡ فحص الأداة ⚡{Colors.RESET}\n"
            f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}\n\n"
            f"⏰ وقت البداية : {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"⏱️ مدة التشغيل : {int(hours)} ساعة و {int(minutes)} دقيقة و {int(seconds)} ثانية\n"
            f"🔢 عدد الضغطات : {self.clicks}\n"
            f"🗑️ اليوزرات المصفاة : {filtered_count}\n"
            f"📊 اليوزرات المتاحة : {len(self.available_usernames)}\n\n"
            f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}\n"
            f"⚡ {developer}"
        )
        
        await event.reply(status_message)

    async def detailed_stats(self, event):
        """إحصائيات مفصلة"""
        current_time = datetime.now()
        uptime = current_time - self.start_time
        
        hours = uptime.total_seconds() / 3600
        speed = self.clicks / hours if hours > 0 else 0
        
        filtered_count = len(self.banned_usernames) + len(self.unknown_usernames) + len(self.invalid_usernames)
        
        stats_message = (
            f"{Colors.CYAN}📊 الإحصائيات المفصلة{Colors.RESET}\n\n"
            f"• عدد اليوزرات المفحوصة: {self.clicks}\n"
            f"• عدد اليوزرات المتاحة: {len(self.available_usernames)}\n"
            f"• عدد اليوزرات المميزة: {len(self.premium_usernames)}\n"
            f"• عدد اليوزرات المصفاة: {filtered_count}\n"
            f"• اليوزرات Banned: {len(self.banned_usernames)}\n"
            f"• اليوزرات Unknown: {len(self.unknown_usernames)}\n"
            f"• اليوزرات Invalid: {len(self.invalid_usernames)}\n"
            f"• سرعة الفحص: {speed:.2f} يوزر/ساعة\n"
            f"• مدة التشغيل: {str(uptime).split('.')[0]}\n"
            f"• وقت البدء: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}"
        )
        await event.reply(stats_message)

    async def show_help(self, event):
        """عرض رسالة المساعدة"""
        help_message = (
            f"{Colors.CYAN}⚡ أوامر البوت ⚡{Colors.RESET}\n\n"
            "`.فحص` - عرض حالة البوت الأساسية\n"
            "`.الاحصائيات` - إحصائيات مفصلة عن الأداء\n"
            "`.اليوزرات` - عرض اليوزرات المتاحة\n"
            "`.قنواتي` - عرض قنواتي مع اليوزرات\n"
            "`.تصفية` - إحصائيات اليوزرات المصفاة\n"
            "`.المجلد` - عرض موقع مجلد التصفية\n"
            "`.حذف_unknown` - حذف ملف unknown وإعادة فحص اليوزرات\n"
            "`.ايقاف` - إوقف البوت مؤقتاً\n"
            "`.تشغيل` - شغل البوت\n"
            "`.المساعدة` - عرض هذه الرسالة\n\n"
            f"📞 للمساعدة: {developer}\n\n"
            f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}"
        )
        await event.reply(help_message)

    async def show_usernames(self, event):
        """عرض اليوزرات المتاحة"""
        if not self.available_usernames:
            await event.reply("❌ لا توجد يوزرات متاحة حتى الآن")
            return
        
        usernames_list = "\n".join([f"• @{user}" for user in self.available_usernames[:10]])
        
        usernames_message = (
            f"{Colors.CYAN}📋 اليوزرات المتاحة{Colors.RESET}\n\n"
            f"{usernames_list}\n\n"
            f"• الإجمالي: {len(self.available_usernames)} يوزر\n"
        )
        
        if self.premium_usernames:
            premium_list = "\n".join([f"• ✨ @{user}" for user in self.premium_usernames[:5]])
            usernames_message += f"\n{Colors.YELLOW}اليوزرات المميزة:{Colors.RESET}\n{premium_list}\n"
        
        usernames_message += f"\n{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}"
        
        await event.reply(usernames_message)

    async def show_my_channels(self, event):
        """عرض قنوات المستخدم مع اليوزرات"""
        try:
            # الحصول على جميع الدردشات
            dialogs = await self.client.get_dialogs()
            
            # تصفية القنوات فقط
            channels = [dialog for dialog in dialogs if dialog.is_channel]
            
            if not channels:
                await event.reply("❌ ليس لديك أي قنوات")
                return
            
            message = f"{Colors.CYAN}📊 قنواتك ({len(channels)}){Colors.RESET}\n\n"
            
            for i, channel in enumerate(channels[:20], 1):  # عرض أول 20 قناة فقط
                entity = channel.entity
                username = f"@{entity.username}" if entity.username else "لا يوجد يوزر"
                message += f"{i}. {entity.title} - {username}\n"
            
            if len(channels) > 20:
                message += f"\n... وعرض {len(channels) - 20} قناة إضافية\n"
            
            message += f"\n{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}"
            
            await event.reply(message)
            
        except Exception as e:
            await event.reply(f"❌ حدث خطأ أثناء جلب القنوات: {str(e)}")

    async def stop_bot(self, event):
        """إيقاف البوت مؤقتاً"""
        self.is_running = False
        await event.reply("⏸️ تم إيقاف البوت مؤقتاً. استخدم `.تشغيل` لاستئناف العمل")

    async def start_bot(self, event):
        """تشغيل البوت"""
        self.is_running = True
        await event.reply("▶️ تم تشغيل البوت. جاري استئناف الفحص...")

    async def show_filter_stats(self, event):
        """عرض إحصائيات التصفية"""
        filtered_count = len(self.banned_usernames) + len(self.unknown_usernames) + len(self.invalid_usernames)
        
        stats_message = (
            f"{Colors.CYAN}🗑️ إحصائيات التصفية{Colors.RESET}\n\n"
            f"• إجمالي اليوزرات المصفاة: {filtered_count}\n"
            f"• اليوزرات Banned: {len(self.banned_usernames)}\n"
            f"• اليوزرات Unknown: {len(self.unknown_usernames)}\n"
            f"• اليوزرات Invalid: {len(self.invalid_usernames)}\n\n"
            f"• الملفات موجودة في مجلد: {self.filter_dir}\n\n"
            f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}"
        )
        await event.reply(stats_message)

    async def show_folder_location(self, event):
        """عرض موقع مجلد التصفية"""
        folder_path = os.path.abspath(self.filter_dir)
        message = (
            f"{Colors.CYAN}📁 موقع مجلد التصفية{Colors.RESET}\n\n"
            f"• المسار: {folder_path}\n\n"
            f"• الملفات الموجودة:\n"
        )
        
        try:
            files = os.listdir(self.filter_dir)
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(self.filter_dir, file)
                    size = os.path.getsize(file_path)
                    message += f"  - {file} ({size} بايت)\n"
        except Exception as e:
            message += f"  ❌ خطأ في قراءة الملفات: {e}\n"
        
        message += f"\n{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}"
        await event.reply(message)

    async def delete_unknown_file(self, event):
        """حذف ملف unknown وإعادة فحص اليوزرات"""
        try:
            if os.path.exists(self.unknown_file):
                # قراءة اليوزرات من ملف unknown
                with open(self.unknown_file, 'r', encoding='utf-8') as f:
                    unknown_usernames = [line.strip() for line in f if line.strip()]
                
                # حذف الملف
                os.remove(self.unknown_file)
                
                # إزالة اليوزرات من مجموعة unknown
                for username in unknown_usernames:
                    if username in self.unknown_usernames:
                        self.unknown_usernames.remove(username)
                    if username in self.filtered_usernames:
                        self.filtered_usernames.remove(username)
                
                await event.reply(f"✅ تم حذف ملف unknown وإزالة {len(unknown_usernames)} يوزر من القائمة السوداء")
            else:
                await event.reply("❌ ملف unknown غير موجود")
        except Exception as e:
            await event.reply(f"❌ حدث خطأ أثناء حذف الملف: {str(e)}")

    def generate_random_username(self):
        """إنشاء يوزر عشوائي"""
        # مجموعة من اليوزرات الشائعة
        common_prefixes = ['admin', 'user', 'account', 'official', 'team', 'news', 'channel', 'bot', 
                          'store', 'shop', 'market', 'service', 'support', 'help', 'info', 'contact']
        
        # مجموعة من الكلمات الشائعة
        common_words = ['king', 'queen', 'star', 'gold', 'silver', 'diamond', 'prime', 'elite', 
                       'pro', 'max', 'ultra', 'mega', 'super', 'hyper', 'alpha', 'beta', 'omega']
        
        # مجموعة من الأرقام الشائعة
        common_numbers = ['123', '2023', '2024', '007', '100', '999', '777', '888', '111', '222']
        
        # اختيار نمط عشوائي لليوزر
        pattern = random.choice([1, 2, 3, 4, 5])
        
        if pattern == 1:
            # كلمة + أرقام (مثل: star123)
            return random.choice(common_words) + random.choice(common_numbers)
        elif pattern == 2:
            # بادئة + كلمة (مثل: adminstar)
            return random.choice(common_prefixes) + random.choice(common_words)
        elif pattern == 3:
            # كلمة + كلمة (مثل: kingstar)
            return random.choice(common_words) + random.choice(common_words)
        elif pattern == 4:
            # بادئة + أرقام (مثل: admin123)
            return random.choice(common_prefixes) + random.choice(common_numbers)
        else:
            # أرقام + كلمة (مثل: 123star)
            return random.choice(common_numbers) + random.choice(common_words)

    async def check_username_availability(self, username):
        """فحص توفر اليوزر"""
        try:
            # تخطي اليوزرات المصفاة مسبقاً
            if username.lower() in self.filtered_usernames:
                return "filtered"
            
            # فحص اليوزر باستخدام API التيليجرام
            result = await self.client(CheckUsernameRequest(username=username))
            
            if result:
                return "available"
            else:
                return "taken"
                
        except errors.UsernameInvalidError:
            self.save_filtered_username(username, self.invalid_file)
            return "invalid"
        except errors.UsernameOccupiedError:
            return "taken"
        except errors.UsernameNotOccupiedError:
            return "available"
        except errors.UsernamePurchaseAvailableError:
            self.premium_usernames.append(username)
            return "premium"
        except Exception as e:
            error_msg = str(e).lower()
            if "banned" in error_msg:
                self.save_filtered_username(username, self.banned_file)
                return "banned"
            elif "unknown" in error_msg:
                self.save_filtered_username(username, self.unknown_file)
                return "unknown"
            else:
                self.save_filtered_username(username, self.unknown_file)
                return "unknown"

    async def claim_username(self, username):
        """محاولة حجز اليوزر"""
        try:
            # إنشاء قناة جديدة
            channel = await self.client(CreateChannelRequest(
                title=f"Channel {username}",
                about="Auto-created channel for username claiming",
                megagroup=False
            ))
            
            # تحديث يوزر القناة
            await self.client(UpdateChannelUsername(
                channel=channel.chats[0].id,
                username=username
            ))
            
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ فشل في حجز اليوزر {username}: {e}{Colors.RESET}")
            return False

    async def start_scanning(self):
        """بدء فحص اليوزرات"""
        print(f"{Colors.GREEN}🚀 بدء فحص اليوزرات...{Colors.RESET}")
        
        while self.is_running:
            try:
                # إنشاء يوزر عشوائي
                username = self.generate_random_username()
                
                # فحص اليوزر
                status = await self.check_username_availability(username)
                self.clicks += 1
                
                # معالجة النتيجة
                if status == "available":
                    self.available_usernames.append(username)
                    print(f"{Colors.GREEN}✅ @{username} - متاح{Colors.RESET}")
                    
                    # محاولة حجز اليوزر
                    if await self.claim_username(username):
                        print(f"{Colors.GREEN}🎉 تم حجز @{username} بنجاح!{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}❌ فشل في حجز @{username}{Colors.RESET}")
                        
                elif status == "premium":
                    print(f"{Colors.YELLOW}💰 @{username} - مميز (للبيع){Colors.RESET}")
                elif status == "taken":
                    print(f"{Colors.RED}❌ @{username} - محجوز{Colors.RESET}")
                elif status == "filtered":
                    # تم تخطيه لأنه مصفى مسبقاً
                    pass
                else:
                    # تم حفظه في الملف المناسب بالفعل في الدالة check_username_availability
                    pass
                
                # عرض الإحصائيات كل 100 فحص
                if self.clicks % 100 == 0:
                    current_time = datetime.now()
                    uptime = current_time - self.start_time
                    hours = uptime.total_seconds() / 3600
                    speed = self.clicks / hours if hours > 0 else 0
                    
                    print(f"{Colors.CYAN}📊 الإحصائيات: {self.clicks} فحص | {len(self.available_usernames)} متاح | {speed:.2f} يوزر/ساعة{Colors.RESET}")
                
                # تأخير عشوائي بين المحاولات لتجنب الحظر
                delay = random.uniform(0.5, 2.0)
                await asyncio.sleep(delay)
                
            except Exception as e:
                print(f"{Colors.RED}❌ خطأ غير متوقع: {e}{Colors.RESET}")
                await asyncio.sleep(5)  # انتظار أطول في حالة الخطأ

    async def run(self):
        """تشغيل البوت"""
        print(f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}")
        print(f"{Colors.YELLOW}⚡ Ultra Username Claimer ⚡{Colors.RESET}")
        print(f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}")
        print(f"{Colors.BLUE}📞 المطور: {developer}{Colors.RESET}")
        print(f"{Colors.BLUE}📢 قناة الدعم: {support_channel}{Colors.RESET}")
        print(f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}\n")
        
        # إنشاء مجلد الجلسات إذا لم يكن موجوداً
        os.makedirs("sessions", exist_ok=True)
        
        # محاولة التسجيل التلقائي أولاً
        if not await self.auto_login_with_session():
            # إذا فشل التسجيل التلقائي، استخدام الطريقة اليدوية
            if not await self.login_with_phone():
                print(f"{Colors.RED}❌ فشل تسجيل الدخول. الخروج...{Colors.RESET}")
                return
        
        # بدء فحص اليوزرات
        await self.start_scanning()

# تشغيل البوت
if __name__ == "__main__":
    bot = UltraUsernameClaimer()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.run())
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}⏹️  تم إيقاف البوت بواسطة المستخدم{Colors.RESET}")
    finally:
        if bot.client:
            loop.run_until_complete(bot.client.disconnect())
        loop.close()
