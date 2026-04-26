# iappconfschool (OPTICS-15 / ASRP-BRIA 2026)

Ստատիկ կայք (HTML/CSS/JS)։ **`main` push = FTP deploy` — [Actions](https://github.com/NarekGhazaryanjs/iappconfschool/actions)։

## GitHub (մի անգամ)

| | |
|--|--|
| **Secrets** | `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD` |
| **Variable (ըստ ցանկության)** | `CPANEL_FTP_DIR` — cPanel-ի `File Manager`→ այն `*-ի` path-ը, ուր ասում ա` `opticssymposia.iapp.am` (օր. `opticssymposia.iapp.am/`, կամ եթi host-ը այլ ա` `public_html/…/`, **վերջնով` `/`**) |  

Եթի variable **չ**ես սահմանի, deploy-ն գնում ա **`opticssymposia.iapp.am/`**` workflow-ի default-ով։  

## Եթի push-ից հետո live-ը չի փոխվում

1. cPanel-ում` բացջ` document root-ը URL-ի համար, համեմատջ` GitHub-ի path-ի հետ։  
2. **Variable**-ով ուղջ` `CPANEL_FTP_DIR`։  
3. `security: loose` + նոր` `state-name` արդա workflow-ն (կերար full sync)։  

**Զիպ` `.\scripts\zip-site.ps1` → File Manager` նույն folder**։
