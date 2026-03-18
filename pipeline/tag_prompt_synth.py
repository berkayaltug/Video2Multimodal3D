import os
import sys

#Tag setinden baskın temayı tespit eder.
def generate_theme_from_tags(tags):
    theme_keywords = {
    "gothic": [
        "dark", "monster", "crimson", "cathedral", "cross", "black wings", "sharp fingernails", "pointy ears", "blood", "victorian", 
    # Mimari
    "cathedral", "gargoyle", "archway", "buttress", "spire", "cloister", "abbey", "vaulted", "tracery", "stonework",
    # Işık / Gölge
    "dim", "shadowy", "candlelit", "eerie glow", "chiaroscuro", "flickering light", "moonlit", "misty", "twilight", "darkness",
    # Renkler
    "crimson", "black", "charcoal", "deep purple", "blood red", "silver", "ivory", "ashen", "maroon", "indigo",
    # Moda / Stil
    "corset", "lace", "velvet", "leather", "victorian", "cloak", "fishnet", "boots", "choker", "gloves",
    # Duygusal Ton
    "melancholy", "haunting", "tragic", "brooding", "mysterious", "forlorn", "anguish", "solitude", "wistful", "tormented",
    # Doğa / Ortam
    "fog", "forest", "cemetery", "ruins", "ravens", "bats", "ivy", "graveyard", "crypt", "moon",
    # Objeler / Semboller
    "candle", "mirror", "cross", "skull", "rose", "coffin", "book", "clock", "window", "key",
    # Karakter / Arketip
    "vampire", "ghost", "witch", "specter", "doll", "nun", "fallen angel", "werewolf", "ghoul", "recluse",
    # Mimetik / Kavramlar
    "decay", "eternity", "curse", "relic", "obsession", "madness", "sanctuary", "lament", "echo", "veil"
    ],
    "cyberpunk": [
        "neon", "tech", "cybernetic", "visor", "cityscape", "glow", "augmented", "robot arm", "urban", "synthwave", 
    # Şehir ve Atmosfer
    "neon", "rainy street", "urban decay", "skyscraper", "back alley", "crowded city", "dystopia", "megacity", "gridlock", "digital haze",
    # Teknoloji / Donanım
    "cybernetic", "augmentation", "biotech", "nanotech", "interface", "implant", "hologram", "retinal scan", "exosuit", "dataspike",
    # Moda / Stil
    "leather jacket", "chrome visor", "tattoos", "combat boots", "punk hair", "stealth suit", "utility belt", "glitch aesthetic", "layered clothing", "mirror shades",
    # Renk Paleti / Işık
    "glow", "cyan", "magenta", "electric blue", "acid green", "infrared", "monochrome", "flicker", "blinking lights", "neon red",
    # Karakter / Arketip
    "hacker", "mercenary", "android", "netrunner", "corporate spy", "cyborg", "street samurai", "tech junkie", "drifter", "AI avatar",
    # Duygu / Ruh Hali
    "alienation", "rebellion", "loss", "chaos", "paranoia", "underground", "subversion", "anxiety", "transhuman", "identity crisis",
    # Ortam / Mekan
    "arcade", "data hub", "underground lab", "cyber cafe", "corporate tower", "black market", "slums", "VR lounge", "abandoned mall", "rooftop",
    # Objeler / Semboller
    "chip", "mask", "console", "firewall", "drone", "satellite", "server", "cords", "eyepiece", "antenna",
    # Sistem / Toplum
    "megacorp", "surveillance", "censorship", "techno-feudalism", "virtual rebellion", "network saturation", "autocracy", "protocol breach", "post-humanity", "digital currency"
    ],
    "school-life": [
        "uniform", "student", "reading", "book", "classroom", "chalkboard", "glasses", "tie", "desk", "library" , 
    # Mekan / Ortam
    "classroom", "locker", "schoolyard", "auditorium", "library", "hallway", "cafeteria", "gymnasium", "science lab", "clubroom",
    # Günlük Etkinlikler
    "studying", "recess", "group work", "exam", "homeroom", "lunch break", "school trip", "cleaning duty", "morning assembly", "late arrival",
    # Kıyafet / Stil
    "school uniform", "blazer", "tie", "backpack", "notebook", "textbook", "glasses", "sneakers", "hair clip", "watch",
    # Sosyal Dinamikler
    "friendship", "bullying", "rivalry", "love confession", "clique", "crush", "secret note", "student council", "childhood friend", "class rep",
    # Duygusal Ton
    "nostalgia", "awkwardness", "innocence", "embarrassment", "peer pressure", "loneliness", "daydream", "motivation", "growth", "happiness",
    # Zaman / Mevsimsel
    "spring festival", "summer homework", "exam season", "new semester", "graduation", "cherry blossoms", "yearbook", "final bell", "sunset", "snow day",
    # Kulüpler / Aktiviteler
    "art club", "sports team", "music club", "literature club", "science fair", "culture festival", "drama club", "game club", "school band", "debate team",
    # Karakter / Arketip
    "shy girl", "class clown", "senpai", "teacher", "transfer student", "bookworm", "athlete", "idol", "delinquent", "nerd",
    # Objeler / Simge
    "desk", "chalkboard", "bell", "eraser", "pencil case", "ID card", "lunchbox", "diary", "club flyer", "name tag"
    ],
    "military": [
        "gun", "uniform", "rifle", "camouflage", "tank", "helmet", "tactical gear", "battle", "flag", "explosion",
    # Üniforma / Donanım
    "camouflage", "helmet", "dog tags", "combat boots", "tactical vest", "goggles", "gloves", "beret", "armor", "utility belt",
    # Silah & Araç
    "rifle", "grenade", "tank", "drone", "missile", "sniper", "submachine gun", "artillery", "rocket launcher", "jeep",
    # Mekan / Ortam
    "bunker", "base camp", "battlefield", "training ground", "hangar", "war zone", "control room", "command post", "trench", "outpost",
    # Takım / Birlikler
    "squad", "platoon", "special forces", "commando", "infantry", "airborne unit", "navy SEAL", "medic", "drill sergeant", "intelligence agent",
    # Operasyon / Taktik
    "ambush", "stealth", "infiltration", "deployment", "flanking", "cover fire", "evacuation", "recon", "surveillance", "hostage rescue",
    # Duygusal Ton
    "discipline", "loyalty", "valor", "fear", "sacrifice", "honor", "tension", "courage", "command", "strategy",
    # Teknoloji / Sistem
    "radar", "satellite", "radio", "surveillance drone", "encrypted signal", "thermal scope", "cyber ops", "navigation system", "military AI", "supply chain",
    # Zaman / İklim
    "night raid", "dawn attack", "cold war", "desert ops", "urban warfare", "fog of war", "patrol mission", "rainfall", "snowfield", "heatwave",
    # Karakter / Arketip
    "general", "soldier", "sniper", "pilot", "operative", "spy", "prisoner of war", "civilian", "veteran", "mechanic",
    # Semboller / Objeler
    "medal", "flag", "ammunition box", "map", "radio device", "sentry gun", "battle log", "briefcase", "mission report", "dog tag"
    ],
    "fantasy": [
        "wizard", "magic", "staff", "dragon", "castle", "elf", "spell", "runes", "floating island", "sword",
    # Karakter / Irk
    "wizard", "elf", "dwarf", "orc", "knight", "sorceress", "dragon", "fairy", "golem", "necromancer",
    # Büyü / Güç
    "spell", "enchantment", "magic circle", "mana", "summoning", "curse", "elemental force", "alchemy", "divination", "portal",
    # Silah / Ekipman
    "sword", "staff", "bow", "shield", "armor", "dagger", "grimoire", "amulet", "ring", "cloak",
    # Mekan / Atmosfer
    "castle", "dungeon", "forest", "tower", "village", "cavern", "sky realm", "underground ruins", "enchanted glade", "floating island",
    # Canlılar / Varlıklar
    "griffin", "troll", "phoenix", "werewolf", "giant", "mermaid", "sprite", "centaur", "harpy", "leviathan",
    # Semboller / Objeler
    "scroll", "crystal", "runestone", "chalice", "map", "mirror", "orb", "torch", "book of spells", "key",
    # Zaman / Döngü
    "ancient prophecy", "eternal night", "solar eclipse", "age of heroes", "moonlight", "ritual dawn", "timeless realm", "seasonal bloom", "sunset over castle", "stars align",
    # Tema / Duygusal Ton
    "epic quest", "destiny", "betrayal", "rebirth", "heroism", "sacrifice", "mystery", "forbidden magic", "lost legacy", "legend",
    # Halklar / Sosyal Yapılar
    "kingdom", "tribe", "guild", "rebels", "court mage", "royalty", "assassins", "order of knights", "mages council", "wandering bard",
    # Işık / Renk / Aura
    "glow", "aura", "golden mist", "emerald light", "shadow fog", "firelight", "blue shimmer", "twilight haze", "silver dust", "radiant burst"
    ],
    "sci-fi": [
        "spaceship", "alien", "planet", "laser", "visor", "robot", "space suit", "hologram", "interstellar", "future",
    # Teknoloji / Sistem
    "artificial intelligence", "nanotech", "quantum computer", "cybernetics", "robotics", "terraforming", "biotech", "neural link", "hologram", "fusion core",
    # Mekan / Ortam
    "spaceship", "space station", "colony", "alien planet", "research lab", "cryopod", "control room", "asteroid field", "black hole", "galactic hub",
    # Karakter / Arketip
    "android", "pilot", "alien", "scientist", "space marine", "cyborg", "technomancer", "explorer", "AI entity", "clone",
    # Silah / Donanım
    "plasma gun", "energy sword", "shield generator", "gravity rifle", "exo armor", "force field", "ion cannon", "laser drone", "teleport device", "neural disruptor",
    # Duygusal Ton / Temalar
    "isolation", "discovery", "first contact", "betrayal", "fate", "transcendence", "paradox", "evolution", "identity", "survival",
    # Uzay / Kozmos
    "nebula", "galaxy", "wormhole", "supernova", "comet", "orbit", "dark matter", "cosmic radiation", "space-time", "gravity anomaly",
    # Zaman / Olay
    "dystopia", "uprising", "colonization", "reboot", "extinction event", "technocratic rule", "simulation", "interstellar war", "data breach", "revolution",
    # Objeler / Semboller
    "chip", "helmet", "console", "scanner", "artifact", "DNA strand", "star chart", "servo", "beacon", "encrypted file",
    # Renk / Işık / Stil
    "glow", "chrome", "electric blue", "infrared", "laser beam", "neon pulse", "black steel", "cyan shimmer", "red flare", "magnetic aura",
    # Toplum / Sistemler
    "megacorp", "space federation", "AI governance", "hive mind", "technocracy", "post-humanity", "VR network", "cyber resistance", "protocol layer", "data vault"
    ],
    "idol/anime pop": [
        "microphone", "stage", "sparkle", "idol", "music", "dance", "outfit", "hair ornament", "cheerful", "concert", 
    # Sahne / Performans
    "stage lights", "microphone", "spotlight", "live concert", "fan chant", "dance routine", "backup dancers", "pyrotechnics", "cheering crowd", "concert banner",
    # Moda / Stil
    "frilly skirt", "platform shoes", "accessories", "colorful tights", "hair bow", "sparkly outfit", "ribbon", "glitter", "kawaii fashion", "uniform costume",
    # Duygusal Ton
    "excitement", "nervousness", "joy", "confidence", "teamwork", "idol dreams", "passion", "overcoming doubt", "grateful", "inner shine",
    # Renk / Işık / Aura
    "neon pink", "pastel blue", "strobe light", "rainbow aura", "stage glow", "bubble sparkle", "warm yellow", "shimmer", "soft hue", "blinking effects",
    # Karakter / Arketip
    "center girl", "support idol", "rookie", "veteran", "solo act", "twin duo", "producer", "rival idol", "shy newcomer", "idol group leader",
    # Ortam / Mekan
    "rehearsal room", "audition hall", "green room", "idol agency", "recording studio", "photo shoot", "fan event", "TV show", "mall concert", "stadium",
    # Objeler / Semboller
    "glowstick", "idol poster", "signed photo", "fan letter", "idol diary", "headphones", "CD case", "idol badge", "photo frame", "music score",
    # Sosyal Dinamikler
    "fandom", "shipping", "vote ranking", "SNS post", "scandal rumor", "fan meetup", "idol handshake", "fanbase name", "support team", "viral clip",
    # Günlük Hayat / Yansıma
    "school idol", "morning practice", "late night edits", "group chat", "idol diet", "song writing", "stage fright", "schoolwork balance", "idol part-time job", "early debut",
    # Müzik / Performans
    "catchy chorus", "autotune", "dance beat", "signature pose", "theme song", "karaoke", "opening jingle", "closing theme", "album jacket", "idol anthem"
    ],
    "historical/japanese": [
        "kimono", "katana", "temple", "shrine", "paper lantern", "traditional", "samurai", "cherry blossoms", "tea", "wooden sandals",
    # Dönem / Zaman
    "Edo period", "Meiji era", "Taisho era", "Samurai age", "feudal Japan", "Sengoku period", "Heian court", "Warring States", "Imperial Japan", "Showa timeline",
    # Karakter / Arketip
    "samurai", "shogun", "ronin", "geisha", "ninja", "monk", "emperor", "daimyo", "villager", "court lady",
    # Kıyafet / Stil
    "kimono", "hakama", "obi", "geta", "sandals", "armor", "hairstick", "kabuto", "kataginu", "jingasa",
    # Mekan / Ortam
    "castle", "shrine", "tea house", "rice field", "mountain path", "temple", "old town", "samurai district", "garden", "wooden bridge",
    # Objeler / Semboller
    "katana", "scroll", "tatami", "bamboo", "lantern", "calligraphy", "sakura fan", "torii gate", "tea set", "sword stand",
    # Doğa / Manzara
    "cherry blossoms", "pine trees", "mount Fuji", "autumn leaves", "snowfall", "river stream", "misty valley", "stone lantern", "koi pond", "sunrise",
    # Sanat / Kültür
    "kabuki", "noh mask", "origami", "shodo", "haiku", "taiko drum", "ikebana", "bushido", "zen meditation", "bonsai",
    # Duygusal Ton / Tema
    "honor", "discipline", "silence", "tradition", "loyalty", "sadness", "fate", "regret", "devotion", "respect",
    # Mimari / Detay
    "paper wall", "sliding door", "rooftile", "wooden beam", "veranda", "pathway stones", "gate ornament", "thatched roof", "torii arch", "drum tower",
    # Olay / Durum
    "duel", "tea ceremony", "pilgrimage", "training", "harvest festival", "ancestral prayer", "scroll writing", "sword cleaning", "night patrol", "battle march"
    ],
    "post-apocalyptic": [
        "dust", "ruins", "gas mask", "destroyed buildings", "grime", "scars", "survivor", "mutant", "fire", "desolate",
    # Ortam / Zemin
    "ruins", "abandoned city", "cracked highway", "dust storm", "radioactive wasteland", "collapsed buildings", "empty shelter", "overgrown subway", "decaying mall", "flooded streets",
    # Doğa / Atmosfer
    "ash cloud", "toxic rain", "muted sunlight", "green haze", "dry heat", "muddy terrain", "dead forest", "frozen landscape", "scorched earth", "acid fog",
    # Karakter / Arketip
    "lone survivor", "scavenger", "warlord", "wanderer", "mechanic", "mutant", "raider", "child soldier", "masked rebel", "outcast healer",
    # Silah / Donanım
    "rusty rifle", "makeshift armor", "gas mask", "flare gun", "crossbow", "spiked bat", "blade gauntlet", "grenade pouch", "weaponized drone", "sling trap",
    # Duygusal Ton / Tema
    "survival", "isolation", "loss", "hope", "desperation", "trust", "decay", "betrayal", "redemption", "memory",
    # Araçlar / Ulaşım
    "modified motorcycle", "armored truck", "abandoned train", "supply cart", "solar buggy", "engine wreckage", "hover bike", "cargo sled", "fuel tank", "broken bridge",
    # Sistem / Toplum
    "barter system", "tribal clan", "military remnant", "tech cult", "anarchy zone", "resource war", "data ruins", "quarantine sector", "survivor camp", "lawless outpost",
    # Objeler / Semboller
    "ration pack", "water filter", "map fragment", "radio beacon", "biohazard symbol", "broken monitor", "survival guide", "dog tags", "burnt photo", "lockbox",
    # Zaman / Olaylar
    "fallout", "global blackout", "virus outbreak", "meteor impact", "solar flare", "extinction level event", "civil collapse", "last broadcast", "final migration", "lost archives",
    # Renk / Stil / Işık
    "sepia tone", "dark amber", "rust red", "grim light", "flickering neon", "green smoke", "charcoal haze", "cold blue", "gritty texture", "irregular shadow"
    ],
    "slice of life": [
        "kitchen", "living room", "casual wear", "smile", "morning light", "tea", "window", "plant", "quiet", "cozy",
    # Günlük Etkileşimler
    "morning routine", "breakfast", "walking to school", "shopping", "cooking", "cleaning", "doing laundry", "window watching", "grocery run", "bike ride",
    # Ortam / Mekan
    "kitchen", "living room", "cafe", "park bench", "school hallway", "train station", "bedroom", "convenience store", "bus stop", "apartment rooftop",
    # Zaman / Mevsim
    "spring breeze", "summer sunset", "rainy day", "quiet morning", "evening glow", "cold winter", "cherry blossom season", "afternoon nap", "snowfall", "golden hour",
    # Karakter / Arketip
    "shy student", "bookworm", "teacher", "childhood friend", "little sibling", "grandparent", "class president", "lonely girl", "quiet boy", "newcomer",
    # Duygu / Ton
    "nostalgia", "awkwardness", "warmth", "bittersweet", "comfort", "gentle silence", "simple joy", "tranquility", "hesitation", "soft sadness",
    # Kıyafet / Stil
    "school uniform", "casual hoodie", "oversized sweater", "raincoat", "scarf", "pajamas", "slippers", "hairpin", "glasses", "messy bun",
    # Objeler / Detaylar
    "mug", "bento box", "journal", "photo frame", "phone screen", "alarm clock", "calendar", "umbrella", "music player", "pencil case",
    # Sosyal Dinamikler
    "friendship", "study group", "family dinner", "neighbors", "shared secret", "group chat", "walk home", "birthday party", "farewell gift", "unexpected meeting",
    # Aktivite / Anlar
    "making tea", "watering plants", "hanging laundry", "stargazing", "petting cat", "yawning", "stretching", "flipping pages", "fixing hair", "watching clouds",
    # Işık / Renk / Atmosfer
    "soft lighting", "warm palette", "pastel colors", "flickering sunlight", "dim corner", "dust particles", "shadow cast", "slow motion", "gentle wind", "quiet ambiance"
    ],
    "sports": [
        "jersey", "ball", "running", "field", "goal", "sweat", "team", "stadium", "whistle", "jump",
    # Branşlar
    "soccer", "basketball", "baseball", "tennis", "volleyball", "swimming", "track", "gymnastics", "boxing", "karate",
    # Mekan / Ortam
    "stadium", "court", "field", "gym", "locker room", "track field", "arena", "pool", "training center", "dugout",
    # Karakter / Arketip
    "athlete", "coach", "team captain", "rookie", "opponent", "rival", "injured player", "referee", "cheerleader", "sports journalist",
    # Ekipman / Objeler
    "ball", "whistle", "net", "bat", "gloves", "racket", "goalpost", "helmet", "water bottle", "scoreboard",
    # Duygusal Ton / Tema
    "competition", "teamwork", "perseverance", "victory", "defeat", "sweat", "pressure", "comeback", "dedication", "underdog",
    # Giyim / Stil
    "jersey", "headband", "sports shoes", "tracksuit", "arm band", "knee pads", "uniform", "visor", "sportswear", "ankle tape",
    # Hareket / Aksiyon
    "run", "jump", "pass", "dribble", "dive", "kick", "score", "serve", "sprint", "block",
    # Zaman / Olay
    "tournament", "practice", "final match", "halftime", "championship", "warm-up", "injury time", "overtime", "team huddle", "podium ceremony",
    # Renk / Işık / Stil
    "bright lights", "sweat shine", "uniform color clash", "team flag", "score flash", "motion blur", "roaring crowd", "sunlit field", "shadow play", "slow motion",
    # Sosyal Dinamikler
    "supporters", "rivalry", "celebration", "locker talk", "strategy meeting", "sportsmanship", "cheering squad", "match analysis", "scouting", "idolization"
    ],
    "horror": [
        "ghost", "blood", "fog", "pale", "red eyes", "shadow", "abandoned", "creepy", "scratches", "scream",
    # Ortam / Mekan
    "abandoned house", "dark forest", "asylum", "graveyard", "basement", "haunted mansion", "deserted town", "foggy woods", "creaking hallway", "empty hospital",
    # Atmosfer / Işık
    "flickering light", "fog", "darkness", "red glow", "blood stain", "shadows", "broken mirror", "whispers", "dim candle", "cold wind",
    # Karakter / Arketip
    "ghost", "demon", "serial killer", "possessed girl", "cultist", "witch", "creature", "zombie", "masked figure", "vampire",
    # Objeler / Detaylar
    "chains", "doll", "Ouija board", "bloody knife", "skull", "book of curses", "photo album", "bone", "clock ticking", "crucifix",
    # Duygusal Ton / Tema
    "fear", "paranoia", "madness", "isolation", "pain", "torment", "screaming", "despair", "hysteria", "regret",
    # Ses / Hareket
    "footsteps", "creak", "heartbeat", "whispers", "scream", "breathing", "growl", "clawing", "echo", "snarl",
    # Görsel / Stil
    "grainy texture", "sepia tone", "black-and-white", "glitch effect", "distorted face", "shadow silhouette", "crimson overlay", "wet floor", "fog lens", "night vision",
    # Doğa / Varlıklar
    "rats", "crows", "spiders", "bats", "worms", "flesh", "tentacles", "rotting trees", "bones", "ashes",
    # Olay / Durum
    "possession", "ritual", "exorcism", "murder scene", "buried secret", "door slam", "mirror shatter", "trap", "paranormal activity", "vanishing",
    # Zaman / Sembol
    "full moon", "midnight", "devil’s hour", "Halloween", "old photograph", "rust", "grave", "blood trail", "warning sign", "cursed relic"
    ],
    "steampunk": [
        "gear", "brass", "goggles", "steam", "mechanical", "retro machine", "coat", "top hat", "metal arm", "pipe",
    # Mekanik & Donanım
    "gear", "cogwheel", "steam engine", "pressure valve", "boiler", "vacuum tube", "metal pipe", "lever", "piston", "copper coil",
    # Moda / Stil
    "top hat", "goggles", "corset", "waistcoat", "gloves", "tailcoat", "cravat", "lace-up boots", "pocket watch", "leather strap",
    # Objeler / Semboller
    "clockwork", "brass ornament", "mechanical bird", "spyglass", "airship compass", "gear pendant", "screwdriver", "lockpick", "monocle", "blueprint",
    # Ortam / Mimari
    "airship", "factory", "steam tunnel", "laboratory", "clock tower", "gaslight street", "iron bridge", "train station", "smoggy alley", "victorian cityscape",
    # Karakter / Arketip
    "inventor", "engineer", "explorer", "aristocrat", "mechanic", "airship captain", "rogue", "automaton", "mad scientist", "clockmaker",
    # Zaman / Dönem
    "alternate history", "industrial age", "Victorian era", "neo-renaissance", "coal age", "empire expansion", "steam revolution", "mechanized war", "retro future", "lost century",
    # Teknoloji / Yapı
    "steam cannon", "mechanical limbs", "gear-driven wings", "steam-powered armor", "smoke emitter", "oscillator", "vapor core", "magnetic stabilizer", "retro circuitry", "fluid injector",
    # Duygusal Ton / Tema
    "rebellion", "innovation", "curiosity", "decadence", "adventure", "mystery", "conspiracy", "eccentricity", "obsession", "restoration",
    # Renk / Stil / Işık
    "brass", "copper", "sepia", "polished chrome", "rust red", "golden hue", "metallic sheen", "shadow overlay", "smoke haze", "warm glow",
    # Hareket / Dinamikler
    "hissing", "clanking", "whirring", "steam burst", "spark", "gear rotation", "door slam", "crank turn", "leap through smoke", "mechanism failure"
    ]
    
}
    scores = {theme: len(set(tags) & set(keywords)) for theme, keywords in theme_keywords.items()}
    return max(scores, key=scores.get, default="original")

#Tag'lere göre en uygun anime/evren önerisi.
def suggest_input_series(tags):
    series_map = {
    "gothic": [
        "Bloodborne", "Castlevania", "Van Helsing", "Crimson Peak", "Dark Souls",
        "Penny Dreadful", "Vampire Hunter D", "Hellsing", "The Witcher (gothic mod), The Pale Blue Eye", "Interview with the Vampire", "Requiem: Berlin Gothic",
        "Sweeney Todd", "Edward Scissorhands", "Diablo IV", "Carnival Row"
    ],
    "cyberpunk": [
        "Cyberpunk 2077", "Blade Runner", "Ghost in the Shell", "Akira",
        "Altered Carbon", "Armitage III", "The Matrix", "Deus Ex", "Mardock Scramble, Armitage III", "Technolyze", "Observer", "Cloudpunk", "Serial Experiments Lain",
        "Love, Death & Robots (cyber arcs)", "Deus Ex"
    ],
    "medieval": [
        "Marco Polo (Netflix)", "The Pillars of the Earth", "Kingdom Come: Deliverance",
        "Northgard", "Medieval II: Total War", "Ritter Rost", "Beowulf"
    ],
    "school-life / anime": [
        "Fruits Basket", "Clannad", "My Youth Romantic Comedy", "Horimiya",
        "Toradora!", "K-On!", "Your Lie in April", "Love Live!", "Azumanga Daioh"
    ],
    "military / tactical": [
        "Call of Duty", "Metal Gear Solid", "Full Metal Panic!", "Valkyria Chronicles",
        "Girls und Panzer", "Tom Clancy's Rainbow Six", "Halo (military aspect)", "GATE, 86 (Eighty-Six)", "Jormungand", "SOCOM", "Battlefield V", "Strike Witches",
        "Tears of Steel", "Hell Let Loose"
    ],
    "fantasy / medieval": [
        "Lord of the Rings", "Elden Ring", "Game of Thrones", "The Witcher",
        "Dungeons & Dragons", "Berserk", "Record of Lodoss War", "Eragon", "Dragon Age, Elric of Melniboné", "Mistborn", "Legend of the Seeker", "Dragon's Dogma",
        "Magic: The Gathering", "Tales of Zestiria", "The Owl House"
    ],
    "idol / pop culture": [
        "Love Live!", "Idolmaster", "Vivy: Fluorite Eye’s Song", "Zombieland Saga",
        "Aikatsu!", "Uta no Prince-sama", "Show by Rock!!", "K-Pop aesthetics, BOFURI", "Healer Girl", "Symphogear", "AKB0048", "Parappa the Rapper",
        "PriPara", "Tokyo 7th Sisters"
    ],
    "historical / japanese": [
        "Rurouni Kenshin", "Mononoke", "Inuyasha (feudal Japan)", "Sekiro", "Mulan",
        "Samurai Champloo", "Yuki Yuna is a Hero (shrine theme)", "Touken Ranbu"
    ],
    "sci-fi / space opera": [
        "Mass Effect", "Star Wars", "Halo", "No Man’s Sky", "Legend of the Galactic Heroes",
        "Cowboy Bebop", "Expanse", "Star Trek", "Gundam Series, Andromeda", "Edge of Tomorrow", "Ender’s Game", "Outriders", "Scavengers Reign",
        "Apex Legends (space skins)", "Anthem"
    ],
    "post-apocalyptic / dystopia": [
        "Mad Max", "Metro 2033", "The Walking Dead", "Attack on Titan",
        "The Last of Us", "Fallout", "Ergo Proxy", "I Am Legend", "Trigun, Snowpiercer", "I Am Legend", "Children of Men", "Enslaved: Odyssey to the West",
        "The 100", "Divergent Series", "Love Death & Robots (post-apoc arcs)"
    ],
    "slice of life": [
        "Barakamon", "March Comes in Like a Lion", "Usagi Drop", "Shirobako",
        "Non Non Biyori", "Yuru Camp", "Flying Witch", "Natsume's Book of Friends, Shikimori's Not Just a Cutie", "Non Non Biyori", "A Place Further than the Universe",
        "Irodori", "My Roommate is a Cat", "Ojisan to Marshmallow", "March Comes In Like a Lion"
    ],
    "sports": [
        "Haikyuu!!", "Kuroko no Basket", "Yowamushi Pedal", "Captain Tsubasa",
        "Eyeshield 21", "Free!", "Ace of Diamond", "Ping Pong The Animation"
    ],
    "horror / suspense": [
        "Another", "Higurashi", "Silent Hill", "Paranoia Agent", "Junji Ito Collection",
        "Corpse Party", "Resident Evil", "The Promised Neverland", "Dark Water, Bram Stoker’s Dracula", "Callisto Protocol", "Outlast", "Fear Street",
        "Dead Space", "The Ritual", "The Medium"
    ],
    "steampunk": [
        "Steamboy", "Last Exile", "Howl's Moving Castle", "The Order: 1886",
        "Dishonored", "The Golden Compass", "Nausicaa (tech hybrid)", "Myst Series, Neo Steam", "SteamWorld Dig", "Clockwork Empires", "Abney Park universe",
        "Machinarium", "Professor Layton (steampunk elements)", "The Order: 1886"
    ],
    "mythology / spiritual": [
        "Okami", "Princess Mononoke", "Fate Series (Myth Servants)", "Hades",
        "God of War", "Onmyoji", "Izanami/Izanagi legends", "Journey", "Nioh, Journey to the West", "Genshin Impact (Liyue/Inazuma arcs)", "Purgatory",
        "Touhou Project", "Fire Emblem Echoes (divine theme)", "Amatsuki", "The Path"
    ],
    "nature/mystical": [
        "Kinoko no Yama", "Kujira no Kora", "Ever Oasis", "Children Who Chase Lost Voices",
        "Sky: Children of the Light", "Fe", "Rain World"
    ],
    ## 🎯 Superhero (Modern Cities, Powers, Hero Costumes)
    "superhero_modern": [
        "The Avengers", "Iron Man", "Spider-Man", "Ms. Marvel", "Shazam!", "Hawkeye", "The Boys", "Invincible", "Kick-Ass"
    ],

    ## 🦇 Superhero Gothic / Noir (Dark Themes, Urban Shadows)
    "superhero_noir": [
        "Batman", "The Dark Knight", "Gotham", "Watchmen", "Moon Knight", "Daredevil", "V for Vendetta", "The Punisher", "Jessica Jones"
    ],

    ## 🚀 Intergalactic Sci-Fi (Spaceships, Force, Alien Civilizations)
    "space_epic": [
        "Star Wars", "Dune", "Guardians of the Galaxy", "Star Trek", "The Mandalorian", "Rebel Moon", "Battlestar Galactica", "The Expanse"
    ],

    ## 💥 Multiverse / Cosmic Fantasy
    "multiverse_fantasy": [
        "Doctor Strange", "WandaVision", "Loki", "Everything Everywhere All At Once","The Flash", "Spider-Man: Across the Spider-Verse", "Rick and Morty", "Legion"
    ],

    ## 🧟 Post-Human / Mutants / Dystopian Superpowers
    "mutant_apocalypse": [
        "X-Men", "Logan", "Deadpool", "Brightburn", "Titans", "Chronicle","Umbrella Academy", "Project Power"
    ],

    ## 🏛️ Mythic Superheroes / Legendary Lineage
    "mythic_heroes": [
        "Thor", "Wonder Woman", "Aquaman", "Black Adam", "Eternals","Percy Jackson", "Hercules (Disney)", "300", "Clash of the Titans"
    ],

    ## 🌌 Animated Cosmic & Hero Worlds
    "animated_hero_universes": [
        "Big Hero 6", "Megamind", "The Incredibles", "Teen Titans", "Young Justice","Ben 10", "My Hero Academia", "One Punch Man"
    ],

    ## 🧝‍♂️ High Fantasy Legends (epic büyülü dünyalar, karakter ve kostüm ağırlıklı)
    "film_high_fantasy": [
        "The Lord of the Rings", "The Hobbit", "The Witcher (Netflix)", "Willow", "The Chronicles of Narnia", "Eragon", "Legend", "Stardust"
    ],

    ## 🪖 Heroic Historical Epics (mücadele, zırh, kahramanlık atmosferi)
    "film_historical_epic": [
        "Gladiator", "300", "Troy", "Kingdom of Heaven", "The Last Duel", "Robin Hood", "Ben-Hur", "Spartacus"
    ],

    ## ⚔️ Medieval Dark Fantasy (karanlık tonlu, savaşçı ve ritüel estetiği)
    "film_dark_medieval": [
        "Game of Thrones", "House of the Dragon", "The Northman", "Vikings", "The Green Knight", "Outlaw King", "The Bastard Executioner"
    ],

    ## 🚀 Futuristic Sci-Fi Worlds (ileri teknoloji, uzay, karakter takımı)
    "film_sci_fi": [
        "Star Wars", "Blade Runner", "Dune", "Interstellar", "Oblivion","The Expanse", "Passengers", "Edge of Tomorrow"
    ],

    ## 🧠 Philosophical Sci-Fi / AI Temaları
    "film_ai_philosophy": [
        "Ex Machina", "Her", "I, Robot", "Transcendence", "Chappie", "The Matrix", "After Yang", "Westworld"
    ],

    ## 🦸 Marvel Cinematic Universe (karakter stili, teknoloji, kostüm bazlı)
    "film_marvel_heroes": [
        "Iron Man", "Spider-Man", "Black Panther", "Doctor Strange", "Thor", "Ant-Man", "Avengers", "Captain America", "WandaVision", "Loki"
    ],

    ## 🦇 DC Cinematic Universe (karanlık kostüm, şehir, simge estetiği)
    "film_dc_heroes": [
        "Batman", "The Dark Knight", "Justice League", "Man of Steel", "Wonder Woman", "Aquaman", "Peacemaker", "The Flash"
    ],

    ## 🧟 Supernatural / Horror Characters (görsel efekt odaklı yaratık ve karanlık karakterler)
    "film_supernatural_horror": [
        "Stranger Things", "Penny Dreadful", "Crimson Peak", "Sleepy Hollow","The Witch", "The Haunting of Hill House", "Constantine", "The Sixth Sense"
    ],

    ## 🎩 Steampunk & Fantasy Hybrids (mekanik + büyü + stil fantezisi)
    "film_steampunk_fantasy": [
        "Mortal Engines", "Hugo", "The Golden Compass", "Howl’s Moving Castle","SteamBoy", "The League of Extraordinary Gentlemen"
    ]
}

    for key, series in series_map.items():
        if all(word in tags for word in key.split(", ")):
            return series
    return "original"