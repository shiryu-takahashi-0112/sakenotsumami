# つまみ写真の生成指示

写真は `images/<レシピのid>.jpg` に置くと、一覧と詳細に自動で表示される。
無いあいだは、黄色の地にアイコンが出る。

## 共通の条件

- 正方形（1:1）で生成する。一覧では72px、詳細では横長4:3に切り抜いて使う。
- 料理を中央に置き、四辺に少し余白を残す（4:3に切り抜いても欠けないように）。
- 文字・ロゴ・手・人物は入れない。

各料理の指示文の後ろに、次の共通文をつなげて使う。

```plain text
, home-cooked Japanese izakaya-style snack served on a small handmade ceramic plate, on a dark wooden counter, soft natural window light from the side, shot from a 45-degree angle, shallow depth of field, realistic food photography, appetizing, no text, no people, no hands, square composition with the dish centered, plain softly blurred background with no bottles, no labels, no lettering
```

## 料理ごとの指示文

過去の生成では背景に酒瓶の和文字や人物が入りやすかったため、共通文の末尾に背景の条件を追記した。

| id | 料理 | 指示文 |
|---|---|---|
| mugen-piman | 無限ピーマン | `Thinly julienned green bell peppers tossed with canned tuna and sesame oil, glossy, piled in a small mound` |
| shiodare-cabbage | 塩だれキャベツ | `Raw cabbage torn into bite-size pieces, dressed with sesame oil and garlic salt sauce, sprinkled with white sesame seeds` |
| tataki-kyuri | たたききゅうりの梅しそ和え | `Smashed cucumber chunks dressed with chopped umeboshi plum paste and thin strips of green shiso leaves` |
| nagaimo-butter | 長芋のバター醤油焼き | `Round slices of Japanese nagaimo yam pan-fried golden brown with butter and soy sauce, sprinkled with black pepper` |
| avocado-wasabi | アボカドのわさび醤油 | `Sliced avocado fanned out, drizzled with soy sauce, a dab of wasabi, topped with shredded nori seaweed` |
| chikuwa-isobe | ちくわの磯辺揚げ焼き | `Chikuwa fish cake pieces cut diagonally, coated in crispy batter speckled with green aonori seaweed` |
| atsuage-miso | 厚揚げのねぎ味噌焼き | `Cubes of thick fried tofu (atsuage) topped with caramelized miso paste and chopped green onions, toasted` |
| sunagimo-garlic | 砂肝のにんにく炒め | `Stir-fried sliced chicken gizzards with golden garlic chips, black pepper, a lemon wedge on the side` |
| tebanaka-shio | 手羽中の塩焼き | `Salt-grilled chicken wing mid-sections with crispy golden skin, black pepper, a lemon wedge on the side` |
| camembert-honey | カマンベールのはちみつ焼き | `Whole baked camembert cheese with a crosshatched melting top, drizzled with honey and crushed walnuts, black pepper, a few baguette slices` |
| tomato-marinade | ミニトマトのマリネ | `Halved cherry tomatoes marinated in olive oil and lemon, sprinkled with dried basil, glistening` |
| mushroom-ajillo | マッシュルームのアヒージョ | `Whole button mushrooms bubbling in garlic olive oil with a red chili pepper, served in a small cast-iron skillet` |
| namaham-cheese | 生ハムのクリームチーズ巻き | `Six rolls of prosciutto wrapped around cream cheese sticks, drizzled with honey and black pepper` |
| shirasu-yakko | しらすと大葉の冷奴 | `A block of chilled silken tofu topped with a pile of shirasu whitebait and thin shiso leaf strips, drizzled with sesame oil` |
| iburigakko-cheese | いぶりがっこクリームチーズ | `Thin slices of smoked Japanese daikon pickle (iburigakko) each topped with a piece of cream cheese, black pepper` |
| aburaage-natto | 油揚げの納豆詰め焼き | `Crispy pan-grilled fried tofu pouches (aburaage) stuffed with natto and green onions, cut in half showing the filling` |
| shiokara-jagabutter | 塩辛じゃがバター | `Steamed whole potato split open with a cross cut, a melting pat of butter and salted squid (ika no shiokara) on top` |
| chicken-negishio | 鶏もものねぎ塩焼き | `Sliced pan-seared chicken thigh with crispy skin, topped generously with chopped green onion salt sauce with lemon` |
| yakinasu | 焼きなすのしょうが醤油 | `Grilled Japanese eggplant peeled and torn into strips, topped with grated ginger and bonito flakes, soy sauce` |
| edamame-peperoncino | 枝豆のペペロンチーノ | `Edamame pods stir-fried with olive oil, sliced garlic and red chili pepper flakes, glossy` |
| moyashi-namul | もやしのナムル | `Korean-style bean sprout namul seasoned with sesame oil and salt, sprinkled with white sesame seeds` |
| saba-lemon | サバ缶の玉ねぎレモンマリネ | `Chunks of canned mackerel tossed with thinly sliced onion, lemon and olive oil, black pepper, a lemon slice` |
| kimchi-yakko | キムチ奴 | `A block of chilled silken tofu topped with chopped red kimchi, sliced green onions and torn Korean seaweed, drizzled with sesame oil` |
| tako-carpaccio | タコのカルパッチョ | `Thinly sliced boiled octopus arranged in a circle, topped with sliced onion and baby salad leaves, drizzled with olive oil and lemon, black pepper` |
| maguro-yukke | まぐろのユッケ風 | `Diced raw red tuna dressed in a glossy sweet-spicy gochujang sauce, a bright raw egg yolk in the center, sprinkled with green onions and sesame seeds` |
| caprese | カプレーゼ | `Alternating slices of red tomato and fresh mozzarella with green basil leaves, drizzled with olive oil, sprinkled with salt and black pepper` |
| kanikama-kyuri | カニカマときゅうりの中華和え | `Shredded crab sticks and julienned cucumber tossed in a light Chinese vinegar and sesame oil dressing, sprinkled with white sesame seeds` |
| onion-okaka | オニオンスライスのおかか醤油 | `A heap of thinly sliced white onion topped generously with fluttering bonito flakes, ponzu sauce pooled at the base` |
| tomato-shiokombu | 冷やしトマトの塩昆布和え | `Chilled red tomato wedges tossed with dark strands of salted kombu seaweed and a little sesame oil, glistening` |
| creamcheese-okaka | クリームチーズのおかか醤油 | `Cubes of white cream cheese topped with bonito flakes and chopped green onions, a drizzle of soy sauce` |
| salmon-marinade | サーモンのレモンマリネ | `Thin slices of raw salmon marinated in lemon and olive oil with sliced onion, sprinkled with dill, a thin lemon slice on the side` |
| nagaimo-ume | 長芋の梅おかか和え | `Crisp sticks of peeled Japanese nagaimo yam dressed with mashed umeboshi plum, topped with bonito flakes` |
| celery-asazuke | セロリの浅漬け | `Lightly pickled thin diagonal slices of celery with a few celery leaves and red chili rings, fresh and crisp` |
| carrot-rapee | キャロットラペ | `French carrot salad of finely shredded bright orange carrots with raisins, dressed in olive oil and vinegar, glossy` |
| zasai-tofu | ザーサイ豆腐 | `Chilled silken tofu topped with finely chopped zha cai pickled mustard stem and green onion, drizzled with sesame oil and red chili oil` |
| katsuo-tataki | かつおのたたき 香味のせ | `Slices of seared bonito tataki with a red center and charred edges, topped with sliced onion, shiso and myoga strips, ponzu sauce` |
| shungiku-salad | 春菊とのりの韓国風サラダ | `Fresh raw shungiku chrysanthemum greens tossed with torn Korean seaweed and sesame dressing, sprinkled with sesame seeds` |
| mentai-dip | 明太クリームチーズディップ | `A small bowl of pale pink mentaiko cream cheese dip surrounded by crackers and cucumber and carrot sticks` |
| daikon-hotate | 大根とホタテ缶のサラダ | `Julienned daikon radish salad mixed with flaked canned scallops and a little mayonnaise, topped with radish sprouts` |
| thai-cucumber | タイ風きゅうりのサラダ | `Thai-style smashed cucumber salad with fish sauce and lime dressing, red chili rings, crushed peanuts and fresh cilantro` |
| yodare-dori | よだれ鶏 | `Sliced tender steamed chicken breast drenched in glossy red chili oil sauce with chopped green onion and sesame seeds, Sichuan style` |
| butabara-moyashi | 豚バラともやしのレンジ蒸し | `Steamed thin pork belly slices layered over bean sprouts on a plate, drizzled with ponzu, sprinkled with green onions` |
| nasu-chukadare | レンジ蒸しなすの中華だれ | `Soft steamed peeled eggplant torn into strips, topped with a Chinese sweet vinegar sauce with minced green onion and ginger` |
| kabocha-cheese-salad | かぼちゃとクリームチーズのサラダ | `Chunky mashed kabocha squash salad with cubes of cream cheese and crushed mixed nuts, black pepper` |
| mentai-potesala | 明太ポテトサラダ | `Creamy Japanese potato salad mixed with pink mentaiko cod roe, topped with chopped green onions` |
| asari-sakamushi | あさりの酒蒸し | `Opened steamed asari clams in a light sake broth with garlic slices, a melting pat of butter and green onions, in a shallow bowl` |
| broccoli-okakamayo | ブロッコリーのおかかマヨ | `Bright green broccoli florets tossed with mayonnaise, soy sauce and bonito flakes` |
| horenso-goma | ほうれん草のごま和え | `Japanese spinach goma-ae, blanched spinach cut into short lengths and dressed with ground sesame sauce, neatly mounded` |
| okura-okaka | オクラのおかか和え | `Bright green okra pods cut diagonally showing star-shaped cross sections, tossed with bonito flakes and soy sauce` |
| eringi-butter | エリンギのバター醤油 | `Hand-torn king oyster mushroom strips glossy with butter and soy sauce, black pepper and green onions` |
| range-mapo | レンジ麻婆豆腐 | `Mapo tofu with cubes of tofu in a glossy red spicy minced pork sauce, sprinkled with chopped green onions, in a small bowl` |
| sasami-wasabi | ささみのわさび和え | `Shredded steamed chicken tenderloin tossed with julienned cucumber and wasabi soy sauce, topped with shredded nori` |
| satsumaimo-butter | さつまいものバター醤油 | `Round slices of purple-skinned sweet potato glazed with butter and soy sauce, sprinkled with black sesame seeds` |
| furofuki-daikon | レンジふろふき大根 | `Thick rounds of tender simmered daikon radish topped with sweet glossy miso paste and a sliver of yuzu peel` |
| sausage-cabbage | ソーセージとキャベツのレンジ蒸し | `Steamed plump sausages with scored skins on a bed of soft cabbage, with a spoon of whole-grain mustard, black pepper` |
| yum-woonsen | ヤムウンセン | `Thai glass noodle salad yum woon sen with pink shrimp, halved cherry tomatoes, sliced red onion, red chili and fresh cilantro` |
| enoki-nametake | えのきの自家製なめたけ | `Homemade nametake, soft enoki mushrooms simmered in a glossy brown soy and mirin sauce, served over grated daikon` |
| hakusai-millefeuille | 白菜と豚バラのミルフィーユ蒸し | `Napa cabbage and pork belly mille-feuille, layered cabbage and pork packed upright in a round dish, steamed and juicy` |
| renkon-kinpira | れんこんのきんぴら | `Stir-fried style lotus root slices glazed in sweet soy sauce with red chili rings and sesame seeds, showing their lacy holes` |
| snap-pea-anchovy | スナップえんどうのアンチョビ和え | `Bright green sugar snap peas, some split open showing peas, tossed with chopped anchovy, garlic and olive oil` |
| buta-kimchi | 豚キムチ | `Stir-fried pork and red kimchi with garlic chives, glossy and steaming, sprinkled with sesame seeds` |
| nira-tama | ニラ玉 | `Fluffy Chinese-style scrambled eggs with bright green garlic chives, soft and glossy` |
| nira-chijimi | にらチヂミ | `Crispy golden Korean chive pancake (buchimgae) cut into wedges, with a small dish of vinegar soy dipping sauce` |
| garlic-shrimp | ガーリックシュリンプ | `Hawaiian-style garlic shrimp with shells on, sauteed in golden garlic butter, black pepper, a lemon wedge` |
| german-potato | ジャーマンポテト | `German potatoes, golden pan-fried potato chunks with crispy bacon and softened onion, black pepper and parsley` |
| goya-champuru | ゴーヤチャンプルー | `Okinawan goya champuru, stir-fried bitter melon with tofu, pork and scrambled egg, topped with bonito flakes` |
| shogayaki | 豚こまのしょうが焼き | `Ginger pork shogayaki, glossy sweet soy and ginger glazed thin pork slices with onion, finely shredded cabbage on the side` |
| tori-tsukune | 鶏つくねの照り焼き | `Glossy teriyaki chicken meatballs tsukune shaped into ovals, with a raw egg yolk in a small dish for dipping` |
| dashimaki | だし巻き卵 | `Japanese rolled omelette dashimaki tamago sliced to show golden layers, with a small mound of grated daikon` |
| yaki-shishito | 焼きししとうのおかか醤油 | `Blistered green shishito peppers with charred spots, tossed with soy sauce and bonito flakes` |
| asparagus-bacon | アスパラとベーコンのソテー | `Sauteed green asparagus pieces with crispy bacon, glossy with olive oil, black pepper` |
| ika-butter | イカのバター醤油焼き | `Pan-fried squid rings and tentacles glossy with butter and soy sauce, sprinkled with chopped green onions` |
| buri-teriyaki | ぶりの照り焼き | `Two pieces of yellowtail teriyaki with a shiny dark caramelized glaze, a small pile of shredded green onion on top` |
| hotate-butter | ホタテのバターソテー | `Seared scallops with a deep golden crust, glistening with brown butter and soy, black pepper, a lemon wedge` |
| konnyaku-pirikara | こんにゃくのピリ辛炒め | `Hand-torn konnyaku pieces stir-fried in a dark sweet-spicy soy glaze with red chili rings and bonito flakes` |
| gapao-lettuce | ガパオのレタス包み | `Thai basil minced chicken gapao with diced red pepper and onion, served with crisp lettuce cups for wrapping` |
| samgyeopsal | サムギョプサル風 豚バラ焼き | `Crispy pan-grilled thick pork belly slices with garlic chips, fresh lettuce leaves and a small dish of red ssamjang paste` |
| dakgalbi | チーズタッカルビ | `Korean cheese dakgalbi, spicy red chicken and cabbage stir-fry with a pool of stretchy melted cheese in the center, in a small skillet` |
| komatsuna-nampla | 小松菜のナンプラー炒め | `Stir-fried komatsuna greens with crushed garlic and dried red chili, glossy with fish sauce, Southeast Asian street style` |
| ebi-chili | えびチリ | `Chinese chili shrimp ebi chili, plump shrimp coated in a glossy red sweet-spicy sauce with minced green onion` |
| tofu-steak | 豆腐ステーキ | `Pan-seared tofu steaks with a crisp golden crust, glazed with garlic soy butter, topped with garlic chips and green onions` |
| bulgogi | 牛こまのプルコギ | `Korean beef bulgogi, thin slices of beef stir-fried with onion, carrot and chives in a sweet soy glaze, sesame seeds` |
| shiitake-mayo | しいたけのマヨチーズ焼き | `Shiitake mushroom caps filled with mayonnaise and melted golden cheese, sprinkled with parsley, on a small plate` |
| hanpen-cheese | はんぺんのチーズ焼き | `Triangles of puffy Japanese hanpen fish cake topped with toasted melted cheese, wrapped with a strip of nori` |
| oil-sardine | オイルサーディンのねぎ醤油焼き | `An open tin of oil sardines bubbling hot, topped with sliced green onion and soy sauce, shichimi pepper, placed on a small plate` |
| aburaage-pizza | 油揚げピザ | `Crispy fried tofu sheet used as a pizza base, topped with tomato sauce, ham, onion and bubbling melted cheese, cut into squares` |
| shishamo | 焼きししゃも | `A row of grilled shishamo smelt fish with golden crispy skin, a lemon wedge and a dab of mayonnaise` |
| satsumaage-aburi | さつま揚げの炙り しょうが醤油 | `Toasted Japanese satsuma-age fried fish cakes with crosshatch char marks, topped with grated ginger and green onions` |
| asparagus-cheese | アスパラの粉チーズ焼き | `Whole roasted green asparagus spears with a crust of toasted grated parmesan, black pepper` |
| zucchini-cheese | ズッキーニのチーズ焼き | `Round slices of zucchini topped with golden melted cheese and dried basil, neatly arranged` |
| salmon-foil | 鮭のきのこホイル焼き | `Salmon fillet baked in opened aluminum foil with shimeji mushrooms, onion and melting butter, a lemon wedge` |
| enoki-bacon | えのきのベーコン巻き | `Bundles of enoki mushrooms wrapped in crispy golden bacon, black pepper, arranged in a row` |
| yaki-tomato | 焼きトマトのパン粉焼き | `Halved roasted tomatoes topped with golden garlic parmesan breadcrumbs and parsley, juicy and blistered` |
| bruschetta | トマトのブルスケッタ | `Italian bruschetta, toasted baguette slices topped with diced fresh tomato, olive oil and green basil` |
| piman-maruyaki | ピーマンの丸焼き | `Whole roasted green bell peppers with blistered charred skin, topped with bonito flakes and soy sauce` |
| chicken-misomayo | 鶏ももの味噌マヨ焼き | `Bite-size chicken thigh pieces broiled with a golden caramelized miso mayonnaise topping, sprinkled with green onions` |
| negi-grill | 長ねぎのオーブン焼き | `Roasted thick Japanese leeks with charred edges and soft glossy centers, black pepper, a small spoon of whole-grain mustard` |
| mochi-cheese-nori | お餅のチーズのり焼き | `Small toasted puffed mochi rice cake pieces with melted cheese and soy sauce, each wrapped with a strip of nori` |
| tunamayo-piman | ツナマヨのピーマン詰め焼き | `Halved green bell peppers stuffed with tuna mayonnaise and topped with bubbling golden cheese, black pepper` |
| nachos | ナチョス | `Mexican nachos, tortilla chips covered with melted cheese and topped with fresh diced tomato and onion salsa` |

## 2026-10-09 に足した20品（写真はまだ無い）

写真を置いたら、`python3 tools/photos.py` で変換したあと、`python3 tools/build_pages.py` も実行する（検索用ページは、写真が無いあいだ黄色の地を出している）。

| id | 料理 | 指示文 |
|---|---|---|
| kinoko-marinade | きのこのレンジマリネ | `Steamed shimeji and sliced king oyster mushrooms marinated in olive oil and vinegar, glossy, sprinkled with black pepper and dried parsley` |
| maitake-ponzu | 舞茸のバターポン酢 | `Hand-torn maitake mushrooms pan-seared golden brown with butter and ponzu sauce, topped with chopped green onions` |
| gyu-shigure | 牛肉のしぐれ煮 | `Japanese beef shigureni, thinly sliced beef simmered in sweet soy sauce with julienned ginger, glossy and dark, piled in a small mound` |
| gyu-garlic | 牛こまのガーリックペッパー炒め | `Stir-fried thin beef slices and onion wedges with coarse black pepper, topped with crispy golden garlic chips` |
| tomato-tamago | トマトと卵の中華炒め | `Chinese tomato and egg stir-fry, soft fluffy scrambled egg with juicy tomato wedges, glossy` |
| uzura-bacon | うずら卵のベーコン巻き | `Quail eggs wrapped in crispy bacon strips, held with toothpicks, toasted, sprinkled with black pepper` |
| tofu-shiokombu | 豆腐の塩昆布ごま油がけ | `Chilled silken tofu cubes topped with shio kombu kelp strips, chopped green onions, sesame oil and white sesame seeds` |
| aburaage-negiponzu | カリカリ油揚げのねぎポン酢 | `Crispy toasted fried tofu pouches (aburaage) cut into squares, topped with chopped green onions, ponzu sauce and shichimi pepper` |
| torikawa | 鶏皮のパリパリ焼き | `Crispy pan-fried chicken skin pieces, golden and crunchy like crackers, sprinkled with salt and black pepper, a lemon wedge on the side` |
| sasami-umeshiso | ささみの梅しそチーズ焼き | `Butterflied chicken tenderloins topped with umeboshi paste, green shiso leaves and melted golden cheese, toasted` |
| buta-negishio-lemon | 豚バラのねぎ塩レモン | `Pan-seared pork belly slices topped with chopped green onion salt sauce with sesame oil and lemon, a lemon slice on the side` |
| range-butashabu | レンジ豚しゃぶの香味サラダ | `Thin sliced cooked pork shabu-shabu on a bed of torn lettuce, julienned myoga ginger and shiso leaves, drizzled with ponzu sauce` |
| aji-namerou | あじのなめろう | `Japanese aji namerou, finely chopped raw horse mackerel mixed with miso, ginger and green onions, shaped into a small mound on a shiso leaf` |
| ebi-avocado | えびとアボカドのわさびマヨ | `Cubed avocado and boiled peeled shrimp tossed in a creamy wasabi mayonnaise dressing` |
| chikuwa-kyuri | ちくわときゅうりのごまポン酢 | `Sliced chikuwa fish cake rings and thin cucumber slices dressed with ground sesame and ponzu sauce` |
| potato-galette | じゃがいものチーズガレット | `Crispy golden potato galette made of shredded potato and melted cheese, cut into wedges, sprinkled with black pepper` |
| gobo-chips | ごぼうチップス | `Crispy thin burdock root chips sprinkled with salt and green aonori seaweed flakes` |
| zucchini-namul | ズッキーニのナムル | `Korean-style zucchini namul: thick half-moon slices of cooked zucchini (courgette) with soft, slightly translucent pale cream flesh and dark green skin edges, clearly zucchini and not cucumber (no seeds pattern, no crisp raw look), glossy with sesame oil and garlic, sprinkled with white sesame seeds` |
| cheese-senbei | チーズせんべい | `Crispy golden cheese crisps, small lacy squares, some sprinkled with black pepper and some with green aonori seaweed` |
| gyoza-pizza | 餃子の皮ピザ | `Mini pizzas made on round gyoza wrappers with ketchup, bacon, thin green bell pepper rings and melted golden cheese, crispy edges` |

## 2026-10-10 に足した80品（写真はまだ無い）

写真を置いたら、`python3 tools/photos.py` で変換したあと、`python3 tools/build_pages.py` も実行する。

| id | 料理 | 指示文 |
|---|---|---|
| myoga-amazu | みょうがの甘酢漬け | `Myoga ginger buds cut in half lengthwise, pickled in sweet vinegar, glowing translucent pale pink, arranged in a small pile` |
| radish-butter | ラディッシュのバターのせ | `Fresh red radishes with short green tops, some halved, each topped with a thin slice of cold butter, sprinkled with coarse flaky salt` |
| kabu-lemon | かぶの塩レモン和え | `Paper-thin half-moon slices of white Japanese turnip tossed with chopped turnip greens, olive oil and lemon juice, topped with fine strips of lemon zest` |
| somtam-daikon | 大根のソムタム風サラダ | `Thai som tam style salad made with finely julienned daikon radish and carrot, quartered cherry tomatoes, sliced red chili, topped with crushed peanuts` |
| pajeori | ねぎのパジョリ | `Korean pajeori scallion salad, very finely shredded white leek strands tossed with sesame oil and red chili flakes, sprinkled with sesame seeds, piled high` |
| satoimo-yuzumiso | 里芋のゆず味噌がけ | `Peeled steamed Japanese taro potatoes, smooth and creamy white, topped with glossy sweet miso sauce and grated yellow yuzu zest` |
| chingensai-oyster | チンゲン菜のオイスター蒸し | `Steamed bok choy with bright green leaves and stems cut into long wedges, drizzled with glossy dark oyster sauce and sesame oil` |
| shintama-range | 新玉ねぎの丸ごとレンジ蒸し | `A whole steamed new onion, soft and translucent, cross-cut on top and opened slightly, with melting butter and soy sauce, topped with bonito flakes and chopped green onion` |
| tataki-gobo | たたきごぼう | `Japanese tataki gobo, short lengths of lightly smashed burdock root coated in creamy ground white sesame and vinegar dressing` |
| corn-butter | とうもろこしのバター醤油 | `Corn on the cob cut into thick rounds, glazed with melted butter and soy sauce, lightly browned and glossy` |
| mushroom-balsamic | マッシュルームのバルサミコソテー | `Halved brown mushrooms sauteed golden with sliced garlic, glazed with dark glossy balsamic reduction, sprinkled with black pepper` |
| jaga-sanra | じゃがいもの酢辣炒め | `Chinese hot and sour shredded potato stir-fry, crisp translucent thin potato strips with green bell pepper strips and dried red chili rings` |
| renkon-steak | れんこんのステーキ | `Thick round slices of lotus root pan-seared golden brown, glazed with sweet soy sauce, sprinkled with black pepper and chopped green onion` |
| ingen-sichuan | いんげんの四川風炒め | `Sichuan dry-fried green beans, blistered and wrinkled with charred spots, tossed with minced pickled zha cai, garlic and red chili rings` |
| ninjin-shirishiri | にんじんしりしり | `Okinawan carrot shirishiri, finely shredded stir-fried carrot mixed with flaked tuna and soft scrambled egg, bright orange and yellow` |
| kabocha-cumin | かぼちゃのクミン焼き | `Thin wedges of kabocha squash with green skin, roasted with olive oil and cumin seeds, edges caramelized, sprinkled with black pepper` |
| mushroom-escargot | マッシュルームのエスカルゴバター焼き | `Upturned white mushroom caps filled with bubbling garlic parsley butter and toasted breadcrumbs, baked, arranged in a row` |
| nasu-dengaku | なすの田楽 | `Japanese nasu dengaku, halved eggplants with crosshatched flesh, topped with caramelized sweet miso glaze and white sesame seeds` |
| eringi-gochujang | エリンギのコチュジャン焼き | `Hand-torn king oyster mushroom strips roasted with red gochujang glaze, slightly charred edges, topped with sesame seeds and chopped green onion` |
| paprika-marinade | 焼きパプリカのマリネ | `Roasted red and yellow bell pepper strips, peeled, silky and glossy, marinated in olive oil and vinegar, sprinkled with black pepper` |
| saladchicken-bangbangji | サラダチキンのバンバンジー | `Shredded cooked chicken breast piled on thin julienned cucumber, drizzled with creamy white sesame sauce and a few drops of red chili oil` |
| tebamoto-sujoyu | 手羽元のさっぱり煮 | `Chicken drumsticks braised in glossy dark soy and vinegar sauce, tender and lacquered, with thin slices of ginger, a little sauce pooled in the bowl` |
| tori-negima | フライパンねぎま | `Pan-fried bite-size chicken thigh pieces and charred Japanese leek segments glazed with sweet soy yakitori tare, glossy, no skewers` |
| tandoori-chicken | タンドリーチキン | `Bite-size pieces of tandoori chicken with reddish-orange spiced yogurt marinade, charred edges, with a lemon wedge on the side` |
| tori-yuzukosho-mushi | 鶏ももとしめじの柚子こしょう蒸し | `Steamed bite-size chicken thigh pieces with shimeji mushrooms in a little clear broth, a dab of green yuzu kosho, sprinkled with chopped green onions, in a small shallow bowl` |
| mune-panko-yaki | 鶏むねのハーブパン粉焼き | `Sliced chicken breast pieces topped with golden crispy herbed panko breadcrumbs and parmesan, flecks of green parsley` |
| negi-chashu | ねぎチャーシュー | `Thin strips of Chinese chashu roast pork tossed with fine white shredded leek, glistening with sesame oil and a little red chili oil, sprinkled with sesame seeds` |
| hoikoro | 回鍋肉 | `Chinese twice-cooked pork stir-fry with thin pork belly slices, cabbage chunks and green bell pepper, coated in glossy dark sweet bean sauce` |
| buta-misozuke | 豚肩ロースの味噌漬け焼き | `Slices of grilled miso-marinated pork shoulder with caramelized browned miso edges, arranged over green shiso leaves` |
| range-shumai | レンジしゅうまい | `Round steamed pork shumai dumplings coated in thin shredded wonton wrapper strips, with a small dab of yellow mustard and a tiny dish of soy sauce` |
| butamaki-okura | オクラの豚巻きポン酢 | `Okra pods wrapped in thin pork slices, steamed and cut in half to show green okra cross-sections, drizzled with ponzu, a small mound of grated ginger` |
| buta-sate | 豚肉のサテ風 ピーナッツだれ | `Southeast Asian style grilled pork satay skewers with charred edges, a small bowl of creamy peanut sauce on the side` |
| roastbeef-yukke | ローストビーフのユッケ風 | `Thin strips of roast beef dressed in red gochujang sauce, mounded with a raw egg yolk in the center, sprinkled with green onions and sesame seeds` |
| range-japchae | レンジチャプチェ | `Korean japchae with glossy glass noodles, thin strips of beef, carrot and green bell pepper, sprinkled with sesame seeds` |
| gyu-negimaki | 牛肉のねぎ巻き焼き | `Thin beef slices rolled around green onions, grilled with sweet soy glaze, cut into short rolls showing green onion centers` |
| gyu-cumin | 牛肉とピーマンのクミン炒め | `Stir-fried thin beef slices with julienned green bell pepper and onion, speckled with whole cumin seeds and red chili flakes` |
| cornedbeef-onion | コンビーフのオニオンスライスのせ | `Flaked corned beef piled on thinly sliced white onion, drizzled with ponzu, topped with black pepper and a few daikon radish sprouts` |
| namaham-kaki | 生ハムと柿 | `Orange persimmon wedges each wrapped with a strip of prosciutto, drizzled with olive oil and cracked black pepper` |
| ham-steak | 厚切りハムステーキ | `Thick slices of pan-seared ham with crosshatch scoring and browned surface, shredded cabbage on the side, a small dollop of mustard mayonnaise` |
| ham-macaroni-salad | ハムのマカロニサラダ | `Japanese macaroni salad with elbow macaroni, diced ham, thin cucumber slices and onion, creamy mayonnaise dressing, cracked black pepper` |
| tako-kimchi | たこのキムチ和え | `Thinly sliced boiled octopus tossed with red napa cabbage kimchi and sesame oil, topped with chopped green onions and white sesame seeds` |
| salmon-poke | サーモンとアボカドのポキ | `Hawaiian-style poke, cubes of raw salmon and avocado with thin onion slices in glossy soy sesame dressing, sprinkled with sesame seeds` |
| shimesaba-yakumi | しめさばの薬味たっぷりのせ | `Slices of Japanese shimesaba vinegar-cured mackerel with silver skin lined up, topped with a mound of julienned myoga, green shiso and ginger, drizzled with ponzu` |
| ika-mekabu | いかとめかぶのしょうがポン酢 | `Thin strips of raw white squid sashimi mixed with slimy dark green mekabu seaweed in ponzu, with grated ginger and chopped green onions, in a small bowl` |
| ikura-oroshi | いくらおろし | `A small mound of grated daikon radish topped with glistening orange salmon roe (ikura), a little grated yuzu zest, in a small bowl` |
| ebi-broccoli | えびとブロッコリーの塩にんにく蒸し | `Steamed peeled shrimp and broccoli florets glazed in a light garlic salt sauce with sesame oil, Chinese style` |
| tai-negiyu | 鯛のレンジ蒸し ねぎ油がけ | `Chinese-style steamed sea bream fillets in a pool of soy sauce, topped with fine julienned green onion and ginger, glistening with hot sesame oil` |
| saba-tomato | サバ缶のレンジトマト煮 | `Chunks of canned mackerel simmered in chunky tomato sauce with sliced onion, sprinkled with dried basil, in a small shallow dish` |
| seafood-marinade | シーフードミックスのレモンマリネ | `Seafood marinade of shrimp, squid rings and small scallops with thin slices of onion and yellow bell pepper, glossy with olive oil and lemon` |
| tarako-shirataki | たらこしらたき | `Japanese shirataki konjac noodles coated with cooked pink cod roe (tarako), sprinkled with chopped green onions, in a small bowl` |
| salmon-chanchan | 鮭のちゃんちゃん焼き | `Japanese chanchan-yaki, pan-steamed salmon fillet with cabbage and onion in miso sauce, topped with a melting pat of butter` |
| tara-meuniere | たらのレモンバタームニエル | `Two golden pan-fried white cod fillets meuniere with brown butter lemon sauce, sprinkled with chopped parsley` |
| ika-gochujang | いかのコチュジャン炒め | `Korean stir-fried squid rings with onion and carrot strips in glossy red gochujang sauce, sprinkled with sesame seeds` |
| ebi-mayo | えびマヨ | `Chinese-style ebi mayo, crispy coated shrimp tossed in creamy pale pink mayonnaise sauce, on torn green lettuce leaves` |
| jako-piman | じゃこピーマン | `Julienned green bell peppers stir-fried with crispy tiny dried whitebait (chirimen jako), sprinkled with sesame seeds` |
| eihire-aburi | えいひれの炙り マヨ七味 | `Toasted dried stingray fin (eihire) torn into thin amber strips, with a small dish of mayonnaise sprinkled with red shichimi pepper` |
| iwashi-panko | いわしの香草パン粉焼き | `Butterflied sardine fillets baked with golden herb breadcrumb topping of parsley, garlic and cheese, with a lemon wedge` |
| sanma-cheese | さんま蒲焼き缶のチーズ焼き | `Canned kabayaki saury pieces in sweet soy glaze topped with melted browned cheese and sliced green onion, baked in a small gratin dish` |
| kajiki-tandoori | めかじきのタンドリー焼き | `Bite-size pieces of swordfish marinated in yogurt and curry spices, roasted with charred orange-red edges, with a lemon wedge` |
| kamaboko-mentai | かまぼこの明太マヨ焼き | `Thick slices of white kamaboko fish cake topped with toasted pink mentaiko mayonnaise, browned spots, sprinkled with chopped green onions` |
| deviled-egg | デビルドエッグ | `Halved hard-boiled eggs with the yolk filling piped back in a smooth mound, dusted with red paprika and chopped parsley, arranged in a neat row` |
| keranchim | レンジでケランチム | `Fluffy Korean steamed egg (gyeran-jjim) puffed up in a small deep ceramic bowl, topped with sliced green onions, sesame seeds and a drizzle of sesame oil` |
| ontama-kimchi | レンジ温玉のキムチのせ | `A soft poached onsen egg with a runny yolk sitting on a mound of red napa cabbage kimchi, scattered with chopped green onion and torn Korean seaweed` |
| spanish-omelet | スパニッシュオムレツ | `Thick Spanish potato omelette (tortilla) cut into wedges, golden brown outside, showing layers of sliced potato and onion inside` |
| yam-khai-dao | ヤムカイダオ | `Thai fried egg salad: crispy-edged fried eggs cut into pieces, tossed with sliced red onion, halved cherry tomatoes and fresh cilantro, glossy fish sauce and lime dressing with red chili rings` |
| sugomori-tamago | キャベツの巣ごもり卵 | `Baked egg with a glossy soft yolk nestled in a nest of shredded cabbage and diced bacon in a small round baking dish, sprinkled with grated parmesan and black pepper` |
| avocado-egg | アボカドとうずら卵のチーズ焼き | `Two avocado halves baked with a quail egg in each pit hollow, surrounded by melted golden cheese, drizzled with a little soy sauce and black pepper` |
| pitan-tofu | ピータン豆腐 | `A block of silken tofu topped with chopped dark amber century egg (pidan) and minced green onion, dressed with black vinegar soy sauce and chili oil, garnished with cilantro` |
| natto-takuan | 納豆とたくあんののり巻き | `A small bowl of minced natto mixed with diced yellow takuan pickles and green onion, served with squares of nori seaweed and green shiso leaves for hand-wrapping` |
| range-yudofu | レンジ湯豆腐のしょうがあん | `Warm silken tofu pieces in a small bowl covered with translucent glossy ginger dashi sauce, topped with grated ginger and sliced green onion, gentle steam` |
| atsuage-oyster | 厚揚げのオイスターしょうが煮 | `Bite-size cubes of thick fried tofu (atsuage) simmered in glossy dark oyster sauce glaze, topped with sliced green onion, a little sauce pooled on the plate` |
| koya-karaage | 高野豆腐の唐揚げ風 | `Crispy golden fried koya-dofu (freeze-dried tofu) pieces like karaage fried chicken, piled up with a lemon wedge on the side` |
| tofu-mochi | 豆腐もちの甘辛焼き | `Small round chewy tofu mochi patties pan-fried golden, coated in glossy sweet soy glaze, each wrapped with a strip of nori seaweed` |
| daizu-curry | 蒸し大豆のカレー塩焼き | `Roasted soybeans with a crisp golden surface, dusted with yellow curry powder and salt, piled in a small dish` |
| corn-cheese | コーンチーズ | `Korean corn cheese: sweet corn kernels baked with mayonnaise under a layer of bubbling melted cheese with browned spots, in a small shallow cast-iron skillet, sprinkled with parsley` |
| range-fondue | レンジでチーズフォンデュ | `A small ceramic bowl of smooth molten cheese fondue with black pepper, surrounded by bite-size baguette cubes, broccoli florets and cherry tomatoes on skewers` |
| cheese-isobe | チーズの磯辺焼き | `Sticks of processed cheese wrapped in crisp nori seaweed, pan-seared with the cheese edges slightly melted and golden, glazed with soy sauce` |
| gorgonzola-honey | ゴルゴンゾーラのはちみつくるみ | `Crackers topped with crumbled blue gorgonzola cheese and chopped walnuts, drizzled with golden honey and cracked black pepper` |
| creamcheese-gochujang | クリームチーズのコチュジャン和え | `Cubes of white cream cheese coated in glossy red gochujang sauce, sprinkled with white sesame seeds, with sheets of Korean seaweed on the side` |
| mozzarella-panko | モッツァレラとトマトのパン粉焼き | `Torn mozzarella and halved cherry tomatoes baked in a small gratin dish under golden crispy breadcrumbs and parmesan, flecked with dried basil, olive oil glistening` |
