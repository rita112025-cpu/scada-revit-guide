# SCADA / Cable Tray 專用 Revit 起手式指南

新建或接手 Revit MEP／SCADA 專案後，正式繪製 Cable Tray／Conduit／SCADA 設備之前，該做哪些設定與檢查的實務指南。以台灣工程現場常用說法撰寫，操作路徑明確，初學者可直接照做。

適用版本：Autodesk Revit 2027（若與該版本介面有出入，文件內會標註「需於 Revit 2027 實機確認」，見文件末「仍需 Revit 2027 實機驗證的項目清單」）。

**權限前提**：假設使用者是公司 Windows 電腦、僅一般使用者權限（無系統管理員權限）。全部必要流程只用 Revit 原生功能，不需要 UAC 提權、不需要修改系統設定。本指南的必要流程不依賴 pyRevit、Dynamo 額外套件、Navisworks Manage 或其他第三方工具（這些工具本身仍可能需要安裝與 IT 核准，只是不在本指南的必要流程之內）。詳見指南「六、公司電腦權限限制（硬性規則）」。

## 內容

- [SCADA_REVIT_STARTUP_GUIDE.md](SCADA_REVIT_STARTUP_GUIDE.md) — 完整指南（Markdown 版，適合閱讀、版本控管、複製貼上）。
- [index.html](index.html) — 網頁版（適合現場查閱，含可勾選 Checklist、章節導覽、故障排查快速跳轉），可直接用瀏覽器開啟，或部署到 GitHub Pages。

## 文件架構

0. 開始前先判斷：新建專案或接手專案
1. 標準起手式主流程 Step 1～15（單位、Link 模型、座標、Level/Grid、工作視圖、View Range、View Template、View Filter、Cable Tray Type、SCADA 參數、Schedule、3D 協調視圖、QA 視圖、Browser Organization、Worksharing）
2. SCADA Revit 起手 10 步（快速版）
3. 正式畫 Tray 前 Checklist
4. 最常發生的問題（5 個排查情境）
5. AutoCAD Router 與 Revit 欄位對應（資料架構建議，非已實作的自動同步）
6. 公司電腦權限限制（硬性規則）——全流程免系統管理員權限、免安裝第三方軟體

## 使用網頁版

直接用瀏覽器開啟 `index.html` 即可，不需要伺服器：

```bash
start index.html
```

或部署到 GitHub Pages：Settings → Pages → Source 選 `main` 分支根目錄。

## 維護原則

- 內容以實際操作為主，避免抽象的 BIM 理論。
- 所有步驟區分「必做」「建議」「視公司流程而定」。
- 無法確認與 Revit 2027 實際行為一致的地方，一律標註「需於 Revit 2027 實機確認」，不虛構功能或選單。
