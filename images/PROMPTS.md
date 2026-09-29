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
