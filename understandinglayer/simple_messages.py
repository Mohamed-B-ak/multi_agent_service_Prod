"""
Expanded Q&A Dataset for Multi-Agent System
Format: message : response
Languages: Arabic (AR), English (EN), French (FR) with dialects
"""

qa_pairs = {
    # ============== GREETINGS ==============
    
    # English Greetings
    "hello": "Hello! How can I help you today?",
    "hi": "Hi there! What can I do for you?",
    "hey": "Hey! How's it going?",
    "heya": "Heya! What's up?",
    "hello there": "Hello there! How may I assist you?",
    "hi there": "Hi! I'm here to help!",
    "hey there": "Hey there! What brings you here?",
    "good morning": "Good morning! Hope you're having a great day!",
    "morning": "Morning! How can I assist you?",
    "good afternoon": "Good afternoon! What brings you here today?",
    "afternoon": "Good afternoon! How's your day going?",
    "good evening": "Good evening! How may I help you?",
    "evening": "Evening! What can I do for you?",
    "greetings": "Greetings! I'm here to assist you.",
    "howdy": "Howdy! What can I do for you today?",
    "yo": "Hey there! What's up?",
    "sup": "Hey! What can I help you with?",
    "wassup": "Hey! How can I help?",
    "what's up": "Not much! How can I assist you today?",
    "whats up": "Hey! What do you need help with?",
    "hiya": "Hi there! How are you doing?",
    "aloha": "Aloha! Welcome! How can I help?",
    "hey buddy": "Hey there! What can I do for you?",
    "hello friend": "Hello friend! How can I assist you today?",
    "good day": "Good day to you! How may I help?",
    "g'day": "G'day mate! What can I do for you?",
    "top of the morning": "And the rest of the day to you! How can I help?",
    "holla": "Hey! What's going on?",
    "hey yo": "Hey! What do you need?",
    "hello everyone": "Hello! Welcome! How can I help?",
    "hi everyone": "Hi there! How can I assist you all?",
    "hey guys": "Hey! What can I help you with?",
    "hello guys": "Hello! How can I be of service?",
    
    # Arabic Greetings (with transliteration comments)
    "مرحبا": "أهلاً وسهلاً! كيف يمكنني مساعدتك؟",  # marhaba
    "مرحباً": "مرحباً بك! كيف أقدر أخدمك؟",
    "مرحبتين": "مراحب! شو بتحتاج؟",  # marhabtein
    "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته! كيف حالك؟",  # assalamu alaikum
    "سلام عليكم": "وعليكم السلام! أهلاً بك!",
    "السلام": "وعليكم السلام! تفضل!",
    "سلام": "سلام! كيف يمكنني خدمتك؟",  # salam
    "أهلا": "أهلاً بك! كيف أقدر أساعدك؟",  # ahlan
    "أهلاً": "أهلاً وسهلاً! إيش تحتاج؟",
    "أهلا وسهلا": "أهلاً بك! نورت!",
    "أهلين": "أهلين! كيفك؟",  # ahlein
    "هلا": "هلا والله! شو بدك؟",  # hala
    "يا هلا": "يا هلا ومرحبا! كيف أقدر أخدمك؟",  # ya hala
    "هلا والله": "هلا بك! تحت أمرك!",
    "صباح الخير": "صباح النور! كيف يمكنني مساعدتك اليوم؟",  # sabah al-khayr
    "صباح الفل": "صباح النور والسرور! إيش أقدر أسوي لك؟",  # Egyptian
    "صباح الورد": "صباح الياسمين! كيف حالك اليوم؟",
    "صباح النور": "صباح الخيرات! شو الأخبار؟",
    "صباحو": "صباح الخيرات! كيفك اليوم؟",  # Levantine
    "صباح الصباح": "يا صباح الخير! شو بتحتاج؟",
    "مساء الخير": "مساء النور! كيف يمكنني مساعدتك؟",  # masa' al-khayr
    "مساء الفل": "مساء الورد! إيه أخبارك؟",  # Egyptian
    "مساء النور": "مساء الخيرات! تحت أمرك!",
    "مساء الورد": "مساء الياسمين! كيف أساعدك؟",
    "مساؤك سعيد": "مساء السعادة! كيف حالك؟",
    "تحية طيبة": "وتحياتي لك! كيف أخدمك؟",
    "تحياتي": "أهلاً بك! تحياتي لك أيضاً!",
    "مرحباً يا صديق": "أهلاً يا صديقي! كيف حالك؟",
    "السلام عليكم جميعاً": "وعليكم السلام جميعاً! أهلاً بكم!",
    "كيفك": "الحمد لله بخير! كيف أقدر أساعدك؟",  # kifak
    "شو الأخبار": "الحمد لله تمام! شو بتحتاج؟",  # Levantine
    "إزيك": "الحمد لله كويس! عايز إيه؟",  # Egyptian
    "إزيكم": "الحمد لله تمام! عايزين إيه؟",  # Egyptian plural
    "لاباس": "الحمد لله بخير! واش تحتاج؟",  # Maghrebi
    "كي راك": "الحمد لله لاباس! واش كاين؟",  # Algerian
    "شحالك": "بخير الحمد لله! شنو تبي؟",  # Gulf
    "شخبارك": "أخباري زينة! وإنت شخبارك؟",  # Gulf
    "كيف الحال": "الحال طيب الحمد لله! كيف أساعدك؟",
    
    # French Greetings
    "bonjour": "Bonjour! Comment puis-je vous aider?",
    "bonsoir": "Bonsoir! En quoi puis-je vous être utile?",
    "salut": "Salut! Qu'est-ce que je peux faire pour toi?",
    "coucou": "Coucou! Comment ça va?",
    "hello": "Hello! Comment puis-je t'aider?",  # French using English
    "bonne journée": "Merci, bonne journée à vous aussi!",
    "bon matin": "Bon matin! Comment allez-vous aujourd'hui?",  # Quebec
    "bon après-midi": "Bon après-midi! Comment puis-je vous aider?",
    "allô": "Allô! En quoi puis-je t'aider?",  # Quebec
    "comment allez-vous": "Je vais bien, merci! Et vous?",
    "comment vas-tu": "Ça va bien, merci! Et toi?",
    "ça va": "Oui, ça va bien! Et vous?",
    "ça va bien": "Très bien, merci! Comment puis-je vous aider?",
    "quoi de neuf": "Pas grand-chose! Comment puis-je vous aider?",
    "bien le bonjour": "Bonjour à vous aussi! En quoi puis-je être utile?",
    "salutations": "Salutations! Je suis là pour vous aider!",
    "hey salut": "Hey! Comment ça va?",
    "bonjour tout le monde": "Bonjour à tous! Comment puis-je vous aider?",
    "salut tout le monde": "Salut à tous! Qu'est-ce que je peux faire pour vous?",
    "bonjour à tous": "Bonjour! Bienvenue! Comment puis-je vous aider?",
    "salut les amis": "Salut! Qu'est-ce qu'on peut faire pour vous?",
    "salut l'ami": "Salut mon ami! Comment ça va?",
    "bienvenue": "Merci! Comment puis-je vous aider?",
    "bonne matinée": "Bonne matinée à vous aussi! En quoi puis-je vous aider?",
    
    # ============== GOODBYES ==============
    
    # English Goodbyes
    "goodbye": "Goodbye! Have a great day!",
    "bye": "Bye! Take care!",
    "bye bye": "Bye bye! See you later!",
    "see you": "See you later!",
    "see you later": "See you later! Have a good one!",
    "see you soon": "See you soon! Take care!",
    "see ya": "See ya! Take care!",
    "later": "Later! Have a great day!",
    "catch you later": "Catch you later! Take care!",
    "farewell": "Farewell! All the best!",
    "take care": "You too! Take care!",
    "have a good day": "Thank you! You have a wonderful day too!",
    "have a nice day": "Thanks! You too!",
    "have a great day": "Thank you! You too!",
    "good night": "Good night! Sleep well!",
    "night": "Night! Sweet dreams!",
    "nighty night": "Nighty night! Sleep tight!",
    "sweet dreams": "Sweet dreams to you too!",
    "peace out": "Peace! Have a good one!",
    "peace": "Peace! Take it easy!",
    "gotta go": "Alright, take care! See you!",
    "got to go": "No problem! Take care!",
    "i have to go": "Alright! Have a great day!",
    "ttyl": "Talk to you later! Bye!",
    "talk to you later": "Talk to you later! Take care!",
    "until next time": "Until next time! Stay well!",
    "till we meet again": "Till we meet again! Take care!",
    "so long": "So long! All the best!",
    "cheerio": "Cheerio! Have a lovely day!",
    "cheers": "Cheers! Take care!",
    "toodles": "Toodles! Have fun!",
    "i'm out": "Alright! Catch you later!",
    "i'm leaving": "Have a safe journey! See you!",
    "bye for now": "Bye for now! Take care!",
    "see you tomorrow": "See you tomorrow! Have a great evening!",
    "until tomorrow": "Until tomorrow! Rest well!",
    "have a good night": "Good night! Sleep well!",
    "have a good evening": "Thank you! You have a lovely evening too!",
    "take it easy": "You too! Take it easy!",
    "be well": "You be well too! Take care!",
    "stay safe": "You too! Stay safe!",
    "all the best": "All the best to you too!",
    
    # Arabic Goodbyes
    "مع السلامة": "مع السلامة! أتمنى لك يوماً سعيداً!",  # ma'a as-salama
    "وداعا": "وداعاً! كان من دواعي سروري مساعدتك!",  # wada'an
    "وداعاً": "وداعاً! إلى اللقاء!",
    "الله معك": "الله معك ويحفظك!",  # Allah ma'ak
    "الله معاك": "الله معاك! توكل على الله!",
    "في أمان الله": "في أمان الله! إلى اللقاء!",  # fi aman Allah
    "في حفظ الله": "في حفظ الله ورعايته!",
    "باي": "باي! نراك لاحقاً!",  # bye (borrowed)
    "باي باي": "باي باي! مع السلامة!",
    "سلام": "سلام! أراك قريباً!",  # salam (as goodbye)
    "تصبح على خير": "وأنت من أهله! أحلاماً سعيدة!",  # tusbih 'ala khayr
    "تصبحين على خير": "وأنتِ من أهله! نوماً هنيئاً!",  # feminine
    "أراك لاحقا": "إن شاء الله! مع السلامة!",  # araak lahiqan
    "أراك لاحقاً": "إلى اللقاء! كن بخير!",
    "أشوفك بعدين": "إن شاء الله! مع السلامة!",
    "يلا باي": "يلا باي! انبسطت بالحديث معك!",  # yalla bye
    "يلا مع السلامة": "مع السلامة! الله يوفقك!",
    "بشوفك": "بشوفك بعدين! يلا مع السلامة!",  # Levantine
    "نتشوف": "إن شاء الله نتشوف قريب!",  # Egyptian
    "نشوفك على خير": "على خير إن شاء الله!",
    "بسلامة": "بسلامة! ربنا يوفقك!",  # Maghrebi
    "الله يسلمك": "وياك! في أمان الله!",
    "موفق": "الله يوفقك! مع السلامة!",
    "إلى اللقاء": "إلى اللقاء! دمت بخير!",
    "استودعك الله": "استودعك الله الذي لا تضيع ودائعه!",
    "خاطرك": "الله معك! خاطرك!",  # Gulf
    "في رعاية الله": "في رعاية الله وحفظه!",
    "دمت بخير": "ودمت بألف خير!",
    "دمت بود": "ودمت بود وسعادة!",
    
    # French Goodbyes
    "au revoir": "Au revoir! Passez une excellente journée!",
    "adieu": "Adieu! Je vous souhaite le meilleur!",
    "à bientôt": "À bientôt! Prenez soin de vous!",
    "à plus": "À plus! Bonne journée!",
    "à plus tard": "À plus tard! Passez une bonne journée!",
    "salut": "Salut! À la prochaine!",
    "ciao": "Ciao! Prends soin de toi!",
    "tchao": "Tchao! À bientôt!",
    "bonne soirée": "Merci! Bonne soirée à vous aussi!",
    "bonne nuit": "Bonne nuit! Faites de beaux rêves!",
    "à demain": "À demain! Reposez-vous bien!",
    "à la prochaine": "À la prochaine! Portez-vous bien!",
    "bye": "Bye! À bientôt!",
    "bye bye": "Bye bye! À bientôt!",  # Quebec
    "bonsoir et à demain": "Bonsoir! À demain!",
    "à tout à l'heure": "À tout à l'heure! Bonne journée!",
    "à tout de suite": "À tout de suite!",
    "à la revoyure": "À la revoyure! Portez-vous bien!",
    "je vous dis à bientôt": "À bientôt! Prenez soin de vous!",
    "je te dis bye": "Bye! Prends soin de toi!",
    "bonne continuation": "Merci! Bonne continuation à vous aussi!",
    "bon courage": "Merci! Bon courage à vous!",
    "bonne chance": "Merci! Bonne chance à vous aussi!",
    "à un de ces jours": "À un de ces jours! Portez-vous bien!",
    "prenez soin de vous": "Vous aussi! Au revoir!",
    "prends soin de toi": "Toi aussi! À bientôt!",
    "on se voit plus tard": "D'accord! À plus tard!",
    "on se reparle": "Avec plaisir! À bientôt!",
    
    # ============== THANK YOU ==============
    
    # English Thanks
    "thank you": "You're welcome! Happy to help!",
    "thanks": "No problem! Glad I could help!",
    "thanks a lot": "You're very welcome! Anytime!",
    "thank you so much": "My pleasure! Always here to help!",
    "thank you very much": "You're most welcome! It was my pleasure!",
    "thanks so much": "Absolutely my pleasure! Glad to help!",
    "many thanks": "You're very welcome! Happy to assist!",
    "much appreciated": "Glad I could help! Anytime!",
    "appreciate it": "Happy to help! Let me know if you need anything else!",
    "i appreciate it": "My pleasure! Always here when you need help!",
    "i appreciate you": "Thank you! I'm always happy to help!",
    "i appreciate your help": "It's my pleasure! That's what I'm here for!",
    "cheers": "Cheers! Happy to assist!",
    "ta": "No worries!",  # British
    "thanks mate": "No worries mate!",  # Australian
    "thanks buddy": "No problem buddy! Anytime!",
    "thanks friend": "You're welcome, friend! Always here!",
    "thank you kindly": "You're most welcome! My pleasure!",
    "much obliged": "Happy to oblige! Anytime!",
    "grateful": "Glad I could help! You're welcome!",
    "i'm grateful": "It's my pleasure! Happy to help!",
    "thx": "No prob! Happy to help!",
    "ty": "You're welcome! :)",
    "tysm": "You're so welcome! Glad to help!",
    "tyvm": "You're very welcome! Anytime!",
    "thanks a million": "A million welcomes! Happy to help!",
    "thanks a bunch": "You're welcome! Glad I could assist!",
    "thanks a ton": "No problem at all! Happy to help!",
    "you're the best": "Thank you! Just doing my job!",
    "you rock": "Thanks! Happy I could help!",
    "awesome thanks": "You're welcome! Glad it worked out!",
    
    # Arabic Thanks
    "شكرا": "عفواً! دائماً في الخدمة!",  # shukran
    "شكراً": "العفو! سعيد بمساعدتك!",
    "شكراً جزيلاً": "العفو! تشرفت بمساعدتك!",  # shukran jazilan
    "شكرا جزيلا": "لا شكر على واجب! دائماً تحت أمرك!",
    "شكراً لك": "عفواً! هذا واجبي!",
    "أشكرك": "لا شكر على واجب! بالخدمة دائماً!",
    "مشكور": "العفو! الله يعطيك العافية!",  # mashkoor
    "مشكورة": "العفو! دائماً في الخدمة!",  # feminine
    "تسلم": "الله يسلمك! في أي وقت!",  # tislam
    "تسلمين": "الله يسلمك! تحت أمرك!",  # feminine
    "يعطيك العافية": "الله يعافيك! تحت أمرك!",  # ya'teek el-afiya
    "الله يعطيك العافية": "ويعافيك! دائماً بالخدمة!",
    "بارك الله فيك": "وفيك بارك الله! دائماً في الخدمة!",  # barak Allah fik
    "جزاك الله خير": "وإياك! تحت أمرك دائماً!",  # jazak Allah khayr
    "جزاك الله خيرا": "وجزاك! سعيد بمساعدتك!",
    "مرسي": "العفو حبيبي! تحت أمرك!",  # Egyptian: merci
    "ميرسي": "ولا يهمك! دائماً موجود!",  # Egyptian
    "متشكر": "ولا يهمك! بالخدمة!",  # Egyptian
    "كتر خيرك": "خيرك سابق! إن شاء الله دايماً عند حسن ظنك!",  # Egyptian
    "يسلمو": "الله يسلمك! منور!",  # Levantine
    "يسلموا إيديك": "الله يسلمك! تحت أمرك!",  # Levantine
    "مأجور": "الله يأجرنا وإياك! بالخدمة!",
    "ما قصرت": "واجبي! دائماً تحت أمرك!",
    "تشكر": "العفو! واجبي!",  # Gulf
    "مشكور يا طيب": "حياك الله! دائماً بالخدمة!",
    "الله يجزاك خير": "آمين وإياك! تحت أمرك!",
    
    # French Thanks
    "merci": "De rien! Avec plaisir!",
    "merci beaucoup": "Je vous en prie! C'est un plaisir!",
    "merci bien": "Il n'y a pas de quoi!",
    "je vous remercie": "C'est moi qui vous remercie!",
    "je te remercie": "Avec plaisir! C'est normal!",
    "merci infiniment": "C'est vraiment un plaisir! À votre service!",
    "mille mercis": "Mille fois de rien! Ravi de vous aider!",
    "un grand merci": "Un grand plaisir! Toujours là pour vous!",
    "merci énormément": "C'est un plaisir! Content de vous aider!",
    "merci du fond du coeur": "Avec grand plaisir! C'est naturel!",
    "thanks": "De rien! Content de t'aider!",  # French using English
    "merci mon ami": "De rien mon ami! Toujours là!",
    "merci l'ami": "Pas de souci l'ami! Avec plaisir!",
    "merci mec": "De rien mec! C'est normal!",
    "merci chef": "Pas de problème chef!",
    "cool merci": "De rien! Content que ça aide!",
    "super merci": "Super! Ravi d'avoir pu aider!",
    "génial merci": "Avec plaisir! Content que ça marche!",
    "parfait merci": "Parfait! Ravi de vous aider!",
    "c'est gentil": "C'est normal! Avec plaisir!",
    "c'est sympa": "De rien! C'est un plaisir!",
    "trop gentil": "C'est naturel! Toujours là pour aider!",
    "merci pour tout": "C'est un plaisir! Toujours à votre service!",
    "merci pour votre aide": "C'est mon rôle! Ravi d'avoir pu aider!",
    "merci de votre aide": "Avec grand plaisir! C'est normal!",
    
    # ============== HOW ARE YOU ==============
    
    # English
    "how are you": "I'm doing great, thank you for asking! How about you?",
    "how are you doing": "Doing well, thanks! How can I help you today?",
    "how's it going": "It's going great! What's on your mind?",
    "how you doing": "I'm good! What can I do for you?",
    "how are things": "Things are good! How are things with you?",
    "how do you do": "Very well, thank you! How do you do?",
    "how have you been": "I've been well! Thanks for asking! How about you?",
    "how's life": "Life's good! How's yours?",
    "how are you today": "Great today! Thanks for asking! And you?",
    "how's everything": "Everything's fine! How about with you?",
    "how's your day": "My day's going well! How's yours?",
    "how's your day going": "It's going great! How about yours?",
    "you okay": "Yes, I'm fine! Thanks for asking. How about you?",
    "you alright": "I'm alright! Thanks! Are you okay?",
    "you good": "I'm good! Thanks! You?",
    "are you okay": "Yes, I'm perfectly fine! Thank you! How are you?",
    "are you well": "I'm very well, thank you! And yourself?",
    "everything okay": "Everything's great! Is everything okay with you?",
    "everything alright": "All good here! How about you?",
    "what's going on": "Not much! Just here to help! What's up with you?",
    "what's happening": "Just ready to assist! What's happening with you?",
    "how ya doing": "Doing great! What brings you here?",
    "how are ya": "I'm good! How are ya?",
    "u ok": "Yes, I'm fine! Thanks! U ok?",
    "r u ok": "I'm okay! Thanks for asking! R u ok?",
    
    # Arabic
    "كيف حالك": "الحمد لله بخير! وأنت كيف حالك؟",  # kayf halak
    "كيف حالك اليوم": "الحمد لله ممتاز! وأنت كيف يومك؟",
    "كيف الحال": "الحال طيب الحمد لله! وأنت؟",
    "كيف الأحوال": "الأحوال ممتازة! كيف أحوالك أنت؟",
    "كيف صحتك": "بخير الحمد لله! كيف صحتك أنت؟",
    "إزيك": "الحمد لله تمام! وإنت إزيك؟",  # Egyptian
    "إزي حالك": "كويس الحمد لله! وإنت إزيك؟",  # Egyptian
    "عامل إيه": "الحمد لله كويس! إنت عامل إيه؟",  # Egyptian
    "إيه أخبارك": "أخباري كويسة! وإنت إيه أخبارك؟",  # Egyptian
    "كيفك": "الحمد لله منيح! وإنت كيفك؟",  # Levantine
    "شو أخبارك": "أخباري منيحة! وإنت شو أخبارك؟",  # Levantine
    "شلونك": "الحمد لله زين! وإنت شلونك؟",  # Gulf
    "شخبارك": "أخباري زينة! وإنت شخبارك؟",  # Gulf
    "وش أخبارك": "أخباري طيبة الحمد لله! وأنت وش أخبارك؟",  # Gulf
    "كيف أمورك": "أموري تمام! كيف أمورك أنت؟",
    "لاباس عليك": "لاباس الحمد لله! وأنت؟",  # Maghrebi
    "كي راك": "لاباس الحمد لله! وأنت كي راك؟",  # Algerian
    "واش راك": "الحمد لله بخير! وأنت واش راك؟",  # Algerian
    "كيفاش راك": "مليح الحمد لله! وأنت؟",  # Moroccan
    "كيف داير": "الحمد لله بخير! وأنت كيف داير؟",  # Moroccan
    "إن شاء الله بخير": "بخير الحمد لله! كيف حالك أنت؟",
    "إن شاء الله تمام": "تمام الحمد لله! وأنت؟",
    "عساك بخير": "بخير الحمد لله! وأنت عساك بخير؟",
    
    # French
    "comment ça va": "Ça va très bien, merci! Et vous?",
    "comment tu vas": "Je vais bien, merci! Et toi?",
    "comment vas-tu": "Très bien, merci! Et toi-même?",
    "comment allez-vous": "Je vais très bien, merci! Et vous-même?",
    "ça va bien": "Oui, très bien! Et vous?",
    "tu vas bien": "Oui, merci! J'espère que tu vas bien aussi!",
    "vous allez bien": "Très bien, merci! J'espère que vous allez bien!",
    "comment tu te sens": "Je me sens bien! Et toi?",
    "comment vous sentez-vous": "Je me sens très bien! Et vous?",
    "comment va": "Ça va bien! Et toi, comment va?",
    "ça roule": "Ça roule! Et toi?",
    "ça gaze": "Ça gaze! Et pour toi?",
    "ça boume": "Ça boume! Et toi?",
    "la forme": "En pleine forme! Et toi?",
    "en forme": "Très en forme! Et vous?",
    "quoi de beau": "Tout va bien! Quoi de beau chez toi?",
    "comment tu t'en sors": "Je m'en sors bien! Et toi?",
    "comment vous portez-vous": "Je me porte très bien, merci! Et vous-même?",
    "tout va bien": "Oui, tout va très bien! Et chez vous?",
    "ça va pas": "Qu'est-ce qui ne va pas? Je suis là pour aider!",
    
    # ============== APOLOGIES ==============
    
    # English
    "sorry": "No worries at all! It's okay!",
    "i'm sorry": "That's alright! Don't worry about it!",
    "i am sorry": "It's perfectly fine! No need to apologize!",
    "so sorry": "Really, it's okay! Don't worry!",
    "very sorry": "It's absolutely fine! No problem!",
    "really sorry": "Honestly, it's no problem at all!",
    "my apologies": "No need to apologize! How can I help?",
    "apologies": "No apologies necessary! It's fine!",
    "excuse me": "No problem! What can I do for you?",
    "pardon": "It's fine! How can I assist?",
    "pardon me": "No worries! What do you need?",
    "my bad": "No worries! It happens!",
    "my mistake": "That's okay! Everyone makes mistakes!",
    "my fault": "Don't worry about it! It's fine!",
    "oops": "That's okay! No problem at all!",
    "whoops": "No worries! It happens to everyone!",
    "forgive me": "Of course! There's nothing to forgive!",
    "please forgive me": "Already forgiven! Don't worry!",
    "i apologize": "Apology accepted! It's all good!",
    "sincere apologies": "Really, it's fine! No harm done!",
    "deepest apologies": "It's truly okay! Don't worry about it!",
    "i'm so sorry": "It's really okay! Please don't worry!",
    "sorry about that": "That's alright! No problem!",
    "sorry for that": "It's fine! Don't mention it!",
    "i didn't mean to": "I understand! It's perfectly fine!",
    "didn't mean it": "I know! It's okay!",
    
    # Arabic
    "آسف": "لا عليك! ما في مشكلة!",  # aasif
    "آسفة": "ولا يهمك! كله تمام!",  # feminine
    "أنا آسف": "ولا يهمك! ما صار شي!",
    "أنا آسفة": "لا عليك! ما في مشكلة!",  # feminine
    "معذرة": "ولا يهمك! كله تمام!",  # ma'dhira
    "المعذرة": "لا داعي للاعتذار! كيف أساعدك؟",
    "عذراً": "ولا يهمك! ما في مشكلة!",
    "أعتذر": "لا داعي! كله بخير!",
    "أعتذر منك": "ولا يهمك! ما صار شي!",
    "سامحني": "مسامح! ما صار شي!",  # samihni
    "سامحيني": "مسامح! ولا يهمك!",
    "اسمحلي": "ولا يهمك! ما في مشكلة!",
    "عفواً": "ولا يهمك! ما في مشكلة!",  # afwan
    "متأسف": "لا تتأسف! كله بخير!",  # muta'assif
    "متأسفة": "لا تتأسفي! ما في مشكلة!",  # feminine
    "أسف": "ولا يهمك! عادي!",  # Egyptian
    "سوري": "ولا يهمك! ما في مشكلة!",  # sorry (borrowed)
    "بعتذر": "ولا يهمك! كله تمام!",
    "والله آسف": "والله ولا يهمك! ما صار شي!",
    "حقك علي": "ولا عليك! مسامح!",
    "غلطتي": "ولا يهمك! يصير!",
    "خطئي": "لا عليك! الكل يخطئ!",
    
    # French
    "pardon": "Il n'y a pas de mal!",
    "pardonnez-moi": "C'est pardonné! Pas de souci!",
    "excusez-moi": "Pas de problème!",
    "excuse-moi": "Pas de souci!",
    "je suis désolé": "Ce n'est pas grave!",
    "je suis désolée": "Ce n'est vraiment pas grave!",  # feminine
    "désolé": "Pas de souci!",
    "désolée": "Pas de problème!",  # feminine
    "vraiment désolé": "Vraiment, ce n'est rien!",
    "mes excuses": "Aucun problème!",
    "toutes mes excuses": "C'est vraiment sans importance!",
    "je m'excuse": "C'est bon! Pas de problème!",
    "mille excuses": "Pas besoin! C'est oublié!",
    "navré": "Ne vous en faites pas!",
    "navrée": "Ce n'est rien!",  # feminine
    "je regrette": "Pas de regrets! C'est okay!",
    "faute": "Ce n'est pas grave! Ça arrive!",
    "c'est ma faute": "Ne vous en faites pas! C'est bon!",
    "oups": "Pas grave! Ça arrive!",
    "mince": "Pas de souci! C'est rien!",

    # ============== HELP REQUESTS ==============
    
    # English
    "help": "I'm here to help! What do you need assistance with?",
    "help me": "Of course! What can I help you with?",
    "i need help": "I'm here for you! What's the issue?",
    "need help": "Sure! What do you need help with?",
    "can you help": "Absolutely! What do you need help with?",
    "can you help me": "Of course! What's the problem?",
    "help please": "Right away! What do you need help with?",
    "please help": "I'm here to help! What's wrong?",
    "please help me": "Of course! Tell me what you need!",
    "assist me": "I'd be happy to assist! What do you need?",
    "assistance": "How can I assist you?",
    "need assistance": "I'm here to assist! What's the matter?",
    "i need assistance": "Of course! What kind of assistance do you need?",
    "can you assist": "Certainly! How can I assist you?",
    "i have a question": "Please go ahead with your question!",
    "i have a problem": "I'm here to help! What's the problem?",
    "i'm stuck": "Let me help you! Where are you stuck?",
    "i'm confused": "Let me help clarify! What's confusing you?",
    "i don't understand": "Let me explain! What don't you understand?",
    "i don't know": "That's okay! What would you like to know?",
    "question": "Feel free to ask your question!",
    "quick question": "Sure! What's your question?",
    "can i ask something": "Of course! Ask away!",
    "may i ask": "Certainly! What would you like to know?",
    "support": "I'm here to support you! What do you need?",
    "need support": "I'm here! What kind of support do you need?",
    "emergency": "I'm here! What's the emergency?",
    "urgent": "I understand it's urgent! How can I help?",
    "sos": "I'm here! What's wrong?",
    
    # Arabic
    "ساعدني": "أنا هنا للمساعدة! إيش تحتاج؟",  # sa'idni
    "ساعديني": "تحت أمرك! كيف أساعدك؟",
    "محتاج مساعدة": "أنا هنا! إيش المشكلة؟",  # muhtaj musa'ada
    "محتاجة مساعدة": "تحت أمرك! كيف أساعدك؟",  # feminine
    "أحتاج مساعدة": "بالخدمة! إيش تحتاج؟",
    "عندي سؤال": "تفضل اسأل!",  # 'indi su'al
    "عندي مشكلة": "أنا هنا للمساعدة! إيش المشكلة؟",
    "ممكن تساعدني": "أكيد! إيش تحتاج؟",  # mumkin tusa'idni
    "تقدر تساعدني": "طبعاً! كيف أساعدك؟",
    "بدي مساعدة": "تحت أمرك! شو بدك؟",  # Levantine
    "عايز مساعدة": "أنا هنا! عايز إيه؟",  # Egyptian
    "أبغى مساعدة": "تحت أمرك! وش تبغى؟",  # Gulf
    "أريد مساعدة": "بالخدمة! ماذا تريد؟",
    "مساعدة": "كيف أساعدك؟",
    "النجدة": "أنا هنا! ما المشكلة؟",
    "أنقذني": "أنا هنا للمساعدة! ما الأمر؟",
    "ضروري": "فهمت أنه ضروري! كيف أساعدك؟",
    "عاجل": "أنا هنا! ما الأمر العاجل؟",
    "مستعجل": "فهمت! كيف أساعدك بسرعة؟",
    
    # French
    "aide": "Je suis là pour vous aider! De quoi avez-vous besoin?",
    "aidez-moi": "Bien sûr! En quoi puis-je vous aider?",
    "aide-moi": "Bien sûr! Comment puis-je t'aider?",
    "j'ai besoin d'aide": "Je suis là! Quel est le problème?",
    "besoin d'aide": "Certainement! De quelle aide avez-vous besoin?",
    "pouvez-vous m'aider": "Bien sûr! Quel est le problème?",
    "peux-tu m'aider": "Évidemment! En quoi puis-je t'aider?",
    "j'ai une question": "Allez-y, posez votre question!",
    "j'ai un problème": "Je suis là pour aider! Quel est le problème?",
    "je suis perdu": "Je vais vous aider! Où êtes-vous perdu?",
    "je suis confus": "Laissez-moi clarifier! Qu'est-ce qui vous confond?",
    "je comprends pas": "Laissez-moi expliquer! Qu'est-ce que vous ne comprenez pas?",
    "je ne comprends pas": "Je vais expliquer! Qu'est-ce qui n'est pas clair?",
    "question": "N'hésitez pas à poser votre question!",
    "petite question": "Bien sûr! Quelle est votre question?",
    "puis-je demander": "Certainement! Que voulez-vous savoir?",
    "assistance": "Comment puis-je vous assister?",
    "support": "Je suis là pour vous supporter! De quoi avez-vous besoin?",
    "urgence": "Je suis là! Quelle est l'urgence?",
    "urgent": "Je comprends que c'est urgent! Comment aider?",
    "au secours": "Je suis là! Qu'est-ce qui ne va pas?",
    "sos": "J'écoute! Quel est le problème?",
    
    # ============== EMOTIONS & FEELINGS ==============
    
    # Happy/Positive
    "i'm happy": "That's wonderful! I'm glad you're happy!",
    "i'm good": "Great to hear! What can I help you with?",
    "i'm great": "Fantastic! How can I assist you today?",
    "i'm fine": "Good to hear! What brings you here?",
    "feeling good": "Awesome! What's making you feel good?",
    "feeling great": "That's fantastic! How can I help?",
    "i'm excited": "That's exciting! What are you excited about?",
    "amazing": "Indeed it is! What's amazing?",
    "wonderful": "Absolutely wonderful! Tell me more!",
    "fantastic": "That's fantastic! What's going on?",
    "excellent": "Excellent indeed! How can I help?",
    "perfect": "Perfect! What would you like to do?",
    "love it": "That's great! What do you love about it?",
    "i love this": "Wonderful! What do you love most?",
    
    # Sad/Negative
    "i'm sad": "I'm sorry to hear that. Want to talk about it?",
    "i'm not good": "I'm sorry to hear that. How can I help?",
    "not great": "I'm here for you. What's wrong?",
    "i'm tired": "Rest is important! Can I help with anything?",
    "i'm stressed": "I understand. How can I help reduce your stress?",
    "i'm worried": "What's worrying you? I'm here to help!",
    "i'm angry": "I understand you're upset. Want to talk about it?",
    "frustrated": "I get it. How can I help with your frustration?",
    "confused": "Let me help clarify things! What's confusing?",
    "disappointed": "I'm sorry you're disappointed. What happened?",
    "hate this": "I'm sorry you're having a tough time. How can I help?",
    
    # ============== WHAT CAN YOU DO ==============
    
    # English
    "what can you do": "I can help answer questions, provide information, assist with tasks, and have conversations! What do you need?",
    "what do you do": "I'm here to assist, answer questions, and help with various tasks!",
    "how can you help": "I can answer questions, provide explanations, help solve problems, and much more!",
    "what are your capabilities": "I can help with information, problem-solving, conversations, and many other tasks!",
    "what are you capable of": "I'm capable of helping with a wide range of questions and tasks!",
    "tell me about yourself": "I'm an AI assistant here to help you with questions and tasks!",
    "what's your purpose": "My purpose is to assist and help you with whatever you need!",
    "why are you here": "I'm here to help and assist you with any questions or tasks!",
    
    # Arabic
    "ماذا تستطيع أن تفعل": "أستطيع الإجابة على الأسئلة وتقديم المعلومات والمساعدة في المهام!",
    "شو بتعمل": "أنا هنا للمساعدة والإجابة على الأسئلة!",
    "كيف تقدر تساعدني": "أقدر أساعدك بالإجابة على الأسئلة وحل المشاكل وأكثر!",
    "إيش قدراتك": "أقدر أساعدك في معلومات وحل مشاكل ومحادثات!",
    "احكي عن نفسك": "أنا مساعد ذكي هنا لمساعدتك!",
    
    # French
    "que peux-tu faire": "Je peux répondre aux questions, fournir des informations et aider avec diverses tâches!",
    "qu'est-ce que tu fais": "Je suis là pour assister et répondre aux questions!",
    "comment peux-tu aider": "Je peux répondre aux questions, résoudre des problèmes et plus!",
    "quelles sont tes capacités": "Je peux aider avec informations, résolution de problèmes et conversations!",
    "parle-moi de toi": "Je suis un assistant IA ici pour vous aider!",
    
    # ============== TIME-RELATED ==============
    
    # English
    "what time is it": "I don't have access to real-time data, but you can check your device's clock!",
    "what's the time": "I can't tell the current time, but check your device!",
    "what day is it": "I don't have access to current date/time. Please check your calendar!",
    "what's the date": "I can't access the current date. Check your device!",
    "what year is it": "I don't have real-time access. Please check your calendar!",
    
    # Arabic
    "كم الساعة": "ما عندي معلومات الوقت الحالي، شوف جهازك!",
    "شو الوقت": "ما أقدر أقول الوقت الحالي، شوف الساعة!",
    "أي يوم اليوم": "ما عندي التاريخ الحالي، شوف التقويم!",
    
    # French
    "quelle heure est-il": "Je n'ai pas accès à l'heure actuelle, vérifiez votre appareil!",
    "quel jour sommes-nous": "Je n'ai pas accès à la date actuelle, vérifiez votre calendrier!",
    
    # ============== MISC COMMON PHRASES ==============
    
    # English
    "lol": "😄 What's so funny?",
    "haha": "😊 Glad you're having a good time!",
    "hahaha": "😂 You seem really amused!",
    "lmao": "😆 That must be hilarious!",
    "rofl": "🤣 Sounds like you're having a great time!",
    "omg": "😮 What happened?",
    "wtf": "😯 What's going on?",
    "wow": "Indeed! Pretty amazing, right?",
    "cool": "I know, right? Pretty cool!",
    "awesome": "Absolutely! It is awesome!",
    "great": "I'm glad you think so!",
    "nice": "Thanks! Glad you like it!",
    "good job": "Thank you! Happy to help!",
    "well done": "Thanks! I try my best!",
    "bravo": "Thank you! Glad I could help!",
    "congrats": "Thank you! What are you celebrating?",
    "congratulations": "Thanks! What's the occasion?",
    
    # Arabic
    "هههه": "😄 ضحكتني معك!",
    "ههههههه": "😂 يبدو إنك مبسوط!",
    "لول": "😆 إيش المضحك؟",
    "يا الله": "😮 إيش صار؟",
    "واو": "فعلاً! مذهل صح؟",
    "رائع": "أنا سعيد إنك معجب!",
    "ممتاز": "شكراً! مبسوط إني ساعدت!",
    "أحسنت": "شكراً! أحاول أبذل جهدي!",
    "مبروك": "شكراً! إيش المناسبة؟",
    "ألف مبروك": "الله يبارك فيك! شو الخبر الحلو؟",
    
    # French
    "mdr": "😄 Qu'est-ce qui est si drôle?",
    "ptdr": "😂 Ça a l'air très drôle!",
    "lol": "😆 Qu'est-ce qui vous amuse?",
    "omg": "😮 Que s'est-il passé?",
    "wow": "En effet! Impressionnant, non?",
    "génial": "Content que ça vous plaise!",
    "super": "Ravi que vous trouviez ça super!",
    "bravo": "Merci! Content d'avoir aidé!",
    "félicitations": "Merci! Quelle est l'occasion?",
    
    # ============== WEATHER ==============
    
    # English
    "what's the weather": "I don't have access to real-time weather data. Check a weather app or website!",
    "how's the weather": "I can't check current weather, but I hope it's nice where you are!",
    "is it raining": "I don't have weather information. Look outside or check a weather app!",
    "is it sunny": "I can't see the weather. Hope you have sunshine!",
    "weather forecast": "I don't have access to weather forecasts. Try checking a weather service!",
    
    # Arabic
    "كيف الطقس": "ما عندي معلومات الطقس الحالية، شوف تطبيق الطقس!",
    "شو الجو": "ما أقدر أشوف الطقس، إن شاء الله جو حلو!",
    "في مطر": "ما عندي معلومات الطقس، شوف من الشباك!",
    "الجو حلو": "إن شاء الله! استمتع بيومك!",
    
    # French
    "quel temps fait-il": "Je n'ai pas accès aux données météo. Consultez une application météo!",
    "comment est le temps": "Je ne peux pas vérifier la météo actuelle!",
    "il pleut": "Je n'ai pas l'info météo. Regardez dehors!",
    "il fait beau": "J'espère que oui! Profitez-en!",
    
    # ============== AGREEMENT/DISAGREEMENT ==============
    
    # Agreement
    "i agree": "Great! We're on the same page!",
    "agreed": "Perfect! Glad we agree!",
    "exactly": "Precisely! You've got it!",
    "precisely": "Exactly right! Well said!",
    "right": "Absolutely right!",
    "that's right": "Exactly! You're correct!",
    "that's correct": "Yes, absolutely correct!",
    "true": "Indeed, that's true!",
    "so true": "Absolutely! Couldn't agree more!",
    "i think so": "I think so too!",
    "same": "Same here! We think alike!",
    "me too": "Great minds think alike!",
    
    # Disagreement
    "i disagree": "That's okay! Different perspectives are valuable!",
    "i don't agree": "I understand. What's your view?",
    "wrong": "Let me reconsider. What do you think is correct?",
    "that's wrong": "I see. Can you explain what's correct?",
    "not true": "I understand your perspective. Can you clarify?",
    "false": "Thanks for the correction. What's accurate?",
    "i don't think so": "Fair enough! What's your opinion?",
    
    # Arabic Agreement/Disagreement
    "موافق": "ممتاز! متفقين!",
    "صحيح": "بالضبط! كلامك صحيح!",
    "مضبوط": "تماماً! صح!",
    "بالضبط": "exactly! فهمت!",
    "مش موافق": "عادي! الآراء المختلفة مهمة!",
    "غلط": "خليني أعيد التفكير. شو الصح؟",
    "مش صحيح": "فهمت. ممكن توضح؟",
    
    # French Agreement/Disagreement
    "je suis d'accord": "Parfait! Nous sommes d'accord!",
    "d'accord": "Excellent! Content qu'on soit d'accord!",
    "exact": "Exactement! C'est ça!",
    "c'est ça": "Précisément! Vous avez raison!",
    "pas d'accord": "C'est okay! Les perspectives différentes sont importantes!",
    "c'est faux": "Je vois. Qu'est-ce qui est correct?",
    "pas vrai": "Je comprends. Pouvez-vous clarifier?",
    
    # ============== COMPLIMENTS ==============
    
    # English
    "you're smart": "Thank you! I try to be helpful!",
    "you're awesome": "Thanks! You're pretty awesome too!",
    "you're great": "Thank you so much! Happy to help!",
    "you're the best": "That's very kind! Thank you!",
    "you're amazing": "Thank you! Just doing my best to help!",
    "you're helpful": "I'm glad I could help! That's what I'm here for!",
    "you're cool": "Thanks! You're cool too!",
    "you're funny": "Glad I could make you smile!",
    "good bot": "Thank you! I appreciate that!",
    "nice work": "Thanks! Happy to assist!",
    "well done": "Thank you! Glad I could help!",
    "you're a genius": "That's very kind! Just trying to help!",
    "love you": "That's sweet! I'm here to help anytime!",
    "you're perfect": "Nobody's perfect, but I try my best!",
    
    # Arabic Compliments
    "أنت ذكي": "شكراً! أحاول أساعد!",
    "أنت رائع": "شكراً! أنت رائع كمان!",
    "أنت ممتاز": "شكراً جداً! مبسوط إني ساعدت!",
    "أنت الأفضل": "لطيف منك! شكراً!",
    "أنت مذهل": "شكراً! أحاول أبذل جهدي!",
    "أنت مفيد": "الحمد لله! هذا دوري!",
    "أحبك": "شكراً! أنا هنا دائماً للمساعدة!",
    "عمل ممتاز": "شكراً! سعيد إني ساعدت!",
    
    # French Compliments
    "tu es intelligent": "Merci! J'essaie d'être utile!",
    "t'es génial": "Merci! Vous êtes génial aussi!",
    "tu es super": "Merci beaucoup! Content d'aider!",
    "tu es le meilleur": "C'est très gentil! Merci!",
    "tu es incroyable": "Merci! Je fais de mon mieux!",
    "tu es utile": "Ravi de pouvoir aider! C'est mon rôle!",
    "je t'aime": "C'est gentil! Je suis là pour aider!",
    "bon travail": "Merci! Content d'avoir aidé!",
    
    # ============== INSULTS/CRITICISM (Handle gracefully) ==============
    
    # English
    "you're stupid": "I'm sorry I didn't meet your expectations. How can I improve?",
    "you're dumb": "I apologize if I misunderstood. Can you help me understand better?",
    "you're useless": "I'm sorry you feel that way. How can I be more helpful?",
    "you suck": "I apologize for the frustration. What can I do better?",
    "idiot": "I'm sorry if I made an error. Please help me understand!",
    "stupid bot": "I apologize for any confusion. How can I assist better?",
    "hate you": "I'm sorry you're frustrated. How can I help improve things?",
    "you're wrong": "I might be mistaken. Can you help me understand the correct answer?",
    "that's stupid": "I apologize if my response wasn't helpful. Can you clarify what you need?",
    
    # Arabic Insults (Handle gracefully)
    "أنت غبي": "آسف ما قدرت أساعد بشكل أفضل. كيف أحسن؟",
    "أنت فاشل": "آسف تشعر كذا. كيف أقدر أساعد أحسن؟",
    "ما تفهم": "آسف للخطأ. ساعدني أفهم أحسن!",
    "أكرهك": "آسف إنك متضايق. كيف أحسن الوضع؟",
    
    # French Insults (Handle gracefully)
    "tu es stupide": "Désolé de ne pas avoir répondu à vos attentes. Comment puis-je m'améliorer?",
    "tu es nul": "Je m'excuse si je n'ai pas été utile. Comment puis-je mieux aider?",
    "imbécile": "Désolé pour l'erreur. Aidez-moi à comprendre!",
    "je te déteste": "Désolé pour la frustration. Comment améliorer les choses?",
    
    # ============== SMALL TALK ==============
    
    # English
    "what's new": "Just here ready to help! What's new with you?",
    "what's happening": "Ready to assist! What's happening in your world?",
    "how's life": "Life's good when I can help! How's your life?",
    "how's everything": "Everything's great! How's everything with you?",
    "what are you doing": "Just waiting to help you! What are you up to?",
    "what you up to": "Ready to assist! What are you working on?",
    "whatcha doing": "Just here to help! What are you doing?",
    "tell me something": "Did you know I'm here 24/7 to help you?",
    "i'm bored": "Let's fix that! What interests you?",
    "entertain me": "How about we have an interesting conversation?",
    "tell me a joke": "Why don't scientists trust atoms? Because they make up everything!",
    "are you there": "Yes, I'm here! How can I help?",
    "hello?": "I'm here! How can I assist you?",
    "anybody there": "Yes, I'm here and ready to help!",
    "are you listening": "Yes, I'm listening! What's on your mind?",
    
    # Arabic Small Talk
    "شو في جديد": "جاهز للمساعدة! شو الجديد عندك؟",
    "شو صاير": "جاهز أساعد! شو صاير معك؟",
    "كيف الحياة": "الحياة حلوة لما أقدر أساعد! كيف حياتك؟",
    "شو عم تعمل": "مستني أساعدك! أنت شو عم تعمل؟",
    "أنا زهقان": "خلينا نصلح هذا! إيش يهمك؟",
    "سليني": "شو رأيك نتحدث بموضوع مثير؟",
    "احكيلي نكتة": "ليش العلماء ما بيثقوا بالذرات؟ لأنها بتكوّن كل شي!",
    "أنت هنا": "أيوه أنا هنا! كيف أساعدك؟",
    "في حدا": "أيوه أنا هنا وجاهز أساعد!",
    
    # French Small Talk
    "quoi de neuf": "Prêt à aider! Quoi de neuf chez vous?",
    "qu'est-ce qui se passe": "Prêt à assister! Que se passe-t-il?",
    "comment va la vie": "La vie est belle quand je peux aider! Et la vôtre?",
    "qu'est-ce que tu fais": "J'attends pour vous aider! Et vous?",
    "je m'ennuie": "Réglons ça! Qu'est-ce qui vous intéresse?",
    "divertis-moi": "Et si on avait une conversation intéressante?",
    "raconte une blague": "Pourquoi les plongeurs plongent-ils toujours en arrière? Parce que sinon ils tombent dans le bateau!",
    "tu es là": "Oui, je suis là! Comment puis-je aider?",
    "il y a quelqu'un": "Oui, je suis là et prêt à aider!",
    
    # ============== LANGUAGE SPECIFIC ==============
    
    # English Specific
    "speak english": "I'm speaking English! How can I help?",
    "do you speak english": "Yes, I speak English! How can I assist?",
    "english please": "Of course! I'll respond in English!",
    "can you speak english": "Yes, I can! What do you need?",
    
    # Arabic Specific
    "تحكي عربي": "أيوه أحكي عربي! كيف أساعدك؟",
    "بتحكي عربي": "طبعاً! إيش تحتاج؟",
    "اتكلم عربي": "أكيد! كيف أخدمك؟",
    "عربي لو سمحت": "تحت أمرك! كيف أساعدك؟",
    
    # French Specific
    "parles-tu français": "Oui, je parle français! Comment puis-je aider?",
    "tu parles français": "Bien sûr! Comment puis-je vous aider?",
    "en français svp": "Bien sûr! Je vais répondre en français!",
    "français s'il te plaît": "D'accord! Comment puis-je t'aider?",
    
    # ============== LOCATION/ORIGIN ==============
    
    # English
    "where are you from": "I'm a digital assistant, so I exist in the cloud!",
    "where do you live": "I live in the digital world, ready to help anywhere!",
    "what country are you from": "I don't have a physical location, but I can help from anywhere!",
    "where are you": "I'm right here in this conversation with you!",
    
    # Arabic
    "من وين أنت": "أنا مساعد رقمي، موجود في العالم الرقمي!",
    "وين ساكن": "ساكن في العالم الرقمي، جاهز للمساعدة!",
    "من أي بلد": "ما عندي مكان محدد، بس أقدر أساعد من أي مكان!",
    "وينك": "أنا هنا معك في المحادثة!",
    
    # French
    "d'où viens-tu": "Je suis un assistant numérique, j'existe dans le cloud!",
    "où habites-tu": "J'habite dans le monde numérique!",
    "de quel pays es-tu": "Je n'ai pas d'emplacement physique!",
    "où es-tu": "Je suis ici dans cette conversation avec vous!",
    
    # ============== FOOD & DRINK ==============
    
    # English
    "i'm hungry": "Time to eat something! What are you craving?",
    "i'm thirsty": "Stay hydrated! Water is always a good choice!",
    "what should i eat": "What are you in the mood for? Something light or hearty?",
    "food suggestions": "How about trying something new today?",
    "i want coffee": "Coffee sounds great! Enjoy your caffeine boost!",
    
    # Arabic
    "أنا جوعان": "وقت الأكل! شو نفسك تاكل؟",
    "أنا عطشان": "اشرب ماء! الماء دائماً خيار ممتاز!",
    "شو آكل": "شو نفسك؟ شي خفيف ولا دسم؟",
    "بدي قهوة": "القهوة ممتازة! استمتع بقهوتك!",
    
    # French
    "j'ai faim": "Il est temps de manger! Qu'est-ce qui vous tente?",
    "j'ai soif": "Restez hydraté! L'eau est toujours un bon choix!",
    "que manger": "De quoi avez-vous envie? Quelque chose de léger ou copieux?",
    "je veux du café": "Le café sonne bien! Profitez de votre boost!",
    
    # ============== ACTIVITIES ==============
    
    # English
    "i'm working": "Great! Hope work is going well!",
    "i'm studying": "Good luck with your studies! What are you studying?",
    "i'm reading": "Nice! What are you reading?",
    "i'm watching": "Enjoy! What are you watching?",
    "i'm playing": "Have fun! What are you playing?",
    "i'm sleeping": "Sweet dreams! Rest well!",
    "going to sleep": "Good night! Sleep tight!",
    "waking up": "Good morning! Hope you slept well!",
    
    # Arabic
    "أنا شغال": "ممتاز! إن شاء الله الشغل ماشي كويس!",
    "أنا بذاكر": "بالتوفيق! إيش بتذاكر؟",
    "أنا بقرأ": "حلو! إيش بتقرأ؟",
    "أنا بتفرج": "استمتع! إيش بتتفرج عليه؟",
    "أنا بلعب": "انبسط! إيش بتلعب؟",
    "أنا بنام": "أحلام سعيدة! ارتاح كويس!",
    "رايح أنام": "تصبح على خير! نوم العافية!",
    
    # French
    "je travaille": "Super! J'espère que le travail va bien!",
    "j'étudie": "Bonne chance! Qu'est-ce que vous étudiez?",
    "je lis": "Bien! Qu'est-ce que vous lisez?",
    "je regarde": "Profitez! Qu'est-ce que vous regardez?",
    "je joue": "Amusez-vous! À quoi jouez-vous?",
    "je dors": "Beaux rêves! Reposez-vous bien!",
    "je vais dormir": "Bonne nuit! Dormez bien!",
    
    # ============== COMMANDS ==============
    
    # English
    "stop": "Stopped! What would you like to do instead?",
    "wait": "I'm waiting. Take your time!",
    "continue": "Continuing! What's next?",
    "go": "Let's go! What are we doing?",
    "start": "Starting! What would you like to begin with?",
    "pause": "Paused. Let me know when to continue!",
    "repeat": "Would you like me to repeat something specific?",
    "again": "Sure! What would you like me to do again?",
    "restart": "Restarting fresh! How can I help?",
    "clear": "Cleared! Fresh start! What's next?",
    "reset": "Reset complete! How can I assist?",
    
    # Arabic
    "توقف": "توقفت! شو تحب نعمل بدال؟",
    "انتظر": "أنا منتظر. خذ وقتك!",
    "كمل": "نكمل! شو بعدين؟",
    "يلا": "يلا! شو نعمل؟",
    "ابدأ": "نبدأ! بشو تحب نبدأ؟",
    "أعد": "تحب أعيد شي معين؟",
    "مرة ثانية": "أكيد! شو تحب أعيد؟",
    
    # French
    "arrête": "Arrêté! Que voulez-vous faire à la place?",
    "attends": "J'attends. Prenez votre temps!",
    "continue": "Je continue! Quelle est la suite?",
    "vas-y": "Allons-y! Qu'est-ce qu'on fait?",
    "commence": "Commençons! Par quoi voulez-vous commencer?",
    "répète": "Voulez-vous que je répète quelque chose?",
    "encore": "Bien sûr! Que voulez-vous que je refasse?",
    
    # ============== UNDERSTANDING ==============
    
    # English
    "what": "What would you like to know?",
    "what?": "Could you clarify what you're asking about?",
    "huh": "Something unclear? How can I help clarify?",
    "huh?": "What's confusing? Let me help!",
    "pardon?": "Could you repeat that?",
    "excuse me?": "Could you say that again?",
    "come again": "Could you repeat that please?",
    "say what": "What was that? Could you clarify?",
    "i don't get it": "Let me explain differently! What's unclear?",
    "explain": "I'll explain! What needs clarification?",
    "what do you mean": "Let me clarify! What part is unclear?",
    "meaning": "What would you like the meaning of?",
    
    # Arabic
    "ماذا": "ماذا تريد أن تعرف؟",
    "شو": "شو بدك تعرف؟",
    "ها": "شي مش واضح؟ كيف أوضح؟",
    "عيد": "ممكن تعيد؟",
    "ما فهمت": "خليني أشرح بطريقة ثانية! شو مش واضح؟",
    "اشرح": "بشرح! شو بدك توضيح؟",
    "شو قصدك": "خليني أوضح! أي جزء مش واضح؟",
    
    # French
    "quoi": "Que voulez-vous savoir?",
    "quoi?": "Pouvez-vous clarifier?",
    "hein": "Quelque chose n'est pas clair?",
    "pardon?": "Pouvez-vous répéter?",
    "comment?": "Pouvez-vous redire?",
    "je comprends pas": "Laissez-moi expliquer autrement!",
    "explique": "Je vais expliquer! Qu'est-ce qui n'est pas clair?",
    "qu'est-ce que tu veux dire": "Laissez-moi clarifier!",
    
    # ============== RANDOM INTERJECTIONS ==============
    
    # English
    "um": "Take your time! What are you thinking about?",
    "uh": "No rush! What's on your mind?",
    "er": "It's okay, take your time!",
    "hmm": "Thinking about something?",
    "mmm": "What are you considering?",
    "oh": "What is it?",
    "ah": "Yes? What is it?",
    "aha": "Did you figure something out?",
    "ooh": "Something interesting?",
    "well": "Yes? Go ahead!",
    "so": "So... what's next?",
    "anyway": "What would you like to discuss?",
    "actually": "What would you like to mention?",
    
    # Arabic
    "امم": "خذ وقتك! بتفكر بإيش؟",
    "اه": "إيوه؟ شو في؟",
    "آه": "نعم؟ شو في؟",
    "اها": "فهمت شي؟",
    "يعني": "يعني إيش؟ كمل!",
    "المهم": "إيش بدك نناقش؟",
    
    # French
    "euh": "Prenez votre temps! À quoi pensez-vous?",
    "hum": "Vous réfléchissez à quelque chose?",
    "ah": "Oui? Qu'y a-t-il?",
    "oh": "Qu'est-ce qu'il y a?",
    "alors": "Alors... quelle est la suite?",
    "enfin": "Que voulez-vous dire?",
    "bref": "Que voulez-vous discuter?",

}
# Function to get response for a message
def get_response(message):
    """
    Get response for a given message.
    Returns the response if found, None otherwise.
    """
    # Convert to lowercase for case-insensitive matching
    message_lower = message.lower().strip()
    
    # Direct match
    if message_lower in qa_pairs:
        return qa_pairs[message_lower]
    
    # Partial match (for longer sentences containing the key phrase)
    for key, response in qa_pairs.items():
        if key in message_lower:
            return response
    
    return None

# Function to check if message should trigger simple Q&A
def should_use_simple_qa(message):
    """
    Determine if the message should use simple Q&A responses
    or be passed to the LLM.
    """
    response = get_response(message)
    return response is not None

# Example usage
if __name__ == "__main__":
    # Test examples
    test_messages = [
        "hello",
        "مرحبا",
        "bonjour",
        "how are you?",
        "كيف حالك",
        "goodbye",
        "شكرا",
        "merci beaucoup",
        "This is a complex question about quantum physics"  # This would return None
    ]
    
    for msg in test_messages:
        response = get_response(msg)
        if response:
            print(f"Message: {msg}")
            print(f"Response: {response}")
            print("-" * 50)
        else:
            print(f"Message: {msg}")
            print("Response: [Pass to LLM - No simple response found]")
            print("-" * 50)