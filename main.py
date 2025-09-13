import os, json, asyncio, re, string, random, aiohttp, time
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
from telethon.tl.functions.channels import DeleteChannelRequest, EditPhotoRequest
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
                
                # إنشاء عميل جديد
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

    async def stop_bot(self, event):
        """إيقاف البوت"""
        self.is_running = False
        await event.reply("⏸️ تم إيقاف البوت مؤقتاً")
    
    async def start_bot(self, event):
        """تشغيل البوت"""
        self.is_running = True
        await event.reply("▶️ تم تشغيل البوت")

    async def show_filter_stats(self, event):
        """عرض إحصائيات التصفية"""
        stats_message = (
            f"{Colors.CYAN}🗑️ إحصائيات اليوزرات المصفاة{Colors.RESET}\n\n"
            f"• اليوزرات المبندة: {len(self.banned_usernames)}\n"
            f"• اليوزرات المجهولة: {len(self.unknown_usernames)}\n"
            f"• اليوزرات غير الصالحة: {len(self.invalid_usernames)}\n\n"
            f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}"
        )
        await event.reply(stats_message)

    async def show_folder_location(self, event):
        """عرض موقع مجلد التصفية"""
        abs_path = os.path.abspath(self.filter_dir)
        
        folder_message = (
            f"{Colors.CYAN}📁 معلومات مجلد التصفية{Colors.RESET}\n\n"
            f"• المسار: `{abs_path}`\n"
            f"• اليوزرات المبندة: {len(self.banned_usernames)}\n"
            f"• اليوزرات المجهولة: {len(self.unknown_usernames)}\n"
            f"• اليوزرات غير الصالحة: {len(self.invalid_usernames)}\n\n"
            f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}"
        )
        await event.reply(folder_message)

    async def delete_unknown_file(self, event):
        """حذف ملف unknown وإعادة تحميل القائمة"""
        try:
            if os.path.exists(self.unknown_file):
                # حفظ عدد اليوزرات قبل الحذف
                count_before = len(self.unknown_usernames)
                
                # حذف الملف
                os.remove(self.unknown_file)
                
                # إزالة اليوزرات من الذاكرة
                self.filtered_usernames -= self.unknown_usernames
                self.unknown_usernames = set()
                
                await event.reply(f"✅ تم حذف ملف unknown بنجاح\n• عدد اليوزرات المحذوفة: {count_before}\n• يمكن إعادة فحص هذه اليوزرات الآن")
            else:
                await event.reply("❌ ملف unknown غير موجود")
        except Exception as e:
            await event.reply(f"❌ خطأ في حذف الملف: {e}")

    def user_gen(self, pattern):
        """توليد يوزرنيم عشوائي"""
        fixed_digits = {}
        fixed_letters = {}
        result = []
        repeat_pattern = re.compile(r'(\w|\#|\*|\$)(\d+)')

        def process_char(char):
            if char == '0':
                return str(random.randint(0, 9))
            elif char in ['1', '2', '3']:
                if char not in fixed_digits:
                    fixed_digits[char] = str(random.randint(0, 9))
                return fixed_digits[char]
            elif char == 'a':
                return random.choice(string.ascii_letters + string.digits)
            elif char == '#':
                if '#' not in fixed_letters:
                    fixed_letters['#'] = random.choice(string.ascii_letters)
                return fixed_letters['#']
            elif char == '*':
                if '*' not in fixed_letters:
                    fixed_letters['*'] = random.choice(string.ascii_letters)
                return fixed_letters['*']
            elif char == 'j':
                if 'j' not in fixed_letters:
                    fixed_letters['j'] = random.choice(string.ascii_letters)
                return fixed_letters['j']
            elif char == '$':
                if '$' not in fixed_letters:
                    fixed_letters['$'] = random.choice(string.ascii_letters)
                return fixed_letters['$']
            else:
                return char

        i = 0
        while i < len(pattern):
            match = repeat_pattern.match(pattern, i)
            if match:
                char = match.group(1)
                repeat_count = int(match.group(2))
                result.extend([process_char(char)] * repeat_count)
                i += len(match.group(0))
            else:
                result.append(process_char(pattern[i]))
                i += 1
        return ''.join(result)

    async def init_session(self):
        """تهيئة جلسة aiohttp"""
        self.session = aiohttp.ClientSession()

    async def generate_username_async(self):
        """توليد اليوزرنيم بشكل غير متزامن"""
        await self.init_session()
        numb = 0
        patterns = [      "$**##",
            "##**$",
            "##$**",

 ]
        
        while True:
            if not self.is_running:
                await asyncio.sleep(1)
                continue
                
            user = self.user_gen(random.choice(patterns))
            
            # تخطي اليوزرات المعيبة المسبقة
            if user.lower() in self.filtered_usernames:
                continue
            
            # فلترة اليوزرات غير المرغوبة
            if len(user) < 3 or any(c in user.lower() for c in ""):
                continue
              
            try:
                # الفحص السريع عبر Fragment أولاً
                fragment_result = await self.Chack_UserName_Fragment_Async(user)
                
                if fragment_result == "Unavailable":
                    # إذا كان متاحاً على Fragment، نتحقق من التليجرام
                    await self.Chack_UserName_TeleGram(user)
                elif fragment_result == "taken":
                    print(f"{Colors.RED}-[{numb}] UserName is Taken [@{user}]{Colors.RESET}")
                elif fragment_result == "available":
                    print(f"{Colors.YELLOW}-[{numb}] UserName is Sold [@{user}]{Colors.RESET}")
                else:
                    print(f"{Colors.MAGENTA}-[{numb}] UserName is unknown [@{user}]{Colors.RESET}")
                    self.save_filtered_username(user, self.unknown_file)
                        
            except Exception as e:
                print(f"{Colors.RED}-[{numb}] Error: {e} [@{user}]{Colors.RESET}")
            
            numb += 1
            self.clicks += 1
            await asyncio.sleep(0.1)

    async def Chack_UserName_Fragment_Async(self, user):
        """فحص Fragment بشكل غير متزامن"""
        try:
            url = f"https://fragment.com/username/{user}"
            async with self.session.get(url, timeout=3) as response:
                text = await response.text()
                
                if '<span class="tm-section-header-status tm-status-taken">Taken</span>' in text:
                    return "taken"
                elif '<span class="tm-section-header-status tm-status-unavail">Sold</span>' in text:
                    return "available"
                elif '<div class="table-cell-status-thin thin-only tm-status-unavail">Unavailable</div>' in text:
                    return "Unavailable"
                else:
                    return "unknown"
        except:
            return "unknown"

    async def Chack_UserName_TeleGram(self, user):
        """فحص اليوزر على التليجرام"""
        try:
            tele = await self.client(CheckUsernameRequest(username=user))
            
            if tele:
                print(f"{Colors.GREEN}- UserName is Available (CheckUsernameRequest) [{user}]{Colors.RESET}")
                
                # فحص سريع للتأكد من عدم وجود حظر
                is_valid = await self.quick_advanced_check(user)
                
                if is_valid:
                    self.available_usernames.append(user)
                    
                    # التحقق إذا كان اليوزر مميزاً (3 أحرف أو أقل)
                    if len(user) <= 3:
                        self.premium_usernames.append(user)
                        print(f"{Colors.CYAN}🎉 تم العثور على يوزر مميز: @{user}{Colors.RESET}")
                    
                    # إنشاء القناة مباشرة
                    await self.save_username_to_channel(user)
                    
                    # إرسال إشعار
                    text = f"• New UserName Available.\n• UserName : @{user} ."
                    await self.client.send_message('me', text)
                else:
                    print(f"{Colors.RED}- UserName is Banned or Restricted [@{user}]{Colors.RESET}")
                      
        except errors.rpcbaseerrors.BadRequestError:
            print(f"{Colors.RED}- UserName is Band [@{user}]{Colors.RESET}")
            self.save_filtered_username(user, self.banned_file)
            return
        except errors.FloodWaitError as timer:
            num = int(timer.seconds)
            print(f"{Colors.RED}- Error Account Flood (CheckUsernameRequest) Time [{num}]\n- UserName [{user}]{Colors.RESET}")
            while num > 0:
                print(f"{Colors.YELLOW}The flood will end after: [{num}]{Colors.RESET}", end="\r")
                await asyncio.sleep(1)
                num -= 1
            return
        except errors.UsernameInvalidError:
            print(f"{Colors.RED}- UserName is Invalid [@{user}]{Colors.RESET}")
            self.save_filtered_username(user, self.invalid_file)
            return
        except Exception as e:
            print(f"{Colors.RED}- Error in Telegram check: {e} [@{user}]{Colors.RESET}")
            return

    async def quick_advanced_check(self, user):
        """فحص سريع للتأكد من أن اليوزر غير مبند"""
        try:
            await self.client.get_entity(user)
            return False
        except ValueError:
            return True
        except Exception:
            return True

    async def get_video_from_channel(self, user):
        """تحميل الفيديو من القناة"""
        try:
            video_channel = await self.client.get_entity('m23333')
            messages = await self.client.get_messages(video_channel, limit=5)
              
            for message in messages:
                if message.media and hasattr(message.media, 'document'):
                    for attr in message.media.document.attributes:
                        if isinstance(attr, types.DocumentAttributeVideo):
                            video_path = await self.client.download_media(message, file=f'Video_{user}.mp4')
                            print(f"{Colors.GREEN}- تم تحميل الفيديو بنجاح{Colors.RESET}")
                            return video_path
              
            print(f"{Colors.YELLOW}- لم يتم العثور على أي فيديو{Colors.RESET}")
            return None
              
        except Exception as e:
            print(f"{Colors.RED}- فشل في تحميل الفيديو: {e}{Colors.RESET}")
            return None

    async def save_username_to_channel(self, user):
        """حفظ اليوزر عن طريق إنشاء قناة"""
        try:
            # إنشاء القناة الجديدة
            r = await self.client(CreateChannelRequest(
                title=f"New user 🐊[{user}]",
                about=f"\nMe • \nCHANNAL • @m23333\n Owner  • {developer} {datetime.now().strftime('%H:%M:%S')}\n",
                megagroup=False
            ))
              
            new_channel = r.chats[0]
              
            # تعيين اليوزرنيم للقناة الجديدة
            try:
                await self.client(functions.channels.UpdateUsernameRequest(channel=new_channel, username=user))
                print(f"{Colors.GREEN}- تم تعيين اليوزرنيم @{user} للقناة بنجاح{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}- فشل في تعيين اليوزرنيم: {e}{Colors.RESET}")
                return
              
            # الحصول على صورة القناة
            try:
                source_channel = await self.client.get_entity('rrkkkrr')
                photos = await self.client.get_profile_photos(source_channel, limit=1)
                if photos:
                    photo_path = await self.client.download_media(photos[0], file=f'channel_photo_{user}.jpg')
                    uploaded_file = await self.client.upload_file(photo_path)
                    input_photo = types.InputChatUploadedPhoto(file=uploaded_file)
                      
                    await self.client(EditPhotoRequest(
                        channel=new_channel,
                        photo=input_photo
                    ))
                    print(f"{Colors.GREEN}- تم تعيين صورة القناة بنجاح{Colors.RESET}")
                    os.remove(photo_path)
            except Exception as e:
                print(f"{Colors.YELLOW}- خطأ في تعيين صورة القناة: {e}{Colors.RESET}")
              
            # تحميل الفيديو من القناة
            video_path = await self.get_video_from_channel(user)
              
            bio_list = [" @m23333 ☘️"]
            bio = random.choice(bio_list)
              
            # إرسال الفيديو مع الترجمة إلى القناة الجديدة
            caption = (
                f'• ✧ ɴᴇᴡ ᴜsᴇʀ ✧  • [@{user}] .\n'
                f'• ✦ Oᴡɴᴇʀ ✦ : {developer}  .\n'
                f'• ⌬ 𝑪𝒍𝒊𝒄𝒌 ⌬ : {self.clicks}\n\n'
                f'• Bio • {bio}'
            )
              
            if video_path and os.path.exists(video_path):
                await self.client.send_file(new_channel, file=video_path, caption=caption)
                print(f"{Colors.GREEN}- تم إرسال الفيديو إلى القناة @{user}{Colors.RESET}")
            else:
                await self.client.send_message(new_channel, caption)
                print(f"{Colors.GREEN}- تم إرسال الرسالة إلى القناة @{user}{Colors.RESET}")
              
            # إرسال رسالة إضافية مع وقت المطالبة
            await self.client.send_message(new_channel, f' — Claim DataTime  - {datetime.now().strftime("%Y:%H:%M:%S")}')
              
            # إرسال رسالة إلى المطور
            try:
                ra_aa_message = f"""• ✧ ɴᴇᴡ ᴜsᴇʀ ✧  • [@{user}] .

• ✦ Oᴡɴᴇʀ ✦ : {developer}  .

• ⌬ 𝑪𝒍𝒊𝒄𝒌 ⌬ : {self.clicks}

• Bio •  @m23333 ☘️"""
                if video_path and os.path.exists(video_path):
                    await self.client.send_file(developer, video_path, caption=ra_aa_message)
                    print(f"{Colors.GREEN}- تم إرسال الفيديو إلى {developer}{Colors.RESET}")
                else:
                    await self.client.send_message(developer, ra_aa_message)
                    print(f"{Colors.GREEN}- تم إرسال الرسالة إلى {developer}{Colors.RESET}")
                      
            except Exception as e:
                print(f"{Colors.RED}- فشل في إرسال رسالة إلى {developer}: {e}{Colors.RESET}")
              
            # حذف الملف المؤقت
            if video_path and os.path.exists(video_path):
                os.remove(video_path)
              
        except Exception as e:
            if "too many public channels" in str(e):
                print(f"{Colors.RED}- Error (too many public channels) save_username_to_channel, UserName: [@{user}]\n Error : [{e}]{Colors.RESET}")
                await self.client.send_message('me', f"- Error (too many public channels) save_username_to_channel, UserName: [@{user}]\n- Error : [{e}]")
            elif "A wait" in str(e):
                time_flood = e.seconds
                print(f"{Colors.RED}- Error Account Flood (caused by UpdateUsernameRequest) Time [{time_flood}]\n- UserName [{user}]{Colors.RESET}")
                while time_flood > 0:
                    print(f"{Colors.YELLOW}The flood will end after: [{time_flood}]{Colors.RESET}", end="\r")
                    await asyncio.sleep(1)
                    time_flood -= 1
            else:
                print(f"{Colors.RED}- Error save_username_to_channel, UserName: [@{user}]\n Error : [{e}]{Colors.RESET}")
                await self.client.send_message('me', f"- Error save_username_to_channel, UserName: [@{user}]\n- Error : [{e}]")

    async def run(self):
        """تشغيل البوت الرئيسي"""
        # إنشاء مجلد الجلسات
        os.makedirs("sessions", exist_ok=True)
        
        # محاولة التسجيل التلقائي أولاً
        if not await self.auto_login_with_session():
            # إذا فشل التسجيل التلقائي، استخدم الطريقة اليدوية
            print(f"{Colors.YELLOW}⚠️  الانتقال إلى تسجيل الدخول اليدوي...{Colors.RESET}")
            if not await self.login_with_phone():
                return
        
        # بدء توليد اليوزرنيم
        print(f"{Colors.GREEN}🚀 بدء البحث عن اليوزرات...{Colors.RESET}")
        await self.generate_username_async()

async def main():
    """الدالة الرئيسية"""
    # تنظيف الشاشة
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # عرض البانر
    print(f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}")
    print(f"{Colors.YELLOW}     ⚡ Ultra Username Claimer ⚡{Colors.RESET}")
    print(f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}")
    print(f"{Colors.WHITE}     المطور: {developer}{Colors.RESET}")
    print(f"{Colors.WHITE}     القناة: {support_channel}{Colors.RESET}")
    print(f"{Colors.CYAN}✦ ━━━━━━━ ⟡ ━━━━━━━ ✦{Colors.RESET}")
    
    # تشغيل البوت
    bot = UltraUsernameClaimer()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())