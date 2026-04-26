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

`server-dir` path-ը `.github/workflows/cicd.yml` ֆայլում ա, եթि cPanel-ում path-ը փոխեիր — ասա, թարմացնենք։

