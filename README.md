# iappconfschool (OPTICS-15 / ASRP-BRIA 2026)

Ստատիկ կայք — GitHub Actions․ `main` **push** կամ **Run workflow**․ **CI** + **FTP deploy** cPanel-ի **վեբ արմատի թղթապանակ** (օր. `opticssymposia.am/`, `public_html/sub/…/`)․ `FTP_TARGET_DIR` **պետք է ճիշտ լինի** (տես ներքև)։

## Ենթադոմեն (subdomain) — սկիզբից + deploy

Թիրախը, օր. **`confschool.iapp.am`** (անունն ընտրում ես դու)․ iapp-ի cPanel, primary domain-ը `iapp.am` ա, shared IP, օր. **49.12.164.154**․

### 1) cPanel-ում ավելացրու նոր ենթադոմեն

1. **cPanel** → **Domains** (Դոմեններ) / կամ **Subdomains** (եթի առանձ menu ա)։
2. **Create A New Domain** / **Create a subdomain** — ըստ host-ի նոր UI-ի։
3. **Subdomain** դաշտ` օր. `confschool` (առանձ `iapp.am` մի ավել արա, նախատեսի dropdown-ոց)։
4. **Դոմեն**` ընտրի **`iapp.am`**։
5. Եթի ա` **«Share document root with main domain»** / նման checkbox — **անջատիր** (ուզում ենք **առանձ** կորեան, ո թե` մի աս `public_html`)։
   - Document root-ը հաճախ` `public_html/sub/confschool` կամ `confschool.iapp.am` (նույն path-ն հաստատի **քայլ 2**-ում)։
6. **Պատրաստ է / Submit**։

### 2) Ու՞ր կորեան, որ **FTP-ն ճիշտ տեղ հանի** (`FTP_TARGET_DIR`)

1. **cPanel** → **Domains** → գտի **`confschool.iapp.am` տող** → **Manage** / *Կարողավիճակ*․
2. Դիտարակիր **Կորեն** դաշտը, օր. **`/confschool.iapp.am`** կամ **`/public_html/sub/confschool`** (կախված host-ից)․
3. **File Manager**-ում բացրու **համապատասխան** թղթապանակը — deploy-ը պետք է `index.html`-ը **այս արմատում** ձգի։
4. `FTP_TARGET_DIR` secret-ը = `home/USERNAME/...`-ից **FTP chroot-ին relative** (հաճախ `confschool.iapp.am/` կամ `public_html/sub/.../`), **վերջնով` `/`**, **նույն արժեքը, ինչ cPanel-ի Domains-ում ցուցադրվում է** որպես կորեան, առանձ` `/home/USERNAME/`-ի։

### 3) GitHub Secrets (ռեպոզիտորի)

**Settings** → **Secrets and variables** → **Actions**․

| Secret | |
|--------|--|
| `FTP_SERVER` | host, օր. `server2.reg.am` |
| `FTP_USERNAME` | cPanel FTP user, օր. `iappamfk` |
| `FTP_PASSWORD` | FTP ծածկագիր |
| `FTP_TARGET_DIR` | cPanel-ում **վեբ արմատի** թղթապանակ, FTP-ի `home/USERNAME/`-ից relative, **վերջնով** `/`․ Օր. `confschool.iapp.am/` կամ `public_html/sub/confschool/` (նույնը, ինչ **քայլ 2**-ի կորեն)։ |

Ստուգում․ cPanel-ի **File Manager**-ի ճանապարհ` եթէ ասում ա `…/confschool.iapp.am`, `FTP_TARGET_DIR` մեծ մասամբ կլինի `confschool.iapp.am/` (առանձ `home/USERNAME/`)․

### 4) Դեպլոյ

```bash
git add -A && git commit -m "deploy" && git push origin main
```

[Actions](https://github.com/NarekGhazaryanjs/iappconfschool/actions)․ **CI**-ից հետո **CD (FTP)** կանաչ ա, եթի path/secret-ները ճիշտ են։  

### 5) SSL

**SSL/TLS Status**-ում ավտոմատ **AutoSSL**-ը `*.iapp.am` ենթադոմենների վրա հաճախ աշխատում ա, եթէ `iapp.am` արդի՞ ցուց ա` hosting-ի IP-ի վրա։ cPanel **Domains**-ում **HTTPS** redirect, երբ սերտիֆիկատը **Valid** ա (կարմիր / self-signed — նախ **Run AutoSSL**)։

### 6) `confschool.iapp.am` vs `opticssymposia.am` առանձ

- **Ենթադոմեն `something.iapp.am`**. cPanel-ը հաճախ **DNS գրառում ավտոմատ** ավելացնում ա, primary `iapp.am` արմուտ աշխատի — սա սովորաբար ավելի **արագ** ա, քան առանձ **`.am`** դոմեն reg.am-ի A record-երով․
- **Առանձ** `opticssymposia.am` դոմեն` reg.am-ում A record + cPanel-ում addon, տես **ստորև` «`DNS_PROBE_FINISHED_NXDOMAIN`»** բաժինը։

## Քո մոտ աշխատանք (ամեն օր)

```bash
cd C:\Users\ADMIN\Desktop\iappconfschool
# … փոփոխում ես ֆայլերը …
git add -A
git commit -m "համառոտ նկարագիր"
git push origin main
```

`push`-ից հետո․ [Actions](https://github.com/NarekGhazaryanjs/iappconfschool/actions) — **CI + CD (FTP sync)**։

## Մեկ անգամյա (եթի դեղ չի արվել)

GitHub → **Settings → Secrets and variables → Actions**․

| Secret | |
|--------|--|
| `FTP_SERVER` | FTP host (օր. `server2.reg.am`) — **անունը ճիշտ այսպես** |
| `FTP_USERNAME` | FTP user |
| `FTP_PASSWORD` | FTP password |
| `FTP_TARGET_DIR` | cPanel-ի արմատը FTP login-ից, օր. **`opticssymposia.am/`** (վերջնով `/`) |

`server-dir` path-ը `.github/workflows/cicd.yml` ֆայլում ա, եթի cPanel-ում path-ը փոխեիր — ասա, թարմացնենք։

## Եթի բրաուզերում `DNS_PROBE_FINISHED_NXDOMAIN`

Սա **DNS** ա, ոչ GitHub-ի ու ոչ FTP-ի bug․ դոմենը **համացանցում IP չի ստանում**։

1. **reg.am** (կամ ուր գրանցված ա `opticssymposia.am`) — մտիր **կառավարման / DNS**։
2. **`A` record** `opticssymposia.am`-ի (և `www`-ի, եթի պետք ա) համար դիր **նույն IP-ն**, ինչ cPanel-ի account-ին ա տրված․ cPanel աջ կողմում սովորաբար **Shared IP** / **Server Information** ա։
3. **Nameserver-ները** reg.am-ի հավասար պահի, եթի DNS-ը reg.am-ում ես խմբագրում — կամ NS-ները host-ի տվածը կիրառի։
4. Սպասի **նվազագույն 15ր–24ժ** propagation, հետո փորձիր `https://opticssymposia.am`։

**Ստուգում.** [dnschecker.org](https://dnschecker.org) — գրիր `opticssymposia.am`, տես՝ **A record** արդի՞ն ա։ Երբ աշխատի, նոր **SSL** (Let’s Encrypt / AutoSSL) cPanel-ից։

## cPanel File Manager

Deploy-ից հետո `opticssymposia.am` արմատում պետք է լինի **`index.html`**, `css/`, `js/`։ Եթի չկան — GitHub **Actions**-ում CD job-ի log-ը նայիր (FTP error)։

