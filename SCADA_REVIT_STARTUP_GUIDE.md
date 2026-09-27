# SCADA / Cable Tray 專用 Revit 起手式指南

> 適用對象：接觸 Autodesk Revit（MEP／SCADA／弱電）的工程人員，包含第一次操作 Revit 的人員。
> 適用版本：Autodesk Revit 2027（介面路徑以此版本為準；若無法確認與該版本完全一致，會在該處標註「需於 Revit 2027 實機確認」）。
> 本文件目的：在**正式開始畫 Cable Tray／Conduit／SCADA 設備之前**，先把模型、座標、視圖、命名這些基礎設定做對，避免後面重畫、對不齊、看不到、算不準。

> **權限前提**：本文件假設使用者在**公司電腦、僅一般使用者權限（無系統管理員權限）**的條件下操作。全文所有「必做」「建議」流程，皆只使用 Revit 原生功能，**不需要 UAC 提權、不需要安裝任何軟體、不需要修改系統設定**即可完成。詳見「六、公司電腦權限限制（硬性規則）」。

---

## 使用方式

- 第一次接觸專案：從「0. 開始前先判斷」讀起，照 Step 1 → Step 15 順序做一次。
- 已經熟悉流程、只是要開新專案：直接看「二、SCADA Revit 起手 10 步（快速版）」。
- 正要開始畫圖前最後檢查：看「三、正式畫 Tray 前 Checklist」。
- 東西畫一畫出問題：跳到「四、最常發生的問題」對照排查。
- 每一步標示：
  - **【必做】**：不做會直接出錯或後面要重工。
  - **【建議】**：不做也能繼續，但長期會比較亂或比較慢。
  - **【視公司流程而定】**：依各公司 BIM 標準或既有專案規則決定，沒有標準答案。

---

## 0. 開始前先判斷：這是新建專案，還是接手專案？

不要一開啟 Revit 就開始畫 Tray。先確認自己是「從零開始」還是「接別人的模型」，兩種要檢查的東西不一樣。

### A. 新建 SCADA / MEP 專案 【必做：判斷屬於哪一種】

開新檔前先確認：

| 檢查項目 | 說明 |
|---|---|
| 使用哪個 Template | 公司是否有指定的 MEP／電氣樣板檔（.rte）？沒有的話用 Revit 內建 `Electrical-Default` 或 `Systems-Default`（實際樣板名稱依安裝內容而定，**需於 Revit 2027 實機確認**）。|
| 是否有公司標準樣板 | 若有，優先使用，裡面通常已含公司的 Cable Tray Type、View Template、命名規則。|
| 是否有既有 MEP 專案可複製標準 | 沒有公司樣板時，找同類型已完成專案，複製其 Cable Tray Type、Filter、View Template 過來，不要每案重做一次。|
| 是否需要 Worksharing | 只有自己一人建模，暫不需要；多人協作再參考 Step 15。|

### B. 接手既有 Revit 專案 【必做：逐項檢查，不要先畫圖】

接手案子，**先檢查、後動筆**。至少過一遍：

- [ ] Link 模型（建築／結構／機電，有哪些、是否為最新版）
- [ ] Level（樓層標高是否與圖面／建築模型一致）
- [ ] Grid（軸網是否完整、命名是否清楚）
- [ ] Shared Coordinates（模型間是否對齊，見 Step 3）
- [ ] View Template（既有專案是否已有，命名規則為何）
- [ ] View Filters（既有 Filter 邏輯是什麼，會不會跟自己新增的衝突）
- [ ] Cable Tray Type（既有 Tray 種類、命名規則、Fitting 設定）
- [ ] Existing / New Phase（Phase 設定，新增的東西要歸在哪個階段）
- [ ] Worksets（是否已啟用 Worksharing，自己會被分配到哪個 Workset）
- [ ] Browser Organization（Project Browser 的視圖分類邏輯）
- [ ] Existing Schedule（既有明細表統計的是什麼、欄位邏輯）

> 只要上面任何一項「看起來怪怪的」（例如模型對不齊、標高對不上），先跟專案負責人確認，**不要自己猜著先畫**。畫完才發現座標錯，等於全部要搬移重接。

---

## 一、標準起手式主流程

### Step 1：確認 Project Units【必做】

**目的**：Cable Tray／Conduit 的寬度、高度、標高、偏移量、彎曲半徑全部依賴單位設定，單位錯，所有尺寸都可能錯或看起來不合理。

**Revit 操作位置**：
```
Manage → Settings → Project Units
```
快捷鍵：`UN`

**實際設定方式**：
- Length（長度）= Millimeters
- Area（面積）= Square Meters
- Angle（角度）= Decimal Degrees

**SCADA 專案注意事項**：
Cable Tray 的 Width、Height、Elevation、Offset、Bend Radius，以及 Conduit Size，這些數值輸入時都直接讀這裡的單位設定，單位不對，輸入 300 可能被當成 300 英呎而不是 300 mm。

**常見錯誤**：
- 用到英制樣板（Imperial Template），單位預設是 Feet and Inches，沒發現就直接畫。
- 只改了 Length，沒注意 Angle 單位（部分公司樣板用 Radians）。

**完成驗收條件**：
建立一段測試用的 300 mm 寬 Cable Tray，選取後在 Properties 面板確認 Width 顯示為 300，畫面量測結果與數字相符。

---

### Step 2：檢查或 Link 建築／結構／機電模型【必做】

**目的**：SCADA Cable Tray 不應該憑空畫在空白畫面，必須以建築、結構（有時含機電）模型為背景，才能判斷路由、避開梁柱、抓對高程。

**Revit 操作位置**：
```
Insert → Link → Link Revit
```
若對方只給 CAD 圖：
```
Insert → Link → Link CAD
```

**實際設定方式**：
1. 選擇正確檔案（確認是最新版，不是舊版）。
2. Positioning 選項建議使用 `Auto - By Shared Coordinates`（前提是對方模型已有設定 Shared Coordinates，否則見 Step 3）。
3. Link 完成後用 `Insert → Manage Links` 確認清單裡的模型狀態是 Loaded，不是 Not Found 或 Unloaded。

**SCADA 專案注意事項**：
- 優先用 **Link**，不要用 Import。
- 不要把所有來源檔案（建築、結構、機電）全部直接匯入塞進同一個模型檔，這樣會讓檔案肥大、無法個別更新、也無法用 Reload 抓對方最新版。
- 不要自己重畫建築模型，除非真的完全沒有來源檔可用。

**Link Revit ／ Link CAD ／ Import CAD 的差異**：三者都是「把外部檔案放進目前模型」，差別在於是否保持獨立、能否更新。CAD 圖也應該優先 **Link CAD**，不是只能 Import——Import 只在真的需要把 CAD 幾何變成本檔物件（例如要在其上描圖建模）時才用。

| | Link Revit | Link CAD | Import CAD |
|---|---|---|---|
| 來源檔案類型 | .rvt | .dwg／.dxf 等 | .dwg／.dxf 等 |
| 檔案關係 | 保持獨立檔案，隨時可 Reload 更新 | 保持獨立檔案，隨時可 Reload 更新 | 幾何被吃進目前檔案，變成本檔物件 |
| 更新方式 | Manage Links → Reload | Manage Links → Reload | 需要重新 Import 或手動更新 |
| 檔案大小影響 | 較小（只是參照） | 較小（只是參照） | 會直接增加本檔大小 |
| 適用情境 | 建築／結構／機電背景模型 | 只有 CAD 圖、沒有 Revit 模型時的**優先**做法 | CAD 圖需要被當成本檔物件處理時的暫時作法（少用） |

**Reload / Manage Links 用途**：對方模型改版後，透過 `Insert → Manage Links` 選取該連結按 `Reload`，就能抓到最新版本，不用重新 Link。

**為什麼 SCADA 工作要以建築與結構模型作背景**：Cable Tray 路由要避開梁、柱、樓板開口、牆體，也要抓對樓層 FFL（結構完成面標高），沒有背景模型等於盲畫。

**常見錯誤**：
- Link 進來的模型 Positioning 選錯，導致座標對不上（見 Step 3）。
- Import CAD 後忘記放在獨立 Workset／Category，後面難以單獨關閉。

**完成驗收條件**：`Manage Links` 視窗中所有連結狀態皆為 Loaded，且在平面圖能看到建築牆柱與結構梁柱正常顯示。

---

### Step 3：確認 Shared Coordinates / Position【必做】

**目的**：在畫任何 Tray 之前，先確認 Link 進來的模型「真的對齊」，不是看起來對、實際上偏移或轉了角度。

**檢查方式（至少檢查這幾個樓層）**：
- 1F
- 典型樓層（Typical Floor）
- 屋頂層
- 地下層（若有）

**觀察重點**：這幾個位置在各 Link 模型之間是否對得上——
- 建築柱位
- 電梯
- 樓梯
- 機房
- 豎井（管道間）
- 外牆線

**若發現對不上**：**先停下來，不要開始畫 Tray**。座標問題必須先解決，畫完再搬移等於重工，而且容易漏掉沒搬到的物件。

**名詞簡單說明（不用背學術定義，知道何時會出問題即可）**：
- **Internal Origin（內部原點）**：Revit 檔案自己內部的座標原點，使用者通常看不到、也不用管。
- **Project Base Point（專案基準點，PBP）**：這個專案自己認定的「0,0,0」，通常對應建築的某個角落或基準線交點。
- **Survey Point（測量點）**：對應到真實世界的測量座標（例如 TWD97 座標），跟基地測量圖對接時會用到。
- **Shared Coordinates（共用座標）**：多個 Revit 檔案之間，用來讓彼此對齊的共用座標系統。當建築、結構、機電模型分別建立時，只要它們有「發佈」與「接收」過 Shared Coordinates，Link 進來時選 `Auto - By Shared Coordinates` 就會自動對齊。

**什麼時候會出問題**：
- 建築模型和結構模型是不同單位各自建的，從未做過 Shared Coordinates 發佈／接收。
- Link 時 Positioning 選成 `Auto - Origin to Origin` 或 `Center to Center`，而不是共用座標，導致對齊依賴巧合。
- 對方模型中途搬動過 Project Base Point，但沒有重新發佈座標。

**常見錯誤**：
- 只看 3D 視圖覺得「看起來有對到」就開始畫，沒有實際疊合柱網、電梯位置核對。
- 忽略地下層或屋頂層，這兩層最常出現對不齊卻沒人發現。

**完成驗收條件**：至少 3 個樓層（1F、典型層、屋頂或地下層其中一層）的柱網、電梯、樓梯、豎井位置與其他 Link 模型疊合誤差在可接受範圍內（實際容許誤差依公司 BIM 標準，**視公司流程而定**）。

---

### Step 4：確認 Level 與 Grid【必做】

**目的**：Cable Tray 的高程完全依賴 Level + Offset／Elevation，Level 錯，整條 Tray 的樓層歸屬與高度就錯。

**重要觀念**：
- 如果建築模型已經有完整標高與軸網，**不要預設 SCADA 模型一定要自己重新畫一套 Level／Grid**。
- Link 進來的模型裡的 Level，**不等於**自己模型裡的 Level——即使名稱一樣（例如都叫「1F」），也是兩個獨立的元素，各自可被獨立修改。

**Copy/Monitor 的使用時機**：
```
Collaborate → Copy/Monitor → Select Link
```
- 適合用於：**Levels（樓層標高）**、**Grids（軸網）**。
- 用途：把 Link 模型中的 Level／Grid「複製」一份到自己檔案裡，並持續監控原始模型是否有更動（更動會跳警示提醒協調）。
- 什麼時候需要：專案需要**跨團隊協調**、而且會頻繁確認建築模型是否修改標高／軸網時。單純看一下背景模型、不需要自己畫東西在同標高系統上時，不一定需要做 Copy/Monitor（**視公司流程而定**）。

**SCADA Cable Tray 最重要的觀念：Level + Offset／Elevation**

範例：
```
1F FFL（結構完成面標高） = 0
Tray Elevation（設計要求的安裝高度） = 2700 mm
則 Tray 實際所在標高 = 1F + 2700 mm
```

也就是說，畫 Tray 時看的是「所屬 Level」加上「該 Level 往上的 Offset」，不是憑空輸入一個絕對標高。

**常見錯誤**：
- 誤把 Link 模型的 Level 當成自己模型的 Level 來設定 View Range（會抓不到正確樓層）。
- FFL 與結構樓板厚度混淆，導致 Offset 算錯。
- 忘記做 Copy/Monitor，之後建築改標高，自己的模型沒同步更新，沒人發現。

**完成驗收條件**：自己模型中的 Level 名稱、數量、標高數值與建築模型一致（或有清楚對應關係），且能正確說出「目前這條 Tray 是哪個 Level + 多少 Offset」。

---

### Step 5：建立 SCADA Working Views【必做】

**目的**：不要在同一張視圖裡，從草稿測試畫到正式出圖，這樣後面很難管理可見性設定，也容易誤改到出圖用的視圖。

**建議建立的視圖（命名可依公司規則調整，此為建議命名）**：
- `WIP_SCADA_1F`
- `WIP_SCADA_2F`
- `WIP_SCADA_3F`
- `COORD_SCADA_1F`
- `{3D}_SCADA_COORD`

**三類視圖用途說明**：

| 類型 | 用途 |
|---|---|
| WIP（Work In Progress） | 日常配管路由、測試 Fitting、自己畫圖用的工作視圖，可以隨意開關圖層、隨意測試。|
| COORD（Coordination） | 跨系統協調用，通常會疊合結構、機電、消防等專業一起檢查碰撞。|
| SHEET | 正式出圖使用，畫面內容、比例、圖框都要固定，不應該拿來做日常測試。|

**操作方式**：
```
複製既有平面視圖 → 右鍵 Duplicate View → Duplicate（不要用 Duplicate with Detailing，除非需要保留註解）→ 重新命名
```

**原則**：不要一張 View 從頭做到尾（從草稿、協調、一路用到出圖），混用會導致正式出圖視圖被意外改動可見性設定。

**常見錯誤**：命名沒有規則、之後 Project Browser 一片視圖分不出哪張是做什麼用的（見 Step 14）。

**完成驗收條件**：至少建立一組 WIP、一組 COORD、一組 3D 協調視圖，且命名清楚可辨識用途。

---

### Step 6：設定 View Range【必做】

**目的**：Cable Tray 最常見的狀況就是「有畫，但平面看不到」，九成原因是 View Range 沒設對，不是模型壞掉。

**Revit 操作位置**：
```
在平面視圖點選空白處 → Properties 面板 → View Range → Edit…
```

**View Range 四個關鍵值**：
- **Top**：視圖範圍的最高裁切面。
- **Cut Plane**：視圖的水平切割面，高於此面的物件通常不顯示（除非設定為可見於 Top 以下）。
- **Bottom**：視圖範圍的最低裁切面。
- **View Depth**：低於 Bottom 但仍可看見（通常以較淡線型顯示）的延伸深度。

**用實際案例說明，而不是只背名詞**：

假設：
```
FFL（樓板面）        = 0
Cable Tray Elevation = +2700 mm
Cut Plane            = +1200 mm
Top                  = +3000 mm
```

Tray 在 +2700 mm，落在 View Range 的垂直範圍之外（超出 Cut Plane +1200 mm）。**若 Tray 在視圖的垂直範圍外，先檢查 Top／Cut Plane／Bottom 這三個值有沒有涵蓋到 Tray 的 Elevation**，這是排查的第一步，不是絕對規則——Cable Tray 實際的 projection/cut 顯示行為，還牽涉 Category 本身的顯示設定、View Discipline 等因素，不同類別的判斷邏輯不完全相同，**具體顯示結果需於 Revit 2027 實機確認**，這裡不當成放諸所有類別皆準的通則。

**排查順序建議**：Cable Tray 平面看不到時，**先檢查 View Range，再懷疑模型是不是沒建好**。

**常見錯誤**：
- Cut Plane 用預設值（通常抓到約 1200 mm），沒有依照 SCADA Tray 實際安裝高度（常見於天花板上方 2400～3000 mm）調整。
- Top 設定太低，把整條 Tray 都排除在範圍外。

**完成驗收條件**：把測試用 Tray 的 Elevation 記下來，設定 View Range 的 Top 明確高於該 Elevation，平面視圖能正常看到該 Tray。

---

### Step 7：建立 SCADA View Template【建議】

**目的**：把「這張視圖該顯示什麼、不該顯示什麼」固定下來，之後套用到多張視圖，不用每張重設一次，也避免各視圖標準不一致。

**Revit 操作位置**：
```
View → Graphics → View Templates → Create Template from Current View…
```
或
```
View → Graphics → View Templates → Manage View Templates…
```

**建議建立**：
- `VT_SCADA_ROUTING`：日常路由工作用。
- `VT_SCADA_COORD`：跨系統協調用。

**至少要控制的項目**：
- Scale（比例）
- Detail Level（詳細程度）
- Discipline（專業別）
- Visibility/Graphics（可見性／圖形）
- Revit Links（連結模型的顯示方式）
- Model Categories（模型類別）
- Annotation Categories（註解類別）
- Filters（見 Step 8）

**建議的 SCADA Routing View 設定方向**：
| 類別 | 建議設定 |
|---|---|
| Architecture（建築） | Halftone（淡化） |
| Structure（結構） | 可見（正常顯示，方便判斷碰撞） |
| Cable Tray | 顯示 |
| Cable Tray Fittings | 顯示 |
| Conduit | 顯示 |
| Electrical Equipment | 顯示 |
| Furniture（家具） | 關閉 |
| Planting（景觀植栽） | 關閉 |

**重要提醒**：**不要把 Temporary Hide/Isolate（暫時隱藏／隔離）當作 View Template 在用。** Temporary Hide/Isolate 只是暫時性的畫面操作（畫面邊框會出現藍色框線提示），關閉視圖或重開後未必保留，也不會被記錄成正式設定，不能取代 View Template 的可見性管理。

**常見錯誤**：用 Temporary Hide/Isolate 把畫面弄乾淨後直接開始出圖或存檔交付，下次打開視圖東西又全部跑出來。

**完成驗收條件**：建立至少一個 View Template 並套用到對應 WIP／COORD 視圖，畫面顯示符合建議設定表。

---

### Step 8：建立 View Filters【建議】

**目的**：用參數自動決定顏色／線型，比每次手動 Override 更適合長期、多人協作的專案。

**Revit 操作位置**：
```
View → Graphics → Filters
```

**建議建立**：
- `FILTER_SCADA_TRAY`
- `FILTER_SCADA_CONDUIT`
- `FILTER_EXISTING`
- `FILTER_NEW`

**過濾依據（若模型已有對應參數）**：
- System（系統別）
- Comments（備註）
- Type（類型）
- Route_ID（路由編號，見 Step 10）
- Discipline（專業別）
- Status（狀態）

**為什麼 Filter 比手動 Override 好**：手動 Override 是針對「選取當下的物件」上色，之後新增的同類物件不會自動套用；Filter 是依規則自動判斷，只要符合條件（例如 System 參數 = "SCADA"），新畫的物件會自動套用設定的顏色／線型，不用每次手動選取上色。

**常見錯誤**：Filter 條件設定的參數，模型裡的物件實際上沒有填寫該參數值，導致 Filter 看起來「沒作用」。

**完成驗收條件**：建立至少一個 Filter 並套用在 View Template 中，改變一個物件的對應參數值後，畫面顏色會自動跟著變化。

---

### Step 9：建立 Cable Tray Types【必做】

**目的**：正式開始大量路由之前，先確認 Tray 的類型設定與各種轉接（Fitting）都能正常產生，避免畫到一半才發現轉彎、分歧處都接不起來。

**Revit 操作位置**：
```
Systems → Cable Tray → 下拉選擇 Type → Edit Type → Duplicate
```

**建議命名規則（範例，依公司規則調整）**：
- `SCADA_LADDER_300x100`
- `SCADA_LADDER_600x100`

**至少要確認的設定**：
- Width（寬度）
- Height（高度）
- Type（Tray 型式，例如 Ladder／Trough／Solid Bottom 等）
- Fitting Type（轉接配件設定，包含 Elbow、Tee、Cross 等使用的族群）
- Bend Radius（彎曲半徑）

**強調：不要只測直線**。正式建模前，至少要逐一測試以下項目，每一項都要實際畫出來看結果，不能只憑設定畫面判斷：

- [ ] Straight（直線段）
- [ ] Elbow（轉彎）
- [ ] Tee（三通）
- [ ] Cross（十字接頭）
- [ ] Reducer（大小頭／變徑）
- [ ] Vertical Rise（垂直上升）
- [ ] Vertical Drop（垂直下降）

**每一項都要檢查**：
- 能不能正常生成（不會報錯或缺件）
- 尺寸是否正確
- 接頭型式是否正確
- 高程是否正確銜接
- Width 是否相容（不同寬度的 Tray 相接時，是否需要 Reducer，系統是否自動判斷）

**常見錯誤**：只用單一寬度測試，換寬度後才發現轉接件抓不到對應的 Fitting 族群，跳出錯誤訊息或直接斷開不連續。

**完成驗收條件**：上述 7 個項目全部實測過至少一次，且都能正常產生、尺寸正確、高程正確銜接。

---

### Step 10：建立 SCADA 專用參數【視公司流程而定】

**目的**：讓 Tray 元件除了幾何資訊外，還能記錄工程資訊，方便篩選、統計、查核、未來銜接自動化流程。

**Revit 操作位置**：
```
Manage → Settings → Project Parameters（專案參數，僅限本專案）
或
Manage → Settings → Shared Parameters（共用參數，可跨專案重複使用，建議優先使用）
```

**若公司流程允許，建議加入的參數**：
- `SCADA_System`
- `Route_ID`
- `From`
- `To`
- `Area`
- `Level`
- `Drawing_No`
- `Status`
- `Remark`

**Project Parameter 與 Shared Parameter 的差異**：兩者都可以出現在 Schedule 中被統計、也都可以用於 Filter——**「能不能被 Schedule 讀到」不是兩者的主要區別**。實際差異在於：
- **Project Parameter**：只存在於目前這個專案檔案裡，無法直接被其他專案重複使用，也無法被某些需要「共享 GUID」的情境使用（例如做成 Tag 標籤、跨檔案的族群共用參數、或未來要做資料交換／匯入匯出對應時）。
- **Shared Parameter**：定義存放在獨立的共用參數文字檔（.txt）中，可以跨專案重複套用同一組參數定義，且擁有固定的 GUID，可用於 Tag、跨檔案資料比對、以及第五節「AutoCAD Router 與 Revit 欄位對應」這類未來銜接情境。

建議：**若這組參數未來可能被其他專案重複使用、或需要跟外部資料（CSV／Router）對應，優先用 Shared Parameter**；只是本專案內部暫時統計用，Project Parameter 也可以。

**權限提醒**：Shared Parameters 需要一個共用參數文字檔（.txt）作為來源檔。這個檔案**存在自己有寫入權限的路徑即可**（例如自己的 Documents、OneDrive，或專案共用資料夾中自己本來就能寫入的位置），不需要系統管理員權限，也不要嘗試存到 `C:\Program Files` 或 Windows 系統目錄。若不確定專案共用資料夾是否有寫入權限，標記【需確認權限】並先詢問專案負責人。

**這些參數不是為了好看，主要用途**：
- Filter（見 Step 8）
- Schedule（見 Step 11）
- QA 查核
- BOQ（數量統計）
- 查詢與篩選
- 後續銜接自動化流程（見「五、AutoCAD Router 與 Revit 欄位對應」）

**常見錯誤**：誤以為 Project Parameter 完全不能出現在 Schedule 裡而堅持全部改用 Shared Parameter，或反過來完全不考慮 Shared Parameter，導致日後要跨專案沿用、或跟外部資料對應時才發現參數無法共用，需要重建。實際上兩者在 Schedule／Filter 中的可用性細節，**需於 Revit 2027 實機確認**。

**完成驗收條件**：至少建立 `Route_ID` 與 `Status` 兩個參數，並能在 Properties 面板中對單一 Tray 元件填寫數值。

---

### Step 11：建立 Cable Tray Schedule【建議】

**目的**：把 Revit 從「畫圖工具」變成「資料模型」，用表格方式統計、查核所有 Tray 資訊。

**Revit 操作位置**：
```
View → Create → Schedules → Schedule/Quantities
→ 選擇 Category：Cable Trays
```

**建議建立**：`SCADA_CABLE_TRAY_SCHEDULE`

**建議欄位**：
- Type
- Width
- Height
- Level
- Length
- Elevation
- Route_ID
- From
- To
- Status

**重要提醒**：**Schedule 統計出的數量，不代表最終 BOQ（數量清單）一定正確**，還要確認：
- 是否有重複建模（同一段被畫兩次）
- Fitting（轉接件）是否有計入長度統計
- 分段方式是否一致（例如同一直線是否被拆成多段而重複計算）
- 單位是否統一
- 長度統計規則（例如是否含轉彎處的長度）

**常見錯誤**：直接把 Schedule 匯出的數字當成最終發包數量，沒有人工複核。

**完成驗收條件**：Schedule 能正確列出目前模型中所有 Cable Tray，欄位資料與模型參數一致。

---

### Step 12：建立 3D Coordination View【必做（多專業協調時）】

**目的**：平面圖無法看出立體碰撞，3D 協調視圖搭配 Section Box 才能有效檢查空間衝突。

**建議建立**：`{3D}_SCADA_COORD`

**只保留重要類別（透過 Visibility/Graphics 關閉不需要的類別）**：
- Architecture
- Structure
- Cable Tray
- Conduit
- Electrical Equipment
- SCADA Equipment

**操作方式**：
```
開啟 3D 視圖 → View → Section Box（勾選）→ 拖曳 Section Box 邊界縮小檢查範圍
```

**主要檢查項目**：
- [ ] 穿梁
- [ ] 穿牆
- [ ] 穿樓板
- [ ] 撞風管
- [ ] 撞消防管線
- [ ] 撞其他 Cable Tray
- [ ] 空間不足（間距太小）
- [ ] 維修空間不足（無法後續維護施工）

**常見錯誤**：3D 視圖類別全部打開沒關閉，畫面雜亂到根本看不出真正的碰撞點。

**完成驗收條件**：能用 Section Box 縮小範圍檢查任一樓層局部區域，且只顯示上述必要類別。

---

### Step 13：建立 QA View【建議】

**目的**：專門用來找問題的視圖，跟正式出圖視圖分開，避免查核用的誇張顯示設定被誤用在出圖上。

**建議建立**：`QA_SCADA`

**建議設定方向**：
- 建築淡化（Halftone）
- 結構突出顯示
- Cable Tray 高對比顏色
- Conduit 高對比顏色
- 設備維持可見

**重要提醒**：**不要用正式出圖視圖做問題檢查**，避免查核時的暫時性顯示設定不小心被留在出圖視圖裡。

**完成驗收條件**：QA_SCADA 視圖存在，且套用與 SHEET 視圖不同的顯示設定（高對比、易於發現問題）。

---

### Step 14：Browser Organization【建議】

**目的**：視圖一多，Project Browser 會變成一長串列表，不整理很難找到要用的視圖。

**Revit 操作位置**：
```
Project Browser 上按右鍵 → Browser Organization… → 建立或編輯規則
```

**整理依據建議**：Discipline（專業別）→ Purpose（用途：WIP／COORD／SHEET／QA）→ Level（樓層）

**範例分類邏輯**：
```
SCADA
  WIP
  COORD
  SHEET
  QA
  3D
```

**常見錯誤**：不整理，幾十張視圖全部混在預設分類中，找視圖比畫圖還花時間。

**完成驗收條件**：Project Browser 中視圖依 Discipline／Purpose 分類清楚可辨。

---

### Step 15：Worksharing / Worksets【視公司流程而定，僅多人協作專案需要】

**目的**：多人同時在同一個模型工作時，避免互相覆蓋對方的修改。

**什麼時候要啟用**：一人建模不需要；兩人以上同時編輯同一份模型才需要。

**Revit 操作位置**：
```
Collaborate → Worksharing（啟用）
Collaborate → Synchronize with Central（同步到中央檔）
Collaborate → Reload Latest（抓取他人最新更新）
```

**關鍵名詞**：
- **Central Model（中央檔）**：存放在共用位置（伺服器／雲端），是所有人同步的對象。
- **Local Model（本機檔）**：每個人自己電腦上的工作複本，實際編輯都在本機檔進行。
- **Synchronize with Central（SWC）**：把本機的修改上傳回中央檔，同時抓取別人已同步的內容。
- **Reload Latest**：只抓取別人的最新內容，不上傳自己的修改。
- **Relinquish（釋放權限）**：釋放自己目前持有、但沒有實際在編輯的元素／Worksets 權限，讓其他人可以編輯。

**重要提醒**：**如果公司已經有既有的 Central Model，不要重新建立一個新的中央檔**，這會讓團隊分裂成兩份不同步的模型。加入既有專案應該是開啟中央檔、建立自己的本機檔（Create New Local）。

**完成驗收條件**：多人協作情境下，能正確完成一次 Synchronize with Central 且未跳出未預期的衝突警告。

---

## 二、SCADA Revit 起手 10 步（快速版）

> 適合列印或放在桌面提醒用，熟悉流程後的懶人版。

1. 開正確模型（確認是不是最新版、對的檔案）
2. 確認 UN（單位）= mm
3. 檢查 Link（建築／結構／機電是否都在、是否最新）
4. 檢查座標（Shared Coordinates 是否對齊）
5. 檢查 Level / Grid（標高、軸網是否正確）
6. 建 WIP View（工作視圖，不要用出圖視圖畫草稿）
7. 設 View Range（Cut Plane／Top／Bottom 要對得上 Tray 高程）
8. 套 View Template / Filter（顯示設定固定下來，不要每次手動調）
9. 測 Cable Tray Fitting（Elbow／Tee／Cross／Reducer／垂直轉接都先測過）
10. 再正式 Routing（前面 9 步都過了，才開始大量畫路由）

---

## 三、正式畫 Tray 前 Checklist

> 開始大量路由之前，逐項勾選確認。

```
□ 單位正確（UN = mm）
□ 建築 Link 正確（最新版、位置正確）
□ 結構 Link 正確（最新版、位置正確）
□ 模型位置正確（Shared Coordinates 已核對至少 3 個樓層）
□ Level 正確（標高與建築模型一致或有清楚對應）
□ View Range 正確（Cut Plane／Top 涵蓋 Tray 實際高程）
□ Cable Tray Type 正確（命名規則、Width/Height 設定完成）
□ Elbow 正常（實測可生成、尺寸正確）
□ Tee 正常（實測可生成、尺寸正確）
□ Cross 正常（實測可生成、尺寸正確）
□ Reducer 正常（實測可生成、尺寸正確）
□ Vertical Transition 正常（垂直上升／下降可正確銜接）
□ View Template 已套用（WIP／COORD 至少一組）
□ QA View 已建立
□ 3D Coordination View 已建立
□ Schedule 可讀取 Tray（欄位資料正確顯示）
□ 正式路由高程已確認（與設計圖或設備需求核對過）
```

---

## 四、最常發生的問題

### 問題 1：Tray 畫了但平面看不到

優先依序檢查：
1. View Range（Step 6，最常見原因）
2. Visibility/Graphics（該 View 是否關閉了 Cable Tray 類別）
3. View Template（是否套用了會隱藏 Tray 的範本）
4. Phase（該物件的 Phase Created 是否在目前視圖的 Phase 篩選之外）
5. Workset（該物件所在 Workset 是否被關閉顯示）
6. Discipline（視圖的 Discipline 設定是否會過濾掉 Electrical/Mechanical 類別）

---

### 問題 2：Tray 接不起來

檢查：
- Width（兩端寬度是否相容，是否需要 Reducer）
- Height（高度是否一致）
- Type（是否為同一 System Type 或至少 Fitting 設定相容）
- Elevation（兩端高程是否真的對齊，看似對齊但數值有微小落差）
- Fitting（該 Cable Tray Type 的 Fitting 設定是否完整，見 Step 9）
- Angle（轉角角度是否在 Fitting 族群支援的範圍內）

---

### 問題 3：Elbow / Tee 不會自動產生

檢查：
- Cable Tray Type 設定中的 Fitting 對應是否正確指定族群
- Routing Preferences／Fitting 設定（依 Revit 2027 介面路徑可能有所調整，**需於 Revit 2027 實機確認**）
- Width compatibility（兩段 Tray 寬度是否相容）
- Geometry angle（角度是否為該 Fitting 族群支援的標準角度，例如只支援 90°／45°）

---

### 問題 4：模型跟建築對不起來

**先停工，不要繼續畫。**

檢查：
- Positioning（Link 時選的對齊方式）
- Shared Coordinates（是否真的有發佈／接收過）
- Project Base Point（是否被誰移動過）
- Survey Point（是否與測量座標對應正確）
- Revit Link positioning method（`Auto - By Shared Coordinates` / `Origin to Origin` / `Center to Center`，目前用的是哪一種）

---

### 問題 5：畫到後面模型超亂

常見原因：
- 沒命名（視圖、Type 名稱都用預設值）
- 沒 View Template（每張視圖顯示設定都不一樣）
- 沒 Filter（顏色都靠手動 Override）
- 沒 Browser Organization（視圖列表一團亂）
- 沒有分流 WIP／COORD／SHEET（同一張視圖從草稿用到出圖）

---

## 五、AutoCAD Router 與 Revit 欄位對應（資料架構建議）

> **重要聲明**：以下是「資料欄位對應的架構建議」，目的是讓 SCADA Cable Tray Router（AutoCAD／CSV 端）與 Revit 模型的資料欄位未來可以互相對應，**不代表目前已完成自動同步功能**，實際銜接需要另外開發匯入／匯出流程。

| AutoCAD / Router 端欄位 | Revit 對應參數（見 Step 10） |
|---|---|
| ROUTE_ID | Route_ID |
| TYPE | Type |
| WIDTH | Width |
| HEIGHT | Height |
| ELEVATION | Elevation |
| FROM | From |
| TO | To |
| LEVEL | Level |
| SYSTEM | SCADA_System |
| STATUS | Status |

**未來可能的銜接路徑（架構示意，非目前已實作功能）**：

```
AutoCAD Router
      ↓
  CSV / Excel
      ↓
    Revit（透過 Shared Parameter 對應欄位匯入）
      ↓
   Schedule
      ↓
     BOQ
```

---

## 六、公司電腦權限限制（硬性規則）

> 適用情境：公司 Windows 電腦，使用者帳號**沒有系統管理員權限**。本節是整份指南的硬性前提——所有「必做」與「建議」流程，都已依此限制設計，不需要提權即可完成。

### 禁止事項

以下操作**一律不列入本文件的必要流程**，包括但不限於：

- 不可要求以「系統管理員身分執行」
- 不可修改 Windows 系統層級設定
- 不可修改 Registry，除非明確確認是目前使用者可寫入的 HKCU 且不需要提權
- 不可修改 `Program Files`
- 不可修改 Windows 系統目錄
- 不可安裝需要管理員權限的 MSI / EXE
- 不可安裝 Windows Service
- 不可安裝系統 Driver
- 不可修改系統 PATH
- 不可修改全機環境變數
- 不可啟用需要 IT 權限的 Windows Feature
- 不可假設使用者能安裝 Revit Add-in
- 不可假設使用者能安裝 Navisworks Manage
- 不可假設使用者能安裝 Dynamo 套件
- 不可假設使用者能安裝 pyRevit
- 不可假設使用者能修改 Revit 安裝目錄
- 不可假設使用者能安裝 Autodesk Desktop Connector、ODA、第三方 BIM 工具或其他外部軟體

### 優先方案順序

所有操作優先依下列順序考慮：

1. Revit 原生功能
2. 使用者層級設定
3. 專案檔內設定
4. View Template
5. View Filter
6. Schedule
7. Project Parameters
8. Shared Parameters（前提是不需系統管理員，見 Step 10 權限提醒）
9. Excel / CSV
10. 純文字設定檔
11. PowerShell / CMD，但僅限不需管理員權限的命令
12. Portable 工具，但必須確認不需要安裝、不需要 UAC、不修改系統
13. Git / Python，僅限目前電腦已經存在且可直接執行，不可假設可以安裝

### 若某功能通常需要額外安裝

若某個進階做法涉及 Revit Add-in、Dynamo Package、pyRevit、Navisworks Manage、外部 clash detection 工具、Python 套件、第三方 Autodesk 外掛、或 Windows 系統工具，**一律標註**：

> 此方案可能需要額外安裝或管理員權限，目前不列為主要方案。

並同時提供一個不需要系統管理員權限的替代方案。範例：

| | 寫法 |
|---|---|
| ❌ 不要只寫 | 「安裝 pyRevit 做批次處理」 |
| ✅ 應改成 | **主要方案**：使用 Revit 原生 Schedule／View Filter／Project Parameters 完成。<br>**進階方案**：pyRevit 可進一步自動化，但可能需要公司 IT 核准，因此不列入目前必要流程。 |

### 執行原則

若某個操作是否需要管理員權限**無法確認**：**不得直接要求執行**。必須標註「**【需確認權限】**」，並優先提供無管理員權限的替代方案，再請使用者自行向 IT 或專案負責人確認。

### 本指南（Step 1～15）權限自查結果

| Step | 是否需要安裝／提權 | 說明 |
|---|---|---|
| 1 Project Units | 否 | Revit 原生選單 |
| 2 Link 模型 | 否 | Revit 原生選單；讀取來源檔僅需該檔案的讀取權限 |
| 3 Shared Coordinates | 否 | Revit 原生功能 |
| 4 Level / Grid、Copy/Monitor | 否 | Revit 原生功能 |
| 5 Working Views | 否 | Revit 原生功能 |
| 6 View Range | 否 | Revit 原生功能 |
| 7 View Template | 否 | Revit 原生功能 |
| 8 View Filters | 否 | Revit 原生功能 |
| 9 Cable Tray Types | 否 | Revit 原生功能 |
| 10 SCADA 參數 | 否 | Shared Parameter 檔存於使用者可寫入路徑即可，見 Step 10 權限提醒 |
| 11 Cable Tray Schedule | 否 | Revit 原生功能 |
| 12 3D Coordination View | 否 | Revit 原生功能（Section Box） |
| 13 QA View | 否 | Revit 原生功能 |
| 14 Browser Organization | 否 | Revit 原生功能 |
| 15 Worksharing | 否（需網路資料夾寫入權限，非系統管理員權限） | Central Model 通常放在公司網路共用資料夾，使用者需要該資料夾的讀寫權限，但不需要本機系統管理員權限；若不確定資料夾權限，標記【需確認權限】並詢問 IT／專案負責人 |

**結論**：Step 1～15 全部可用一般使用者權限完成，**不需要安裝 pyRevit、Dynamo、Navisworks Manage 或任何第三方外掛**。若未來要擴充自動化（例如銜接第五節的 AutoCAD Router 資料流），屬於「進階方案」，需另外標註並取得 IT 核准，不影響本文件的必要流程。

---

## 七、驗收自查（文件維護用）

本文件完成後，應自行核對以下項目是否涵蓋：

- [x] 是否以 SCADA／Cable Tray 為主，而非一般 Revit 教學
- [x] 是否有 View Range 說明（Step 6）
- [x] 是否有 View Template 說明（Step 7）
- [x] 是否有 View Filter 說明（Step 8）
- [x] 是否有 Cable Tray Fitting 測試流程（Step 9）
- [x] 是否有 Schedule 說明（Step 11）
- [x] 是否有 QA View（Step 13）
- [x] 是否有 3D Coordination View（Step 12）
- [x] 是否說明 Copy/Monitor 使用時機（Step 4）
- [x] 是否說明 Worksharing 使用條件（Step 15）
- [x] 是否有正式 Routing 前 Checklist（三、）
- [x] 是否有故障排查（四、）
- [x] 是否有 AutoCAD Router／Revit 欄位對應（五、）
- [x] 是否避免把推測寫成 Autodesk 已確認功能（凡標註「需於 Revit 2027 實機確認」處，皆為此類項目）
- [x] 是否避免把 Temporary Hide/Isolate 當永久 View Template 邏輯（Step 7 已明確提醒）

**公司電腦權限限制專項驗收（六、）**：

- [x] 是否有任何步驟要求 UAC → 否
- [x] 是否有任何步驟要求管理員密碼 → 否
- [x] 是否有任何步驟要求修改 Program Files → 否
- [x] 是否有任何步驟要求安裝第三方軟體 → 否（第三方工具僅列為「進階方案」，明確標註非必要流程）
- [x] 是否有任何步驟要求修改系統 PATH → 否
- [x] 是否有任何步驟假設公司 IT 已開放權限 → 否（Step 15 網路資料夾權限、Step 10 共用參數檔路徑，皆標註需自行確認，未預設已開放）
- [x] 是否所有必要流程都能只靠 Revit 原生功能完成 → 是

---

## 八、仍需 Revit 2027 實機驗證的項目清單

以下項目在文件中已標註，統一列於此處方便逐項驗證：

1. Step 0-A：新建專案時 Revit 2027 內建樣板的實際名稱（`Electrical-Default` 等）。
2. Step 6：View Range 中 Cut Plane 判斷各 Category 顯示與否的細部邏輯（部分類別可能不完全依 Cut Plane 判斷）。
3. Step 10：Project Parameter 與 Shared Parameter 在 Schedule／Filter 中可用性的實際差異。
4. 問題 3：Routing Preferences／Fitting 設定的實際選單路徑（Revit 版本間選單位置曾經調整過）。

在完成上述 4 項實機驗證前，這份文件屬於「可直接照做的操作指南」，但上述 4 個細節建議由實際操作 Revit 2027 的人員補充確認後再視為最終定案。
