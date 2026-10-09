// 日本語の文を、単語の途中で改行しないようにする（動画・カルーセルの型で共通に使う）。
// Chrome の word-break:auto-phrase は文節の区切りを選んでくれるが、1文節が1行より長いと文節の途中で切ってしまう。
// そこで区切ってよい位置の間を1つずつ <span class="ph">（white-space:nowrap）で包み、間に <wbr> を入れる。
// 包んだ中では改行しない（「6〜7分」の「〜」の後ろなども含む）。
// 収まらないときは行からはみ出すので、各型の fit() が文字を小さくして収める。
// 区切ってよい位置：「、」「。」などの後ろ／助詞・活用語尾（を・に・で・て・た など）の次に漢字・カタカナ・数字・英字・括弧が来る所。
// 「切り込み」「取り出す」のような送り仮名（り・き など）の後ろでは切らない。「ひと口」も切らない。
(function () {
  const HIRA = /[ぁ-ゟ]/;
  const HEAD = /[一-鿿々゠-ヿー0-9０-９A-Za-zＡ-Ｚａ-ｚ（(「『【]/;
  const TAIL = /[をにでとがはものへやばてた]/;   // この字で終わるひらがなの後ろなら切ってよい
  const NOBREAK = ['ひと口', 'ふた口', 'ひと晩', 'ひと煮', 'ひと混'];
  const PUNCT = /[、。，．！？!?）)」』】]/;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  function breakPoints(text) {
    const cs = [...text], at = [];
    for (let i = 0; i < cs.length - 1; i++) {
      const a = cs[i], b = cs[i + 1];
      if (PUNCT.test(a) && !PUNCT.test(b)) at.push(i + 1);
      else if (HIRA.test(a) && HEAD.test(b) && TAIL.test(a) && !NOBREAK.some(w => text.slice(0, i + 2).endsWith(w))) at.push(i + 1);
      else if (a === ' ' || a === '　') at.push(i + 1);
    }
    return at;
  }
  // 文を HTML にする（区切ってよい位置に <wbr>）
  window.phraseHTML = function (text) {
    const cs = [...String(text)], at = [0, ...breakPoints(text), cs.length];
    const parts = [];
    for (let k = 0; k < at.length - 1; k++) parts.push('<span class="ph">' + esc(cs.slice(at[k], at[k + 1]).join('')) + '</span>');
    return parts.join('<wbr>');
  };
  window.phraseBreaks = breakPoints;
})();
