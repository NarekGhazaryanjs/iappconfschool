# iappconfschool (OPTICS-15 / ASRP-BRIA 2026)

Ստատիկ կայք (HTML/CSS/JS)։ **`main` push = FTP deploy` — [Actions](https://github.com/NarekGhazaryanjs/iappconfschool/actions)։

## GitHub (մի անգամ)

| | |
|--|--|
| **Secrets** | `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD` |
| **Optional override** (միաժամանակ մի՛ երկուսը) | Secret `FTP_TARGET_DIR` **կամ** Variable `CPANEL_FTP_DIR` |
| **Արժեք** | FTP-ի home-ից **relative** path, օր. **`opticssymposia.iapp.am/`** — **ոչ**՝ `/home/iappamfk/...` (chroot-ի պատճառով) |  

Չլրացնելու դեպքում deploy-ի default-ը **`opticssymposia.iapp.am/`** է։

## Եթի push-ից հետո live-ը չի փոխվում

1. cPanel-ում` բացջ` document root-ը URL-ի համար, համեմատջ` GitHub-ի path-ի հետ։  
2. **Variable**-ով ուղջ` `CPANEL_FTP_DIR`։  
3. `security: loose` + նոր` `state-name` արդա workflow-ն (կերար full sync)։  

**Զիպ` `.\scripts\zip-site.ps1` → File Manager` նույն folder**։
