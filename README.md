# iappconfschool (OPTICS-15 / ASRP-BRIA 2026)

Ստատիկ կայք (HTML/CSS/JS)։

## CI/CD (GitHub Actions)

1. **Secrets` միայն երեքը** (repo → **Settings → Secrets and variables → Actions**)

| Secret | |
|--------|--|
| `FTP_SERVER` | host (օր. `server2.reg.am`) |
| `FTP_USERNAME` | cPanel FTP user |
| `FTP_PASSWORD` | FTP password |

2. **Document root-ը** workflow-ի `env.FTP_DEPLOY_DIR` արժեքն ա` **`opticssymposia.iapp.am/`** (նույնը, ինչ` `/home/USER/opticssymposia.iapp.am/`)` secret-ով path չէ ասում։

3. **`main` push** կամ **Actions → Run workflow** → **Deploy iappconfschool to cPanel** → FTP `opticssymposia.iapp.am/`։ [Actions](https://github.com/NarekGhazaryanjs/iappconfschool/actions)

4. Եթէ host-ը **ուրիշ արմատ** ա (ոչ` `opticssymposia.iapp.am/`), `FTP_DEPLOY_DIR` արժեքը փոխի `.github/workflows/cicd.yml` `env` բաժնում` մեկ տող։

5. **Zip ձեռքով` `.\scripts\zip-site.ps1` → File Manager` `opticssymposia.iapp.am`։**

**Նշում` հին `FTP_TARGET_DIR` secret-ը` կարաս ջնջի, workflow-ն այլ չի օգտագործի։
