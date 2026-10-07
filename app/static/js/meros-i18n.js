/* MEROS — language (RU / ENG / UZB) and currency (UZS / USD / EUR) switching.

   Everything happens in the browser; Django renders the Russian page once and
   puts the other variants next to it:

   - Static interface text needs no markup. Any text node whose (whitespace-
     normalised) Russian text is a key of TEXT below is translated. Elements
     that contain nothing but that text are tagged `data-i18n="<key>"` on the
     first pass, so their translation survives scripts that later rebuild
     their children (the word-by-word heading animation in meros-polish.js).
   - Text with markup inside (a <br> in a heading) uses an id from HTML:
     <h2 data-i18n-html="about.history">Наша<br>история</h2>.
   - Database fields carry every language in attributes:
     <h2 data-ru="…" data-en="…" data-uz="…">…</h2>. An empty translation
     falls back to Russian (the element gets `data-i18n-fallback`).
   - Multi-paragraph database text (|linebreaks) sits in a container marked
     `data-i18n-block`, with <template data-lang="en|uz"> holding the other
     languages.
   - aria-label / alt / title / placeholder are translated the same way as
     text; `data-alt-en` / `data-alt-uz` give the alt of a database image.
   - Prices: <span data-price data-uzs="…" data-usd="…" data-eur="…">. The
     value of the selected currency is shown as is: an empty value is shown as
     0 in that currency, never replaced by another currency or converted.
   - Dates: <span data-date="YYYY-MM-DD">.

   The choice is kept in localStorage (keys shared with the older select
   switcher, so earlier choices still apply). Without JavaScript the site is
   simply Russian in UZS. Other scripts use window.MerosI18n and listen for
   the `meros:prefschange` event. */
(function () {
  'use strict';

  var LANGS = ['ru', 'en', 'uz'];
  var CURRENCIES = ['UZS', 'USD', 'EUR'];
  var LANG_LABELS = { ru: 'RU', en: 'ENG', uz: 'UZB' };
  var LANG_KEY = 'meros-siteLanguage';
  var CURRENCY_KEY = 'meros-siteCurrency';
  var UZS_UNIT = { ru: 'сум', en: 'UZS', uz: 'so‘m' };

  /* Russian text -> [English, Uzbek (Latin)]. Uzbek still needs a review by
     a native speaker. */
  var TEXT = {
    /* navigation, footer, shared interface */
    'Главная': ['Home', 'Bosh sahifa'],
    'О нас': ['About us', 'Biz haqimizda'],
    'Ивенты': ['Events', 'Tadbirlar'],
    'Магазин': ['Shop', 'Do‘kon'],
    'Новости': ['News', 'Yangiliklar'],
    'Контакты': ['Contacts', 'Kontaktlar'],
    'Закрыть': ['Close', 'Yopish'],
    'MENU': ['MENU', 'MENYU'],
    'Навигация': ['Navigation', 'Navigatsiya'],
    'Ташкент': ['Tashkent', 'Toshkent'],
    'Ташкент, Узбекистан': ['Tashkent, Uzbekistan', 'Toshkent, O‘zbekiston'],
    'ул. Сайилгох, 12, Ташкент': ['12 Sayilgoh St., Tashkent', 'Sayilgoh ko‘chasi, 12, Toshkent'],
    'Ежедневно 10:00–20:00': ['Daily 10:00–20:00', 'Har kuni 10:00–20:00'],
    'Галерея наследия и современного узбекского ремесла. Ташкент.': [
      'A gallery of heritage and contemporary Uzbek craft. Tashkent.',
      'Meros va zamonaviy o‘zbek hunarmandchiligi galereyasi. Toshkent.'
    ],
    '© 2026 Meros. Все права защищены.': ['© 2026 Meros. All rights reserved.', '© 2026 Meros. Barcha huquqlar himoyalangan.'],
    'Дизайн и разработка — [ваша студия]': ['Design and development — [your studio]', 'Dizayn va ishlab chiqish — [studiyangiz]'],
    'Язык': ['Language', 'Til'],
    'Валюта': ['Currency', 'Valyuta'],
    'Язык и валюта': ['Language and currency', 'Til va valyuta'],
    'Подробнее': ['Learn more', 'Batafsil'],
    'Узнать больше': ['Learn more', 'Batafsil'],
    'Читать': ['Read', 'O‘qish'],
    'Читать дальше': ['Read more', 'Ko‘proq o‘qish'],
    'Все новости': ['All news', 'Barcha yangiliklar'],
    'А ещё у нас': ['There’s more', 'Bizda yana'],
    'Смотреть': ['View', 'Ko‘rish'],
    'Learn more': ['Learn more', 'Batafsil'],
    'Events & Masterclasses': ['Events & Masterclasses', 'Tadbirlar va master-klasslar'],
    'Book the Gallery': ['Book the Gallery', 'Galereyani band qilish'],
    'Email': ['Email', 'E-pochta'],

    /* page titles */
    'MEROS — Галерея наследия и ремесла': ['MEROS — A gallery of heritage and craft', 'MEROS — Meros va hunarmandchilik galereyasi'],
    'О Meros — Галерея наследия и ремесла': ['About Meros — A gallery of heritage and craft', 'Meros haqida — Meros va hunarmandchilik galereyasi'],
    'Ивенты и мастер-классы — Meros': ['Events and masterclasses — Meros', 'Tadbirlar va master-klasslar — Meros'],
    'Магазин — Meros': ['Shop — Meros', 'Do‘kon — Meros'],
    'Новости — Meros': ['News — Meros', 'Yangiliklar — Meros'],
    'Корзина — Meros': ['Cart — Meros', 'Savat — Meros'],

    /* home */
    'Галерея наследия и ремесла': ['A gallery of heritage and craft', 'Meros va hunarmandchilik galereyasi'],
    'О Meros': ['About Meros', 'Meros haqida'],
    'Ремесло, которое становится домом': ['Craft that becomes home', 'Uyga aylanadigan hunarmandchilik'],
    'Meros — галерея и шоурум в самом сердце Ташкента, где традиционное узбекское ремесло получает вторую жизнь в языке современного интерьера. Расписная керамика Риштана, вышитые сюзане, чапаны — не экспонаты, а часть современного гардероба и дома.': [
      'Meros is a gallery and showroom in the very heart of Tashkent, where traditional Uzbek craft gains a second life in the language of the contemporary interior. Painted Rishtan ceramics, embroidered suzani and chapans are not museum pieces but part of a modern wardrobe and home.',
      'Meros — Toshkentning qoq markazidagi galereya va shourum. Bu yerda an’anaviy o‘zbek hunarmandchiligi zamonaviy interyer tilida ikkinchi hayotga ega bo‘ladi. Rishtonning naqshinkor kulolchiligi, kashta tikilgan so‘zanalar, choponlar — eksponat emas, balki zamonaviy kiyim-kechak va uyning bir qismi.'
    ],
    'Отбираем работы мастеров со всей страны, рассказываем истории тех, кто их создал, и создаём пространство для встречи коллекционеров, дизайнеров интерьера и всех, кто ищет вещи со смыслом — от выставок до мастер-классов.': [
      'We select work by craftspeople from across the country, tell the stories of the people who made it and create a place where collectors, interior designers and everyone looking for meaningful things can meet — from exhibitions to masterclasses.',
      'Biz butun mamlakat ustalarining ishlarini saralaymiz, ularni yaratganlar haqida hikoya qilamiz va kolleksionerlar, interyer dizaynerlari hamda ma’noli buyumlar izlayotgan barcha uchun uchrashuv makonini yaratamiz — ko‘rgazmalardan master-klasslargacha.'
    ],
    'Закрытые ужины, показы коллекций и мастер-классы от практикующих мастеров — всё, что можно провести и чему можно научиться в пространстве Meros.': [
      'Private dinners, collection shows and masterclasses by practising craftspeople — everything you can host and learn in the Meros space.',
      'Yopiq kechki ovqatlar, kolleksiya namoyishlari va amaliyotchi ustalarning master-klasslari — Meros makonida o‘tkazish va o‘rganish mumkin bo‘lgan hamma narsa.'
    ],
    'Что происходит': ['What’s happening', 'Nimalar bo‘lyapti'],
    'Отзывы': ['Reviews', 'Sharhlar'],
    'Что говорят гости и коллекционеры': ['What guests and collectors say', 'Mehmonlar va kolleksionerlar fikri'],
    'Подпишитесь на нас в Instagram': ['Follow us on Instagram', 'Bizni Instagram’da kuzatib boring'],
    'Ежедневное вдохновение и закулисье мастерских — ближе, чем в галерее.': [
      'Daily inspiration and a look behind the scenes of the workshops — closer than in the gallery.',
      'Har kungi ilhom va ustaxonalarning sahna ortidagi hayoti — galereyadagidan ham yaqinroq.'
    ],

    /* about */
    'Мерос значит наследие — мы делаем его частью повседневной жизни.': [
      'Meros means heritage — we make it part of everyday life.',
      'Meros — biz merosni kundalik hayotning bir qismiga aylantiramiz.'
    ],
    'Meros — независимая галерея и культурное пространство в Ташкенте, объединяющее искусство, винтаж, моду, ремесло и людей. Здесь можно познакомиться с работами художников и мастеров, найти редкие предметы, посетить выставку, принять участие в мастер-классе или просто провести время в атмосфере, располагающей к общению и новым идеям.': [
      'Meros is an independent gallery and cultural space in Tashkent that brings together art, vintage, fashion, craft and people. Here you can discover the work of artists and craftspeople, find rare objects, visit an exhibition, take part in a masterclass or simply spend time in an atmosphere that invites conversation and new ideas.',
      'Meros — Toshkentdagi mustaqil galereya va madaniy makon bo‘lib, san’at, vintaj, moda, hunarmandchilik va odamlarni birlashtiradi. Bu yerda rassomlar va ustalarning ishlari bilan tanishish, noyob buyumlarni topish, ko‘rgazmaga borish, master-klassda qatnashish yoki shunchaki muloqot va yangi g‘oyalarga chorlovchi muhitda vaqt o‘tkazish mumkin.'
    ],
    '01 / Истоки': ['01 / Origins', '01 / Ildizlar'],
    'Meros появился из многолетней любви к винтажу, искусству и пространствам с характером. Галерея разместилась в старом ташкентском доме, который постепенно и бережно наполнялся найденными предметами, винтажной мебелью и материалами, сохранёнными из домов, предназначенных под снос.': [
      'Meros grew out of a long-standing love of vintage, art and spaces with character. The gallery settled in an old Tashkent house that was gradually and carefully filled with found objects, vintage furniture and materials saved from houses slated for demolition.',
      'Meros vintajga, san’atga va o‘ziga xos ruhga ega makonlarga bo‘lgan ko‘p yillik muhabbatdan tug‘ildi. Galereya eski toshkent uyida joylashdi: bu uy asta-sekin va ehtiyotkorlik bilan topilgan buyumlar, vintaj mebellar hamda buzishga mo‘ljallangan uylardan saqlab qolingan materiallar bilan to‘ldirildi.'
    ],
    'Так возникло пространство, в котором прошлое не становится музейной декорацией, а продолжает жить и приобретать новое значение.': [
      'This is how a space emerged in which the past does not turn into museum decoration but goes on living and taking on new meaning.',
      'Shu tariqa o‘tmish muzey bezagiga aylanmaydigan, balki yashashda davom etadigan va yangi ma’no kasb etadigan makon paydo bo‘ldi.'
    ],
    '02 / Связи': ['02 / Connections', '02 / Aloqalar'],
    'Наша концепция': ['Our concept', 'Bizning konsepsiyamiz'],
    'Сегодня Meros — это галерея, boutique, secondhand, творческая мастерская и место для культурных событий.': [
      'Today Meros is a gallery, a boutique, a secondhand shop, a creative workshop and a venue for cultural events.',
      'Bugun Meros — bu galereya, butik, secondhand, ijodiy ustaxona va madaniy tadbirlar uchun maskan.'
    ],
    'Разные направления объединяет одна идея: вещи, искусство и традиции не должны оставаться в прошлом. Они могут органично существовать в современном интерьере, гардеробе и образе жизни.': [
      'One idea unites these different directions: things, art and traditions should not stay in the past. They can live naturally in a contemporary interior, wardrobe and way of life.',
      'Turli yo‘nalishlarni bitta g‘oya birlashtiradi: buyumlar, san’at va an’analar o‘tmishda qolib ketmasligi kerak. Ular zamonaviy interyer, kiyim-kechak va turmush tarzida uyg‘un yashashi mumkin.'
    ],
    '03 / Взгляд': ['03 / Outlook', '03 / Qarash'],
    'Мы верим в вещи с историей, ручной труд, культурную преемственность и красоту, которая не нуждается в громкости.': [
      'We believe in things with a history, in handwork, in cultural continuity and in a beauty that has no need to be loud.',
      'Biz tarixi bor buyumlarga, qo‘l mehnatiga, madaniy davomiylikka va baland ovozga muhtoj bo‘lmagan go‘zallikka ishonamiz.'
    ],
    'Для нас галерея — это не только место, где рассматривают искусство. Это пространство, в котором можно встречаться, создавать, открывать новое, вдохновляться и чувствовать себя частью сообщества.': [
      'For us a gallery is not only a place for looking at art. It is a space where you can meet, create, discover, find inspiration and feel part of a community.',
      'Biz uchun galereya — faqat san’at tomosha qilinadigan joy emas. Bu uchrashish, ijod qilish, yangilik kashf etish, ilhomlanish va o‘zini jamoaning bir qismi deb his qilish mumkin bo‘lgan makon.'
    ],
    '04 / Основательница': ['04 / Founder', '04 / Asoschi'],
    'Дизайнер одежды и интерьеров': ['Fashion and interior designer', 'Kiyim va interyer dizayneri'],
    'Основательница Meros': ['Founder of Meros', 'Meros asoschisi'],
    'После многих лет жизни за рубежом Динара вернулась в Узбекистан и создала пространство, объединившее её любовь к винтажу, архитектуре, моде и искусству.': [
      'After many years abroad, Dinara returned to Uzbekistan and created a space that brought together her love of vintage, architecture, fashion and art.',
      'Ko‘p yillar xorijda yashaganidan so‘ng Dinara O‘zbekistonga qaytdi va vintaj, arxitektura, moda hamda san’atga bo‘lgan muhabbatini birlashtirgan makon yaratdi.'
    ],
    'Meros стал отражением её личного видения — местом, где предметы с прошлым, современная культура и люди складываются в одну живую историю.': [
      'Meros became a reflection of her personal vision — a place where objects with a past, contemporary culture and people come together into one living story.',
      'Meros uning shaxsiy qarashlari aksiga aylandi — o‘tmishga ega buyumlar, zamonaviy madaniyat va odamlar bitta jonli hikoyaga birlashadigan joy.'
    ],
    'Слова основательницы': ['In the founder’s words', 'Asoschi so‘zlari'],
    '«Мне хотелось создать не просто галерею, а живое пространство, куда приходят за красотой и остаются ради атмосферы, разговоров и новых идей».': [
      '“I wanted to create not just a gallery but a living space, where people come for beauty and stay for the atmosphere, the conversations and new ideas.”',
      '«Men shunchaki galereya emas, balki odamlar go‘zallik uchun keladigan va muhit, suhbatlar hamda yangi g‘oyalar uchun qoladigan jonli makon yaratmoqchi edim».'
    ],
    'Динара Кадырова': ['Dinara Kadyrova', 'Dinara Kadyrova'],
    'Пространства Meros': ['The spaces of Meros', 'Meros makonlari'],
    'Каждая часть Meros имеет собственный ритм: от открытого двора до камерной зоны Second Hand.': [
      'Every part of Meros has its own rhythm: from the open courtyard to the intimate Second Hand area.',
      'Meros’ning har bir qismi o‘z maromiga ega: ochiq hovlidan tortib Second Hand’ning shinam zonasigacha.'
    ],
    '01 / Пространство': ['01 / Space', '01 / Makon'],
    '02 / Пространство': ['02 / Space', '02 / Makon'],
    '03 / Пространство': ['03 / Space', '03 / Makon'],
    '04 / Пространство': ['04 / Space', '04 / Makon'],
    '05 / Пространство': ['05 / Space', '05 / Makon'],
    '06 / Пространство': ['06 / Space', '06 / Makon'],
    'Внутренний двор, где начинается визит в Meros и проходят открытые встречи.': [
      'The inner courtyard, where a visit to Meros begins and open gatherings take place.',
      'Meros’ga tashrif boshlanadigan va ochiq uchrashuvlar o‘tkaziladigan ichki hovli.'
    ],
    'Шоурум с одеждой и предметами для современной жизни — от лимитированных капсул до вещей на каждый день.': [
      'A showroom of clothing and objects for modern life — from limited capsules to everyday pieces.',
      'Zamonaviy hayot uchun kiyim va buyumlar shourumi — cheklangan kapsulalardan tortib har kungi narsalargacha.'
    ],
    'Мастерская для практических занятий, творческих встреч и резиденций мастеров.': [
      'A workshop for hands-on classes, creative meetings and craftspeople’s residencies.',
      'Amaliy mashg‘ulotlar, ijodiy uchrashuvlar va ustalar rezidensiyalari uchun ustaxona.'
    ],
    'Гостиная для встреч, неспешных разговоров и знакомства с искусством.': [
      'A lounge for meetings, unhurried conversations and getting to know art.',
      'Uchrashuvlar, shoshilmasdan suhbatlashish va san’at bilan tanishish uchun mehmonxona.'
    ],
    'Камерная коллекция отобранных вещей, в которых время становится частью ценности.': [
      'An intimate collection of selected pieces in which time becomes part of their value.',
      'Vaqt qadr-qimmatining bir qismiga aylangan saralangan buyumlardan iborat kichik kolleksiya.'
    ],
    'Первая точка знакомства с галереей и её текущей программой.': [
      'The first point of contact with the gallery and its current programme.',
      'Galereya va uning joriy dasturi bilan tanishishning ilk nuqtasi.'
    ],
    '05 / Практика': ['05 / Practice', '05 / Amaliyot'],
    'События — организация и проведение мероприятий в пространстве галереи. Магазин — retail, vintage и secondhand, вещи с настоящей историей.': [
      'Events — organising and hosting events in the gallery space. Shop — retail, vintage and secondhand, things with a real history.',
      'Tadbirlar — galereya makonida tadbirlarni tashkil etish va o‘tkazish. Do‘kon — retail, vintaj va secondhand, haqiqiy tarixga ega buyumlar.'
    ],
    'Мастер-классы — образовательные и творческие встречи с практикующими мастерами.': [
      'Masterclasses — educational and creative sessions with practising craftspeople.',
      'Master-klasslar — amaliyotchi ustalar bilan ta’limiy va ijodiy uchrashuvlar.'
    ],
    '06 / Люди': ['06 / People', '06 / Odamlar'],
    'Сообщество': ['Community', 'Jamoa'],
    'Meros — это не только пространство, но и круг людей: мастера, коллекционеры, дизайнеры, гости города и соседи, которые заходят на чашку чая.': [
      'Meros is not only a space but also a circle of people: craftspeople, collectors, designers, visitors to the city and neighbours who drop in for a cup of tea.',
      'Meros — bu nafaqat makon, balki odamlar davrasi hamdir: ustalar, kolleksionerlar, dizaynerlar, shahar mehmonlari va bir piyola choyga kirib o‘tadigan qo‘shnilar.'
    ],
    'Мы создаём поводы встречаться — от открытий выставок до мастер-классов и совместных проектов.': [
      'We create reasons to meet — from exhibition openings to masterclasses and joint projects.',
      'Biz uchrashish uchun bahonalar yaratamiz — ko‘rgazmalar ochilishidan tortib master-klasslar va qo‘shma loyihalargacha.'
    ],

    /* events */
    'Meros · События и мастер-классы': ['Meros · Events and masterclasses', 'Meros · Tadbirlar va master-klasslar'],
    'События и мастер-классы': ['Events and masterclasses', 'Tadbirlar va master-klasslar'],
    'Камерные вечера, творческие встречи и новые знакомства в атмосфере Meros.': [
      'Intimate evenings, creative meetings and new acquaintances in the atmosphere of Meros.',
      'Meros muhitidagi samimiy oqshomlar, ijodiy uchrashuvlar va yangi tanishuvlar.'
    ],
    '/ место': ['/ seat', '/ o‘rin'],
    'Ведёт': ['Hosted by', 'Boshlovchi:'],
    'Все места на данное мероприятие проданы.': ['All places for this event have been sold.', 'Ushbu tadbirga barcha o‘rinlar sotildi.'],
    'Все места на этот мастер-класс проданы.': ['All places for this masterclass have been sold.', 'Ushbu master-klassga barcha o‘rinlar sotildi.'],
    'Запросите мероприятие в галерее': ['Request an event at the gallery', 'Galereyada tadbir o‘tkazishga so‘rov yuboring'],
    'Расскажите, что планируете, — и мы предложим формат, вместимость и список услуг под ваш случай.': [
      'Tell us what you are planning and we will suggest a format, capacity and list of services for your occasion.',
      'Nimani rejalashtirayotganingizni aytib bering — biz sizga mos format, sig‘im va xizmatlar ro‘yxatini taklif qilamiz.'
    ],
    'Имя': ['Name', 'Ism'],
    'Телефон': ['Phone', 'Telefon'],
    'Тип мероприятия': ['Event type', 'Tadbir turi'],
    'Частное мероприятие': ['Private event', 'Shaxsiy tadbir'],
    'Показ / презентация': ['Show / presentation', 'Namoyish / taqdimot'],
    'Ужин': ['Dinner', 'Kechki ovqat'],
    'Фотосъёмка': ['Photo shoot', 'Fotosessiya'],
    'Другое': ['Other', 'Boshqa'],
    'Предпочитаемая дата': ['Preferred date', 'Qulay sana'],
    'Количество гостей': ['Number of guests', 'Mehmonlar soni'],
    'Дополнительная информация': ['Additional information', 'Qo‘shimcha ma’lumot'],
    'Отправить заявку': ['Send request', 'So‘rov yuborish'],
    'Заявка подготовлена': ['Request prepared', 'So‘rov tayyorlandi'],

    /* shop, categories, product */
    'Meros · Магазин': ['Meros · Shop', 'Meros · Do‘kon'],
    'Вещи с историей — для современной жизни': ['Things with a story — for modern life', 'Tarixi bor buyumlar — zamonaviy hayot uchun'],
    'Одежда, искусство и предметы, выбранные за их качество, характер и способность оставаться актуальными вне времени.': [
      'Clothing, art and objects chosen for their quality, character and ability to stay relevant beyond time.',
      'Sifati, o‘ziga xosligi va vaqtdan tashqari dolzarb bo‘lib qola olishi uchun tanlangan kiyimlar, san’at asarlari va buyumlar.'
    ],
    'Вещи, у которых есть автор': ['Things that have an author', 'Muallifi bor buyumlar'],
    'Авторская одежда, винтажные находки, произведения искусства и предметы ручной работы — каждая вещь представлена в единственном экземпляре или ограниченном количестве.': [
      'Designer clothing, vintage finds, works of art and handmade objects — each piece is one of a kind or available in limited numbers.',
      'Mualliflik kiyimlari, vintaj topilmalar, san’at asarlari va qo‘l mehnati bilan yaratilgan buyumlar — har bir narsa yagona nusxada yoki cheklangan miqdorda taqdim etiladi.'
    ],
    'Мы выбираем предметы, в которых чувствуется рука автора, культурная память и собственная история. Это вещи, которые не просто занимают место, а становятся частью жизни.': [
      'We choose objects that carry the hand of their maker, cultural memory and a story of their own. These are things that do not simply take up space but become part of life.',
      'Biz muallif qo‘li, madaniy xotira va o‘z tarixi seziladigan buyumlarni tanlaymiz. Bular shunchaki joy egallamaydigan, balki hayotning bir qismiga aylanadigan narsalardir.'
    ],
    'Современный гардероб с глубокими корнями': ['A modern wardrobe with deep roots', 'Chuqur ildizlarga ega zamonaviy garderob'],
    'История, которую можно продолжить': ['A story you can continue', 'Davom ettirish mumkin bo‘lgan tarix'],
    'Достойная вторая жизнь': ['A worthy second life', 'Munosib ikkinchi hayot'],
    'Искусство, которое меняет пространство': ['Art that changes a space', 'Makonni o‘zgartiradigan san’at'],
    'Смотреть Retail': ['View Retail', 'Retail’ni ko‘rish'],
    'Смотреть Vintage': ['View Vintage', 'Vintage’ni ko‘rish'],
    'Смотреть Secondhand': ['View Secondhand', 'Secondhand’ni ko‘rish'],
    'Смотреть Art': ['View Art', 'Art’ni ko‘rish'],
    '← Магазин': ['← Shop', '← Do‘kon'],
    'Купить': ['Buy', 'Sotib olish'],
    'В этой категории пока нет товаров.': ['There are no products in this category yet.', 'Bu toifada hozircha mahsulotlar yo‘q.'],
    'В этой категории пока нет работ.': ['There are no works in this category yet.', 'Bu toifada hozircha asarlar yo‘q.'],
    'Работы современных художников Узбекистана': ['Works by contemporary artists of Uzbekistan', 'O‘zbekiston zamonaviy rassomlarining asarlari'],
    'Смотреть работы': ['View the works', 'Asarlarni ko‘rish'],
    'Весь магазин': ['Entire shop', 'Butun do‘kon'],
    'Стоимость:': ['Price:', 'Narxi:'],
    'Добавить в корзину': ['Add to cart', 'Savatga qo‘shish'],
    'Приобрести работу': ['Acquire this work', 'Asarni sotib olish'],
    'Этот товар уже продан.': ['This item has already been sold.', 'Bu mahsulot allaqachon sotilgan.'],
    'Вернуться в каталог': ['Back to the catalogue', 'Katalogga qaytish'],
    'Связаться с нами': ['Contact us', 'Biz bilan bog‘lanish'],
    'Добавлено в корзину': ['Added to cart', 'Savatga qo‘shildi'],
    'Не удалось добавить': ['Could not add', 'Qo‘shib bo‘lmadi'],

    /* news */
    'Meros · Новости': ['Meros · News', 'Meros · Yangiliklar'],
    'Пока новостей нет — но скоро здесь появится первая.': ['No news yet — the first story will appear here soon.', 'Hozircha yangiliklar yo‘q — tez orada birinchisi paydo bo‘ladi.'],

    /* cart */
    'Ваш выбор': ['Your selection', 'Sizning tanlovingiz'],
    'Корзина': ['Cart', 'Savat'],
    'Позиций': ['Items', 'Pozitsiyalar'],
    'всего единиц': ['total units', 'jami birlik'],
    'Всего единиц': ['Total units', 'Jami birlik'],
    'Товар': ['Product', 'Mahsulot'],
    'Ивент': ['Event', 'Tadbir'],
    'Мастер-класс': ['Masterclass', 'Master-klass'],
    '/ шт.': ['/ pc.', '/ dona'],
    'Количество': ['Quantity', 'Miqdor'],
    'Удалить': ['Remove', 'O‘chirish'],
    'Итого': ['Total', 'Jami'],
    'Продолжить покупки': ['Continue shopping', 'Xaridni davom ettirish'],
    'Здесь пока ничего нет': ['Nothing here yet', 'Hozircha bu yerda hech narsa yo‘q'],
    'Выбранные вещи, билеты на события и места на мастер-классы появятся здесь.': [
      'The items you choose, event tickets and masterclass places will appear here.',
      'Tanlangan buyumlar, tadbir chiptalari va master-klassdagi o‘rinlar shu yerda paydo bo‘ladi.'
    ],
    'Перейти в магазин': ['Go to the shop', 'Do‘konga o‘tish'],

    /* attributes: aria-label, alt */
    'Meros Gallery — на главную': ['Meros Gallery — home page', 'Meros Gallery — bosh sahifa'],
    'Открыть меню': ['Open menu', 'Menyuni ochish'],
    'Закрыть меню': ['Close menu', 'Menyuni yopish'],
    'Прокрутить вниз': ['Scroll down', 'Pastga aylantirish'],
    'Назад': ['Back', 'Orqaga'],
    'Вперёд': ['Next', 'Oldinga'],
    'Избранное': ['Featured', 'Tanlanganlar'],
    'Все товары': ['All products', 'Barcha mahsulotlar'],
    'Предыдущий товар': ['Previous product', 'Oldingi mahsulot'],
    'Следующий товар': ['Next product', 'Keyingi mahsulot'],
    'Предыдущее фото': ['Previous photo', 'Oldingi surat'],
    'Следующее фото': ['Next photo', 'Keyingi surat'],
    'Показать фото': ['Show photo', 'Suratni ko‘rsatish'],
    'Показать:': ['Show:', 'Ko‘rsatish:'],
    'Работы': ['Works', 'Asarlar'],
    'Итог заказа': ['Order summary', 'Buyurtma yakuni'],
    'Уменьшить количество': ['Decrease quantity', 'Miqdorni kamaytirish'],
    'Увеличить количество': ['Increase quantity', 'Miqdorni oshirish'],
    'Светлый выставочный зал с произведениями искусства': ['A bright exhibition hall with works of art', 'San’at asarlari qo‘yilgan yorug‘ ko‘rgazma zali'],
    'Выставка традиционных головных уборов в синем зале': ['An exhibition of traditional headwear in a blue hall', 'Ko‘k zaldagi an’anaviy bosh kiyimlar ko‘rgazmasi'],
    'Иммерсивная световая инсталляция среди деревьев': ['An immersive light installation among trees', 'Daraxtlar orasidagi immersiv yorug‘lik installyatsiyasi'],
    'Выставочный зал с модой и скульптурными объектами': ['An exhibition hall with fashion and sculptural objects', 'Moda va haykaltaroshlik obyektlari qo‘yilgan ko‘rgazma zali'],
    'Выставочные залы с бирюзовыми и терракотовыми стенами': ['Exhibition halls with turquoise and terracotta walls', 'Firuza va terrakota rangli devorli ko‘rgazma zallari'],
    'Открытое музейное пространство с винтовой лестницей': ['An open museum space with a spiral staircase', 'Vintli zinapoyali ochiq muzey makoni']
  };

  /* Markup-bearing texts, addressed by id: [Russian, English, Uzbek]. Only
     these strings — never database values — are written with innerHTML. */
  var HTML = {
    'about.history': ['Наша<br />история', 'Our<br />story', 'Bizning<br />tariximiz'],
    'about.philosophy': ['Наша<br />философия', 'Our<br />philosophy', 'Bizning<br />falsafamiz'],
    'about.founder': ['Динара<br /><em>Кадырова</em>', 'Dinara<br /><em>Kadyrova</em>', 'Dinara<br /><em>Kadyrova</em>'],
    'about.directions': ['Четыре направления<br />одной идеи', 'Four directions<br />of one idea', 'Bitta g‘oyaning<br />to‘rt yo‘nalishi']
  };

  var UZ_MONTHS = ['yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun', 'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr'];

  /* ---------- preferences ---------- */

  function read(key, allowed, fallback) {
    try {
      var value = window.localStorage.getItem(key);
      return allowed.indexOf(value) > -1 ? value : fallback;
    } catch (e) {
      return fallback;
    }
  }
  function write(key, value) {
    try { window.localStorage.setItem(key, value); } catch (e) { /* private mode: keep it for this page only */ }
  }

  var state = {
    lang: read(LANG_KEY, LANGS, 'ru'),
    currency: read(CURRENCY_KEY, CURRENCIES, 'UZS')
  };

  /* ---------- text ---------- */

  function norm(text) { return String(text == null ? '' : text).replace(/\s+/g, ' ').trim(); }

  function lookup(key, lang) {
    lang = lang || state.lang;
    if (lang === 'ru') return key;
    var entry = TEXT[key];
    return entry ? entry[LANGS.indexOf(lang) - 1] : null;
  }

  /* Translate a Russian interface string; unknown strings come back as is. */
  function t(text, lang) {
    var key = norm(text);
    var value = lookup(key, lang);
    return value == null ? text : value;
  }

  /* "Показать фото 3" -> "Show photo 3": a known prefix followed by a number. */
  function translateLabel(original) {
    var key = norm(original);
    var direct = lookup(key);
    if (direct != null) return direct;
    var match = key.match(/^(.*\S)\s+(\d+)$/);
    if (match) {
      var prefix = lookup(match[1]);
      if (prefix != null) return prefix + ' ' + match[2];
    }
    return null;
  }

  function setText(el, value) {
    if (norm(el.textContent) !== norm(value)) el.textContent = value;
  }

  var SKIP = 'script,style,template,noscript,textarea,[data-ru],[data-i18n],[data-i18n-html],[data-i18n-block],[data-price],[data-date],[data-i18n-skip]';
  var originals = new WeakMap(); // mixed-content text node -> its Russian text

  /* First pass over plain text: tag single-text elements, remember the rest. */
  function collectText(root) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        var parent = node.parentElement;
        if (!parent || parent.closest(SKIP)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var mixed = [];
    var node;
    while ((node = walker.nextNode())) {
      var original = originals.has(node) ? originals.get(node) : node.nodeValue;
      var key = norm(original);
      if (!key || !TEXT.hasOwnProperty(key)) continue;
      var parent = node.parentElement;
      if (parent.childNodes.length === 1 && !originals.has(node)) {
        parent.setAttribute('data-i18n', key);
      } else {
        if (!originals.has(node)) originals.set(node, original);
        mixed.push(node);
      }
    }
    return mixed;
  }

  function applyText(root) {
    var mixed = collectText(root);
    mixed.forEach(function (node) {
      var original = originals.get(node);
      var lead = original.match(/^\s*/)[0];
      var trail = original.match(/\s*$/)[0];
      var value = lead + t(original) .replace(/^\s+|\s+$/g, '') + trail;
      if (node.nodeValue !== value) node.nodeValue = value;
    });
    root.querySelectorAll('[data-i18n]').forEach(function (el) {
      setText(el, t(el.getAttribute('data-i18n')));
    });
    root.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var entry = HTML[el.getAttribute('data-i18n-html')];
      if (!entry) return;
      var html = entry[LANGS.indexOf(state.lang)];
      if (state.lang === 'ru' && !el.__i18nTouched) return; // server HTML is already Russian
      el.__i18nTouched = true;
      el.innerHTML = html;
    });
  }

  /* Database fields: data-ru / data-en / data-uz. */
  function applyFields(root) {
    root.querySelectorAll('[data-ru]').forEach(function (el) {
      var value = state.lang === 'ru' ? '' : (el.getAttribute('data-' + state.lang) || '');
      var fallback = state.lang !== 'ru' && !value.trim();
      if (!value.trim()) value = el.getAttribute('data-ru') || '';
      el.toggleAttribute('data-i18n-fallback', fallback);
      setText(el, value);
    });
    root.querySelectorAll('[data-i18n-block]').forEach(function (el) {
      if (!el.__ru) {
        el.__ru = document.createDocumentFragment();
        Array.prototype.forEach.call(el.childNodes, function (child) {
          if (child.nodeName !== 'TEMPLATE') el.__ru.appendChild(child.cloneNode(true));
        });
      }
      var tpl = state.lang === 'ru' ? null : el.querySelector(':scope > template[data-lang="' + state.lang + '"]');
      var useTemplate = tpl && norm(tpl.content.textContent) !== '';
      var wanted = useTemplate ? state.lang : 'ru';
      el.toggleAttribute('data-i18n-fallback', state.lang !== 'ru' && !useTemplate);
      if (el.__shown === wanted || (!el.__shown && wanted === 'ru')) { el.__shown = wanted; return; }
      Array.prototype.slice.call(el.childNodes).forEach(function (child) {
        if (child.nodeName !== 'TEMPLATE') el.removeChild(child);
      });
      var first = el.firstChild;
      el.insertBefore((useTemplate ? tpl.content : el.__ru).cloneNode(true), first);
      el.__shown = wanted;
    });
  }

  var ATTRS = ['aria-label', 'alt', 'title', 'placeholder'];
  var attrOriginals = new WeakMap();

  function applyAttributes(root) {
    var selector = ATTRS.map(function (a) { return '[' + a + ']'; }).join(',');
    root.querySelectorAll(selector).forEach(function (el) {
      if (el.closest('[data-i18n-skip]')) return;
      var store = attrOriginals.get(el);
      if (!store) { store = {}; attrOriginals.set(el, store); }
      ATTRS.forEach(function (name) {
        if (!el.hasAttribute(name)) return;
        if (!(name in store)) store[name] = el.getAttribute(name);
        var original = store[name];
        var value = null;
        if (name === 'alt' && state.lang !== 'ru') value = el.getAttribute('data-alt-' + state.lang) || null;
        if (value == null) value = translateLabel(original);
        if (value == null || state.lang === 'ru') value = original;
        if (el.getAttribute(name) !== value) el.setAttribute(name, value);
      });
    });
    /* Headings split into words for the reveal animation are read by their
       aria-label; keep it equal to the visible text. */
    root.querySelectorAll('.split-heading').forEach(function (el) {
      el.setAttribute('aria-label', norm(el.textContent));
    });
  }

  /* ---------- money ---------- */

  /* '70000', '70 000', '1,200,000', '12.50' -> number. '' -> 0 (the field's
     default). Text that is not a number (e.g. "по договорённости") -> null. */
  function parseAmount(raw) {
    var text = String(raw == null ? '' : raw).replace(/[\s  ]/g, '');
    if (!text) return 0;
    if (/^\d{1,3}([.,]\d{3})+$/.test(text)) return parseInt(text.replace(/[.,]/g, ''), 10);
    if (/^\d+([.,]\d+)?$/.test(text)) return parseFloat(text.replace(',', '.'));
    return null;
  }

  function groupDigits(amount) {
    var fixed = Math.round(amount * 100) / 100;
    var parts = String(fixed).split('.');
    var whole = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    if (!parts[1]) return whole;
    return whole + (state.lang === 'en' ? '.' : ',') + (parts[1].length === 1 ? parts[1] + '0' : parts[1]);
  }

  function formatMoney(amount, currency, lang) {
    currency = currency || state.currency;
    lang = lang || state.lang;
    var number = groupDigits(amount);
    if (currency === 'USD') return '$' + number;
    if (currency === 'EUR') return '€' + number;
    return number + ' ' + UZS_UNIT[lang];
  }

  /* Price of an element carrying data-uzs / data-usd / data-eur. */
  function priceOf(el, currency) {
    currency = currency || state.currency;
    var raw = el.getAttribute('data-' + currency.toLowerCase());
    return { raw: raw == null ? '' : raw, amount: parseAmount(raw) };
  }

  function priceText(el) {
    var price = priceOf(el);
    return price.amount == null ? norm(price.raw) : formatMoney(price.amount);
  }

  function applyPrices(root) {
    root.querySelectorAll('[data-price]').forEach(function (el) { setText(el, priceText(el)); });
  }

  /* ---------- dates ---------- */

  function formatDate(iso) {
    var m = String(iso || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!m) return null;
    var y = +m[1], mo = +m[2], d = +m[3];
    if (state.lang === 'uz') return d + '-' + UZ_MONTHS[mo - 1] + ', ' + y;
    try {
      return new Intl.DateTimeFormat(state.lang === 'en' ? 'en-GB' : 'ru-RU', {
        day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC'
      }).format(new Date(Date.UTC(y, mo - 1, d)));
    } catch (e) {
      return (d < 10 ? '0' : '') + d + '.' + (mo < 10 ? '0' : '') + mo + '.' + y;
    }
  }

  function applyDates(root) {
    root.querySelectorAll('[data-date]').forEach(function (el) {
      var value = formatDate(el.getAttribute('data-date'));
      if (value) setText(el, value);
    });
  }

  /* ---------- switcher in the side menu ---------- */

  function buildSwitcher() {
    var links = document.querySelector('.nav-overlay .nav-overlay-links');
    if (!links || document.querySelector('.meros-preferences')) return;
    var box = document.createElement('div');
    box.className = 'meros-preferences';
    box.setAttribute('role', 'group');
    box.setAttribute('aria-label', 'Язык и валюта');

    function group(label, values, labels, attr) {
      var row = document.createElement('div');
      row.className = 'pref-group';
      var title = document.createElement('span');
      title.className = 'pref-label';
      title.textContent = label;
      var options = document.createElement('div');
      options.className = 'pref-options';
      options.setAttribute('role', 'group');
      options.setAttribute('aria-label', label);
      values.forEach(function (value) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'pref-option';
        button.setAttribute(attr, value);
        button.textContent = labels ? labels[value] : value;
        options.appendChild(button);
      });
      row.appendChild(title);
      row.appendChild(options);
      return row;
    }

    box.appendChild(group('Язык', LANGS, LANG_LABELS, 'data-pref-lang'));
    box.appendChild(group('Валюта', CURRENCIES, null, 'data-pref-currency'));
    links.insertAdjacentElement('afterend', box);

    box.addEventListener('click', function (event) {
      var button = event.target.closest('.pref-option');
      if (!button) return;
      if (button.hasAttribute('data-pref-lang')) setLang(button.getAttribute('data-pref-lang'));
      else setCurrency(button.getAttribute('data-pref-currency'));
    });
  }

  function markSwitcher() {
    document.querySelectorAll('[data-pref-lang]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-pref-lang') === state.lang));
    });
    document.querySelectorAll('[data-pref-currency]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-pref-currency') === state.currency));
    });
  }

  /* ---------- apply ---------- */

  function apply(root) {
    root = root || document;
    var html = document.documentElement;
    html.lang = state.lang;
    html.setAttribute('data-currency', state.currency);
    try {
      applyText(root === document ? html : root);
      applyFields(root);
      applyPrices(root);
      applyDates(root);
      applyAttributes(root);
      markSwitcher();
    } finally {
      html.classList.remove('i18n-pending');
    }
  }

  function changed() {
    apply();
    document.dispatchEvent(new CustomEvent('meros:prefschange', {
      detail: { lang: state.lang, currency: state.currency }
    }));
  }

  function setLang(lang) {
    if (LANGS.indexOf(lang) < 0 || lang === state.lang) return;
    state.lang = lang;
    write(LANG_KEY, lang);
    changed();
  }

  function setCurrency(currency) {
    if (CURRENCIES.indexOf(currency) < 0 || currency === state.currency) return;
    state.currency = currency;
    write(CURRENCY_KEY, currency);
    changed();
  }

  window.MerosI18n = {
    lang: function () { return state.lang; },
    currency: function () { return state.currency; },
    t: t,
    parseAmount: parseAmount,
    formatMoney: formatMoney,
    priceOf: priceOf,
    setLang: setLang,
    setCurrency: setCurrency,
    apply: apply
  };

  /* The other tab changed the choice: follow it. */
  window.addEventListener('storage', function (event) {
    if (event.key === LANG_KEY && LANGS.indexOf(event.newValue) > -1) { state.lang = event.newValue; changed(); }
    if (event.key === CURRENCY_KEY && CURRENCIES.indexOf(event.newValue) > -1) { state.currency = event.newValue; changed(); }
  });

  buildSwitcher();
  apply();
})();
