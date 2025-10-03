import os
import sys
import json
import openai
import random
import asyncio
import pyfiglet
import pyfiglet
import termcolor
import traceback
from pyrogram import Client
from getpass import getpass
from termcolor import colored
from datetime import datetime, timedelta

# Banner Configuration
COLORS = ["red", "green", "yellow", "blue", "magenta", "cyan", "white"]
BOT_NAME = "Tg Post"
OWNER_INFO = "@asadofc"
CHANNEL_INFO = "@DoDotPy"

# Global variables
used_posts = set()
generated_count = 0
scheduled_count = 0

# Topics and Emojis
TOPICS = [
    'love and relationships',
    'self worth',
    'desire and attraction',
    'life choices',
    'emotional honesty',
    'personal growth',
    'real connections'
]

EMOJIS = ['💞', '💟', '💫', '💝', '💗', '💌', '❤️‍🔥', '✨', '🔥', '💕', '💘', '🌙', '⚡', '💋', '🖤', '💜', '🤍', '❤️', '🌟', '💎']

FALLBACK_POSTS = [
    "Real love doesn't need filters",
    "Your vibe attracts your tribe",
    "Being yourself is the ultimate flex",
    "Life's too short for fake connections",
    "Be honest about what you want"
]

# Default character prompt
DEFAULT_CHARACTER_PROMPT = """Write a simple, honest social media post about {topic}.

Rules:
- Use simple everyday language
- Keep it under 12 words
- Be real and relatable, not fancy
- Share actual life experience or truth
- End with ONE emoji
- No quotes, no hashtags

Examples of the style:
- "Love isn't perfect, it's just choosing someone every day 💞"
- "Being yourself attracts the right people 💟"
- "Real connection feels easy, not exhausting 💫"
- "You deserve someone who makes you feel safe 💝"
- "Wanting someone isn't wrong, pretending is 💗"

Write only the post:"""

DEFAULT_SYSTEM_PROMPT = "You write simple, honest posts about life and relationships. Use everyday language. Keep it real and relatable."


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_banner(owner_username=None, channel_username=None):
    """Display the branded banner"""
    clear_screen()
    banner_text = pyfiglet.figlet_format(BOT_NAME, font='slant')
    print(colored(banner_text, random.choice(COLORS)))
    print(colored("="*45, "cyan"))
    print(colored(f"  Developer: {OWNER_INFO}", "magenta"))
    print(colored(f"  Channel: {CHANNEL_INFO}", "green"))
    print(colored("="*45, "cyan"))
    
    if owner_username and channel_username:
        print(colored(f"  User: @{owner_username}", "yellow"))
        print(colored(f"  Target Channel: @{channel_username}", "green"))
        print(colored("="*45, "cyan"))
    else:
        print(colored("  Telegram Post Automation Userbot", "white"))
        print(colored("="*45, "cyan"))
    print()


def get_input(prompt, default=None, required=True, is_password=False, multiline=False):
    """Get user input with optional default value"""
    if multiline:
        display_text = f"{prompt}\n"
        if default:
            display_text += f"Press Enter twice to use default, or type your custom prompt.\n"
        display_text += "Type your input (press Enter twice when done):\n"
        
        print(colored(display_text, "cyan"))
        lines = []
        while True:
            line = input()
            if line == "" and len(lines) > 0:
                break
            if line == "" and len(lines) == 0 and default:
                return default
            lines.append(line)
        return "\n".join(lines).strip()
    
    display_text = f"{prompt}"
    if default and not is_password:
        display_text += f" [{colored(default, 'yellow')}]"
    display_text += ": "
    
    if is_password:
        value = getpass(display_text)
    else:
        value = input(colored(display_text, "cyan"))
    
    if not value and default:
        return default
    elif not value and required:
        print(colored("❌ This field is required!", "red"))
        return get_input(prompt, default, required, is_password)
    return value.strip() if value else None


def get_character_prompts(config):
    """Get character persona and system prompts"""
    print()
    print(colored("🎭 AI Character Persona Configuration", "yellow", attrs=['bold']))
    print(colored("-"*25, "white"))
    
    print(colored("\n📝 Current Default Character Prompt:", "green"))
    print(colored("-"*25, "white"))
    print(colored(DEFAULT_CHARACTER_PROMPT.replace("{topic}", "[TOPIC]"), "white"))
    print(colored("-"*25, "white"))
    
    print(colored("\n💡 The prompt should include:", "yellow"))
    print("  • {topic} placeholder for random topics")
    print("  • Clear rules for the AI")
    print("  • Examples of the desired style")
    print("  • Instructions about format and length")
    print()
    
    custom_choice = input(colored("Do you want to use a custom character prompt? (y/n) [n]: ", "cyan")).lower()
    
    if custom_choice == 'y':
        config['CHARACTER_PROMPT'] = get_input(
            "\n📝 Enter your custom character prompt (use {topic} as placeholder)",
            default=None,
            required=True,
            multiline=True
        )
        
        print(colored("\n📝 Current Default System Prompt:", "green"))
        print(colored(DEFAULT_SYSTEM_PROMPT, "white"))
        print()
        
        system_choice = input(colored("Do you want to customize the system prompt too? (y/n) [n]: ", "cyan")).lower()
        if system_choice == 'y':
            config['SYSTEM_PROMPT'] = get_input(
                "\n📝 Enter your custom system prompt",
                default=None,
                required=True,
                multiline=True
            )
        else:
            config['SYSTEM_PROMPT'] = DEFAULT_SYSTEM_PROMPT
    else:
        config['CHARACTER_PROMPT'] = DEFAULT_CHARACTER_PROMPT
        config['SYSTEM_PROMPT'] = DEFAULT_SYSTEM_PROMPT
    
    return config


def get_credentials():
    """Get only credentials configuration"""
    print(colored("🔐 CREDENTIALS CONFIGURATION", "green", attrs=['bold']))
    print(colored("-"*25, "white"))
    print()
    
    credentials = {}
    
    # Telegram API Configuration
    print(colored("📱 Telegram API Configuration", "yellow", attrs=['bold']))
    print(colored("Get your API credentials from: https://my.telegram.org", "white"))
    print()
    
    credentials['API_ID'] = int(get_input("Enter API ID", required=True))
    credentials['API_HASH'] = get_input("Enter API Hash", required=True, is_password=True)
    credentials['PHONE'] = get_input("Enter Phone Number (with country code)", required=True)
    
    print()
    print(colored("🤖 AI Configuration", "yellow", attrs=['bold']))
    print(colored("Get your API key from: https://openrouter.ai", "white"))
    print()
    
    credentials['OPENROUTER_KEY'] = get_input("Enter OpenRouter API Key", required=True, is_password=True)
    
    print()
    print(colored("📢 Optional Defaults", "yellow", attrs=['bold']))
    credentials['DEFAULT_CHANNEL'] = get_input("Enter Default Channel Username (without @)", required=False)
    if credentials['DEFAULT_CHANNEL'] and not credentials['DEFAULT_CHANNEL'].startswith('@'):
        credentials['DEFAULT_CHANNEL'] = '@' + credentials['DEFAULT_CHANNEL']
    
    credentials['OWNER_USERNAME'] = get_input("Enter Your Telegram Username (without @)", required=False)
    
    return credentials


def get_runtime_configuration(credentials):
    """Get runtime configuration (not saved)"""
    display_banner()
    print(colored("⚙️  RUNTIME CONFIGURATION", "green", attrs=['bold']))
    print(colored("-"*25, "white"))
    print()
    
    config = credentials.copy()
    
    # Channel Configuration
    print(colored("📢 Channel Configuration", "yellow", attrs=['bold']))
    default_channel = credentials.get('DEFAULT_CHANNEL', '')
    channel_input = get_input(f"Enter Channel Username for this run (without @)", 
                             default=default_channel.replace('@', '') if default_channel else None, 
                             required=True)
    if not channel_input.startswith('@'):
        config['CHANNEL'] = '@' + channel_input
    else:
        config['CHANNEL'] = channel_input
    
    # AI Model Configuration
    print()
    print(colored("🤖 AI Model Configuration", "yellow", attrs=['bold']))
    config['OPENROUTER_MODEL'] = get_input("Enter AI Model", default="x-ai/grok-4-fast:free", required=False)
    
    # Get character prompts
    config = get_character_prompts(config)
    
    print()
    print(colored("📅 Schedule Configuration", "yellow", attrs=['bold']))
    
    # Date configuration with validation
    while True:
        start_date = get_input("Enter Start Date (YYYY-MM-DD)", default="2026-01-01", required=True)
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            config['START_DATE'] = start_date
            break
        except ValueError:
            print(colored("❌ Invalid date format! Please use YYYY-MM-DD", "red"))
    
    while True:
        end_date = get_input("Enter End Date (YYYY-MM-DD) or press Enter for auto", default="", required=False)
        if not end_date:
            config['END_DATE'] = ""
            break
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
            config['END_DATE'] = end_date
            break
        except ValueError:
            print(colored("❌ Invalid date format! Please use YYYY-MM-DD", "red"))
    
    config['POSTING_TIME'] = get_input("Enter Daily Posting Time (HH:MM)", default="06:00", required=False)
    
    print()
    print(colored("⚙️  Advanced Configuration (Press Enter for defaults)", "yellow", attrs=['bold']))
    
    config['MAX_PER_CHUNK'] = int(get_input("Max posts per chunk", default="30", required=False))
    config['SCHEDULE_DELAY'] = int(get_input("Delay between schedules (seconds)", default="2", required=False))
    config['CHUNK_DELAY'] = int(get_input("Delay between chunks (seconds)", default="300", required=False))
    config['BATCH_SIZE'] = int(get_input("Batch size for generation", default="15", required=False))
    config['BATCH_DELAY'] = int(get_input("Delay between batches (seconds)", default="1", required=False))
    
    return config


def save_config(credentials):
    """Save only credentials to file"""
    try:
        # Only save credentials, not runtime configurations
        save_data = {
            'API_ID': credentials.get('API_ID'),
            'API_HASH': credentials.get('API_HASH'),
            'PHONE': credentials.get('PHONE'),
            'OPENROUTER_KEY': credentials.get('OPENROUTER_KEY'),
            'DEFAULT_CHANNEL': credentials.get('DEFAULT_CHANNEL', ''),
            'OWNER_USERNAME': credentials.get('OWNER_USERNAME', '')
        }
        
        with open('scheduler_credentials.json', 'w') as f:
            json.dump(save_data, f, indent=2)
        print(colored("\n✅ Credentials saved to scheduler_credentials.json", "green"))
        return True
    except Exception as e:
        print(colored(f"\n⚠️ Could not save credentials: {e}", "yellow"))
        return False


def load_config():
    """Load only credentials from file if exists"""
    try:
        with open('scheduler_credentials.json', 'r') as f:
            credentials = json.load(f)
            # Ensure we only return credential fields
            return {
                'API_ID': credentials.get('API_ID'),
                'API_HASH': credentials.get('API_HASH'),
                'PHONE': credentials.get('PHONE'),
                'OPENROUTER_KEY': credentials.get('OPENROUTER_KEY'),
                'DEFAULT_CHANNEL': credentials.get('DEFAULT_CHANNEL', ''),
                'OWNER_USERNAME': credentials.get('OWNER_USERNAME', '')
            }
    except:
        return None


def build_prompt(config):
    topic = random.choice(TOPICS)
    prompt = config.get('CHARACTER_PROMPT', DEFAULT_CHARACTER_PROMPT)
    return prompt.format(topic=topic)


def create_fallback_post():
    return f"{random.choice(FALLBACK_POSTS)} {random.choice(EMOJIS)}"


async def generate_post(config, retry_count=0):
    global used_posts, generated_count
    
    try:
        prompt = build_prompt(config)
        system_prompt = config.get('SYSTEM_PROMPT', DEFAULT_SYSTEM_PROMPT)
        
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model=config['OPENROUTER_MODEL'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=80,
            temperature=0.8
        )
        
        content = response.choices[0].message.content.strip()
        content = content.replace('"', '').replace("'", "").strip()
        
        if not any(emoji in content for emoji in EMOJIS):
            content = f"{content} {random.choice(EMOJIS)}"
        
        if content in used_posts and retry_count < 2:
            print(f"  Duplicate found, retrying...")
            return await generate_post(config, retry_count + 1)
        
        used_posts.add(content)
        generated_count += 1
        return content
        
    except Exception as e:
        print(f"  Error: {e}")
        if retry_count < 2:
            await asyncio.sleep(2)
            return await generate_post(config, retry_count + 1)
        else:
            return create_fallback_post()


def calculate_date_range(config):
    start_date = datetime.strptime(config['START_DATE'], '%Y-%m-%d')
    
    if config['END_DATE'] and config['END_DATE'].strip():
        end_date = datetime.strptime(config['END_DATE'], '%Y-%m-%d')
    else:
        end_date = start_date + timedelta(days=364)
    
    max_end_date = start_date + timedelta(days=364)
    if end_date > max_end_date:
        print(f"Warning: End date adjusted to {max_end_date.strftime('%Y-%m-%d')}")
        end_date = max_end_date
    
    total_days = (end_date - start_date).days + 1
    return start_date, end_date, total_days


async def generate_all_content(config):
    global used_posts, generated_count
    
    # Reset globals for regeneration
    used_posts = set()
    generated_count = 0
    
    start_date, end_date, total_days = calculate_date_range(config)
    posts = []
    
    print(f"\nGenerating {total_days} posts...")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Posting time: {config['POSTING_TIME']}")
    print("-" * 45)
    
    for day in range(total_days):
        post_date = start_date + timedelta(days=day)
        
        print(f"\n[{day + 1}/{total_days}] {post_date.strftime('%Y-%m-%d %A')}")
        
        content = await generate_post(config)
        
        posts.append({
            'day_number': day + 1,
            'date': post_date.strftime('%Y-%m-%d'),
            'weekday': post_date.strftime('%A'),
            'content': content,
            'schedule_time': None
        })
        
        print(f"  ✅ {content}")
        
        if (day + 1) % config['BATCH_SIZE'] == 0 and day < total_days - 1:
            print(f"\nPausing {config['BATCH_DELAY']}s...")
            await asyncio.sleep(config['BATCH_DELAY'])
    
    print(f"\n✅ Generated {len(posts)} posts")
    return posts


def display_sample_posts(posts, num_samples=10):
    """Display sample posts for review"""
    print("\n" + colored("="*45, "cyan"))
    print(colored(f"📋 SAMPLE POSTS (First {num_samples})", "yellow", attrs=['bold']))
    print(colored("="*45, "cyan"))
    
    for i, post in enumerate(posts[:num_samples]):
        print(f"\n{colored(f'Day {post['day_number']}', 'green')} ({post['date']} - {post['weekday']})")
        print(f"  {colored('→', 'yellow')} {post['content']}")
    
    if len(posts) > num_samples:
        print(colored(f"\n... and {len(posts) - num_samples} more posts", "white"))
    
    print(colored("="*45, "cyan"))


async def review_and_confirm_posts(config, posts):
    """Allow user to review posts and decide next action"""
    while True:
        display_sample_posts(posts)
        
        print(colored("\n📝 POST REVIEW OPTIONS", "green", attrs=['bold']))
        print(colored("-"*25, "white"))
        print(colored("1.", "yellow") + " ✅ Posts look good - Start scheduling")
        print(colored("2.", "yellow") + " 🎭 Update character persona and regenerate")
        print(colored("3.", "yellow") + " 🔄 Regenerate with same persona")
        print(colored("4.", "yellow") + " 👀 View all posts")
        print(colored("5.", "yellow") + " ❌ Cancel and exit")
        print(colored("-"*25, "white"))
        
        choice = input(colored("\nEnter your choice (1-5): ", "cyan"))
        
        if choice == '1':
            return posts, True
        elif choice == '2':
            config = get_character_prompts(config)
            # Note: We don't save character prompts anymore
            print(colored("\n🔄 Regenerating posts with new persona...", "yellow"))
            posts = await generate_all_content(config)
        elif choice == '3':
            print(colored("\n🔄 Regenerating posts...", "yellow"))
            posts = await generate_all_content(config)
        elif choice == '4':
            print("\n" + colored("="*45, "cyan"))
            print(colored("📋 ALL GENERATED POSTS", "yellow", attrs=['bold']))
            print(colored("="*45, "cyan"))
            for post in posts:
                print(f"\n{colored(f'Day {post['day_number']}', 'green')} ({post['date']} - {post['weekday']})")
                print(f"  {colored('→', 'yellow')} {post['content']}")
            print(colored("="*45, "cyan"))
            input(colored("\nPress Enter to continue...", "cyan"))
        elif choice == '5':
            return posts, False
        else:
            print(colored("❌ Invalid choice. Please enter 1-5.", "red"))


def calculate_post_time(post_date_str, posting_time):
    post_date = datetime.strptime(post_date_str, '%Y-%m-%d')
    post_time = datetime.strptime(posting_time, '%H:%M').time()
    return datetime.combine(post_date, post_time)


def chunk_posts(posts, max_per_chunk):
    chunks = []
    for i in range(0, len(posts), max_per_chunk):
        chunks.append(posts[i:i + max_per_chunk])
    return chunks


async def schedule_all_posts(config, posts):
    global scheduled_count
    scheduled_count = 0  # Reset for new scheduling
    
    print(f"\nStarting Telegram scheduling...")
    print(f"Channel: {config['CHANNEL']}")
    print(f"Total posts: {len(posts)}")
    
    chunks = chunk_posts(posts, config['MAX_PER_CHUNK'])
    print(f"Chunks: {len(chunks)} (max {config['MAX_PER_CHUNK']} per chunk)")
    print("-" * 45)
    
    scheduled_posts = []
    
    client = Client(
        "year_scheduler", 
        api_id=config['API_ID'], 
        api_hash=config['API_HASH'], 
        phone_number=config['PHONE']
    )
    
    async with client:
        for chunk_idx, chunk in enumerate(chunks):
            print(f"\nChunk {chunk_idx + 1}/{len(chunks)} ({len(chunk)} posts)")
            print("-" * 45)
            
            for post in chunk:
                schedule_time = calculate_post_time(post['date'], config['POSTING_TIME'])
                
                now = datetime.now()
                days_ahead = (schedule_time - now).days
                
                if days_ahead > 365:
                    print(f"⚠️  Skipping {post['date']} - too far ahead")
                    post['error'] = f"Too far ahead ({days_ahead} days)"
                    scheduled_posts.append(post)
                    continue
                
                try:
                    result = await client.send_message(
                        config['CHANNEL'],
                        post['content'],
                        schedule_date=schedule_time
                    )
                    
                    post['schedule_time'] = schedule_time.isoformat()
                    post['message_id'] = result.id
                    scheduled_posts.append(post)
                    
                    scheduled_count += 1
                    
                    print(f"  [{scheduled_count}/{len(posts)}] ✅ {schedule_time.strftime('%Y-%m-%d %H:%M')}")
                    
                    await asyncio.sleep(config['SCHEDULE_DELAY'])
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"  [{post['day_number']}/{len(posts)}] ❌ {error_msg}")
                    post['error'] = error_msg
                    scheduled_posts.append(post)
            
            if chunk_idx < len(chunks) - 1:
                delay_minutes = config['CHUNK_DELAY'] / 60
                print(f"\nWaiting {delay_minutes:.1f} minutes before next chunk...")
                await asyncio.sleep(config['CHUNK_DELAY'])
    
    print(f"\n✅ Scheduled {scheduled_count}/{len(posts)} posts")
    
    failed = len(posts) - scheduled_count
    if failed > 0:
        print(f"⚠️  {failed} posts failed")
    
    return scheduled_posts


def save_schedule_log(config, posts):
    log_data = {
        'generated_at': datetime.now().isoformat(),
        'channel': config['CHANNEL'],
        'start_date': config['START_DATE'],
        'end_date': config['END_DATE'] if config['END_DATE'] else 'auto',
        'posting_time': config['POSTING_TIME'],
        'total_posts': len(posts),
        'scheduled_successfully': scheduled_count,
        'failed': len(posts) - scheduled_count,
        'character_prompt': config.get('CHARACTER_PROMPT', DEFAULT_CHARACTER_PROMPT),
        'posts': posts
    }
    
    filename = f"schedule_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Log saved: {filename}")
    return filename


async def main():
    try:
        # Check for existing credentials
        existing_credentials = load_config()
        
        if existing_credentials:
            display_banner(
                existing_credentials.get('OWNER_USERNAME', '').replace('@', ''),
                existing_credentials.get('DEFAULT_CHANNEL', '').replace('@', '')
            )
            print(colored("🔐 Found saved credentials!", "green"))
            use_existing = input(colored("\nUse saved credentials? (y/n): ", "cyan")).lower()
            
            if use_existing == 'y':
                credentials = existing_credentials
            else:
                credentials = get_credentials()
                save_config(credentials)
        else:
            display_banner()
            credentials = get_credentials()
            save_config(credentials)
        
        # Get runtime configuration (dates, prompts, etc.)
        config = get_runtime_configuration(credentials)
        
        # Display final banner with usernames
        display_banner(
            config.get('OWNER_USERNAME', '').replace('@', ''),
            config.get('CHANNEL', '').replace('@', '')
        )
        
        # Set up OpenAI/OpenRouter
        openai.api_base = "https://openrouter.ai/api/v1"
        openai.api_key = config['OPENROUTER_KEY']
        
        start_date, end_date, total_days = calculate_date_range(config)
        
        print(colored("\n✅ Configuration Ready", "green", attrs=['bold']))
        print(colored("-"*25, "white"))
        print(f"   Channel: {colored(config['CHANNEL'], 'yellow')}")
        print(f"   Start: {colored(start_date.strftime('%Y-%m-%d'), 'yellow')}")
        print(f"   End: {colored(end_date.strftime('%Y-%m-%d'), 'yellow')}")
        print(f"   Total: {colored(str(total_days) + ' days', 'yellow')}")
        print(f"   Time: {colored(config['POSTING_TIME'], 'yellow')}")
        print(f"   Max per chunk: {colored(str(config['MAX_PER_CHUNK']), 'yellow')}")
        
        print("\n" + colored("="*45, "cyan"))
        print(colored("STEP 1: GENERATING CONTENT", "green", attrs=['bold']))
        print(colored("="*45, "cyan"))
        
        posts = await generate_all_content(config)
        
        # Review posts and get user confirmation
        posts, should_schedule = await review_and_confirm_posts(config, posts)
        
        if not should_schedule:
            print(colored("\n⚠️  Scheduling cancelled by user", "yellow"))
            sys.exit(0)
        
        print("\n" + colored("="*45, "cyan"))
        print(colored("STEP 2: SCHEDULING TO TELEGRAM", "green", attrs=['bold']))
        print(colored("="*45, "cyan"))
        
        scheduled_posts = await schedule_all_posts(config, posts)
        
        log_file = save_schedule_log(config, scheduled_posts)
        
        print("\n" + colored("="*45, "cyan"))
        print(colored("✨ COMPLETE!", "green", attrs=['bold', 'blink']))
        print(colored("="*45, "cyan"))
        print(colored("📊 Summary:", "yellow", attrs=['bold']))
        print(f"   Total posts: {colored(str(total_days), 'green')}")
        print(f"   Scheduled: {colored(str(scheduled_count), 'green')}")
        print(f"   Failed: {colored(str(total_days - scheduled_count), 'red' if total_days - scheduled_count > 0 else 'green')}")
        print(f"   Log file: {colored(log_file, 'cyan')}")
        print(f"\n🎯 Posts scheduled from {colored(start_date.strftime('%Y-%m-%d'), 'yellow')} to {colored(end_date.strftime('%Y-%m-%d'), 'yellow')}")
        print(f"⏰ Daily at {colored(config['POSTING_TIME'], 'yellow')}")
        print(colored("\n✅ You can close this now", "green", attrs=['bold']))
        print(colored("="*45, "cyan") + "\n")
        
    except KeyboardInterrupt:
        print(colored("\n\n⚠️  Stopped by user", "yellow"))
        sys.exit(0)
    except Exception as e:
        print(colored(f"\n\n❌ Error: {e}", "red"))
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__": 
    asyncio.run(main())