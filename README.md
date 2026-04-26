# iappconfschool (OPTICS-15 / ASRP-BRIA 2026)

Ստատիկ կայք (HTML/CSS/JS)։

## Վերբեռնում cPanel

1. PowerShell-ով project root-ում․ `.\scripts\zip-site.ps1` — ստեղծում ա `opticssymposia-site.zip` (կայքի ֆայլերը, առանձ `.git` / `.github`)։
2. cPanel **File Manager** → բացիր **`/home/iappamfk/opticssymposia.iapp.am`** (կամ Domains-ում ցուցադրված **նույն** document root)։
3. zip-ը **Extract** արա այնտեղ (կամ ֆայլերը քարշ արա), որ **արմատում** լինի `index.html`, `css/`, `js/`, `downloads/`, `.htaccess`։

Նոր ենթադոմենը ավելացրու **cPanel → Domains**-ում, document root-ը դիր **`opticssymposia.iapp.am`** (կամ ուր հարմար ա), հետ zip-ը այդ ֆոլդերը։

## CI/CD (GitHub Actions)

`push` / `workflow_dispatch` **main** — **CI** (ֆայլերի ստուգում), հետ **FTP** cPanel․

**Settings → Secrets and variables → Actions**

| Secret | |
|--------|--|
| `FTP_SERVER` | host (օր. `server2.reg.am`) |
| `FTP_USERNAME` | cPanel FTP user |
| `FTP_PASSWORD` | FTP password |
| `FTP_TARGET_DIR` | document root FTP-ից, վերջնով `/` — հաճախ **`opticssymposia.iapp.am/`** (նույնը, ինչ cPanel → Domains → Root) |
