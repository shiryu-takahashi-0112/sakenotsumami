// サケノツマミの recipes.js を読み、JSON で標準出力に出す（元ファイルは読むだけ）。
//   node lib/load_recipe.mjs <recipe_id>   … 1品
//   node lib/load_recipe.mjs --all         … 全レシピ
//   node lib/load_recipe.mjs --list        … id の一覧
// 大きな出力を process.exit で終えるとパイプ先で途中で切れるので、exit は使わず exitCode で終える。
import fs from "node:fs";
import vm from "node:vm";
import { fileURLToPath } from "node:url";
// 既定はこのリポジトリの recipes.js（このファイルは <リポジトリ>/tools/reels/lib/）
const SRC = process.env.SAKE_RECIPES || fileURLToPath(new URL("../../../recipes.js", import.meta.url));
const ctx = {};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(SRC, "utf8") + "\n;this.__R={DRINKS,TOOLS,RECIPES};", ctx);
const { DRINKS, TOOLS, RECIPES } = ctx.__R;
const arg = process.argv[2];
if (arg === "--all") {
  process.stdout.write(JSON.stringify({ recipes: RECIPES, drinks: DRINKS, tools: TOOLS, count: RECIPES.length }) + "\n");
} else if (arg === "--list") {
  process.stdout.write(RECIPES.map(r => r.id).join("\n") + "\n");
} else {
  const recipe = RECIPES.find(r => r.id === arg);
  if (!recipe) {
    console.error(`レシピが見つかりません: ${arg}`);
    process.exitCode = 2;
  } else {
    process.stdout.write(JSON.stringify({ recipe, drinks: DRINKS, tools: TOOLS, count: RECIPES.length }) + "\n");
  }
}
