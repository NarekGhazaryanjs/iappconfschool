# iappconfschool (OPTICS-15 / ASRP-BRIA 2026)

Ստատիկ կայք — GitHub-ից **ամեն `push` `main` branch-ի վրա** GitHub Actions-ը FTP-ով sync է անում cPanel. Secret **`FTP_TARGET_DIR`**-ը **պետք ա համընկնի** cPanel → **Domains**-ում ցուցադրված *կորեն* թղթապանակին (օր. **`opticssymposia.am/`**), ոչ թե այլ անուն։

## Քո մոտ աշխատանք (ամեն օր)

```bash
cd C:\Users\ADMIN\Desktop\iappconfschool
# … փոփոխում ես ֆայլերը …
git add -A
git commit -m "համառոտ նկարագիր"
git push origin main
```

`push`-ից հետո․ [Actions](https://github.com/NarekGhazaryanjs/iappconfschool/actions) — **CI** (ստուգում) + **CD** (FTP)։

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

