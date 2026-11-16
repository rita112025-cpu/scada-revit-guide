#!/usr/bin/env python3
"""Embed the recording lesson into index.html. Requires: pip install markdown.

Run from any directory: python scripts/embed_recording.py
Edit the Markdown source, then regenerate. Existing site CSS/JS remains in index.html.
"""
from pathlib import Path
import re
import markdown

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '錄音教學/MEP_電氣視圖與族群實作.md'
BEGIN = '<!-- recording-lesson:start -->'
END = '<!-- recording-lesson:end -->'


def render():
    body = markdown.markdown((ROOT / SOURCE).read_text(encoding='utf-8'),
                             extensions=['tables', 'fenced_code', 'sane_lists', 'attr_list'])
    body = re.sub(r'^<h1>.*?</h1>\s*', '', body, count=1)
    body = body.replace('<h3', '<h4').replace('</h3>', '</h4>')
    body = body.replace('<h2', '<h3').replace('</h2>', '</h3>')
    # Markdown lives one directory below the site root; embedded links do not.
    body = body.replace('href="../', 'href="')
    body = re.sub(r'<table>.*?</table>',
                  lambda m: '<div class="table-scroll">' + m[0].replace('<table>', '<table class="compare">', 1) + '</div>',
                  body, flags=re.S)
    return (BEGIN + '\n<section id="recording-mep" class="section">\n'
            '<h2><span class="eyebrow">操作實務</span>MEP 電氣、視圖與族群</h2>\n' + body +
            '\n'
            '</section>\n' + END)


def main():
    index = ROOT / 'index.html'
    html = index.read_text(encoding='utf-8')
    block = render()
    if BEGIN in html:
        html = re.sub(re.escape(BEGIN) + '.*?' + re.escape(END), lambda _: block, html, count=1, flags=re.S)
    else:
        marker = '<section id="video-notes"'
        if marker not in html:
            raise ValueError('Missing teaching notes insertion point')
        html = html.replace(marker, block + '\n\n' + marker, 1)
    nav = '''    <li class="toc-acc">
      <details>
        <summary class="toc-group">MEP 操作實務</summary>
        <ol class="toc-panel">
          <li><a href="#recording-mep" data-keywords="錄音 電氣 插座 配電盤 接點 電壓 迴路 跨樓層 貼上 樣板 包括 族群 擠出 混成 迴轉 掃掠 Navisworks 碰撞">教材總覽與單元目錄</a></li>
          <li><a href="#recording-b" data-keywords="Power 配電系統 電壓定義 L-L L-G 電氣迴路">電壓、配電與迴路</a></li>
          <li><a href="#recording-d" data-keywords="樓層 複製 貼上 宿主 剖面框">跨樓層複製</a></li>
          <li><a href="#recording-e" data-keywords="視圖樣板 Include 包括 指定 一次性套用">視圖樣板兩種套用</a></li>
          <li><a href="#recording-f" data-keywords="座標 材料 顏色 NWC Clash Detective Manage SwitchBack">匯出與碰撞檢查</a></li>
          <li><a href="#recording-g" data-keywords="族群 工作平面 Extrusion Blend Revolve Sweep Swept Blend">族群五種造型</a></li>
          <li><a href="#recording-h" data-keywords="練習 驗收 排查 自我測驗">練習與排查</a></li>
        </ol>
      </details>
    </li>
'''
    if '<summary class="toc-group">MEP 操作實務</summary>' not in html:
        marker = '  </ol>\n  <p id="tocEmpty"'
        if marker not in html:
            raise ValueError('Missing sidebar insertion point')
        html = html.replace(marker, nav + marker, 1)
    card = '''  <a class="path-card" href="#recording-mep">
    <div class="k">操作實務</div>
    <h3>MEP 電氣、視圖與族群</h3>
    <p>插座迴路、跨樓層複製、視圖樣板、匯出碰撞與五種族群造型。附操作步驟、練習與排查表。</p>
    <span class="go">進入錄音教材 →</span>
  </a>
'''
    if '<div class="k">操作實務</div>' not in html:
        marker = '</div>\n</header>'
        if marker not in html:
            raise ValueError('Missing home learning paths insertion point')
        html = html.replace(marker, card + marker, 1)
    if "'recording-mep'" not in html:
        html = html.replace('const MEGA_LESSONS = [', "const MEGA_LESSONS = ['recording-mep',", 1)
    index.write_text(html, encoding='utf-8')
    print('Updated index.html from ' + SOURCE)


if __name__ == '__main__':
    main()
