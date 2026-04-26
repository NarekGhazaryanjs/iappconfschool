# iappconfschool (OPTICS-15 / ASRP-BRIA 2026)

Ստատիկ կայք (HTML/CSS/JS)։

## Ինչպես live-ը միշտ repo-ի հետ նույնը լինի

1. **Մի անգամ GitHub-ում** (repo → **Settings → Secrets and variables → Actions**) լրացրու․

| Secret | Ո՞րն է |
|--------|--------|
| `FTP_SERVER` | FTP host (օր. `server2.reg.am`) |
| `FTP_USERNAME` | cPanel FTP user (օր. `iappamfk`) |
| `FTP_PASSWORD` | FTP password |
| `FTP_TARGET_DIR` | **Էյ** path-ը, որ cPanel-ում ցուցադրվում է այն **ֆոլդերի** համար, որն ասում է `https://opticssymposia.iapp.am/` (օր. **`opticssymposia.iapp.am/`**), **վերջնով `/`** |

2. **Երբ `FTP_TARGET_DIR`-ը սխալ ա** (օր. այլ folder, առանց `.iapp.am`), GitHub-ից ֆայլերը **ուժի folder** են գնում — կայքը **քո URL-ում** չի փոխվում, թեև push-ը կանաչ է։

3. **Workflow**․ `main` branch-ին **push** → **CI** → **FTP deploy**․ Ստուգի [Actions](https://github.com/NarekGhazaryanjs/iappconfschool/actions) — **CD** job-ը կանաչ է, եթի path-ը ճիշտ ա։

4. **Ձեռքով zip** (եթի հանկարծ FTP չես ուզում)․ `.\scripts\zip-site.ps1` → upload cPanel **File Manager** → `opticssymposia.iapp.am` document root։
