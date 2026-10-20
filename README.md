# Wenlve Zhou — Academic Homepage

保留现有学术主页设计的 GitHub Pages 版本。修改 JSON 文件并提交到 `main` 后，GitHub Actions 会自动构建、发布，不需要在本地安装依赖或运行命令。

## 第一次部署

1. 在你的 GitHub 账号下创建主页仓库。个人主页仓库名为 `<你的用户名>.github.io`；如果账号为 `Wenlve-Zhou`，仓库名通常为 `Wenlve-Zhou.github.io`。创建前应检查是否已有该仓库，避免覆盖已有主页。
2. 解压后将里面的文件和文件夹提交到仓库根目录的 `main` 分支，包含 `.github/workflows/deploy.yml`。根目录应直接看到 `profile.json`、`build.py` 等文件；上传时保留 `.github` 文件夹。使用 GitHub Free 时，可采用公开仓库部署。
3. 打开仓库 **Settings → Pages → Build and deployment → Source**，选择 **GitHub Actions**。
4. 打开 **Actions → Deploy academic homepage → Run workflow**，启动首次部署。后续提交会自动触发更新。
5. 运行成功后，通过该工作流的 **github-pages / View deployment** 或 **Settings → Pages** 查看实际发布地址。

当前文件已准备好；只有完成 GitHub 授权、创建/选定仓库并成功运行部署后，才能认为迁移已上线。`profile.json` 中的默认地址是按 `Wenlve-Zhou` 用户主页预填的预期地址；在线构建会从 GitHub Pages 设置读取实际地址，兼容项目子路径和自定义域名。

发布后的照片、职业邮箱、简介和论文会随 GitHub Pages 站点公开展示。

## 以后怎么更新

在 GitHub 仓库打开对应文件，点击编辑，保存并提交即可；不需要修改 Python 或手动部署。

| 想修改的内容 | 编辑文件 |
| --- | --- |
| 职称、单位、邮箱、学位、研究方向、研究说明 | `profile.json` |
| 最新动态 / News | `news.json` |
| 论文、作者、发表状态、代码和项目链接、贡献标注 | `publications.json` |
| 照片与论文配图 | `assets/` |
| 颜色、字体、间距和手机排版 | `src/styles.css` |
| 筛选、图片放大、BibTeX 弹窗和复制 | `src/app.js` |

### 个人资料

`profile.json` 的 `role`、`department`、`university`、`email` 等字段会同步更新简介、侧栏、联系信息和经历，不需要到多个位置重复修改。

- `researchStatement`：英文研究说明。
- `interests`：英文研究方向及图标；现有图标为 `eye`、`robot`、`layers`、`box`。
- `extraBiography`：可选的额外英文段落数组，默认空。
- `additionalExperience`：可选的额外经历数组；每项填写 `period`、`role`、`institution`，可选 `url`、`description`。

### News

复制已有条目并替换内容：`date` 使用 `YYYY-MM` 格式，`text` 为英文新闻。可用 `paperId` 指向现有论文的 `id`，并用 `highlight` 指定正文中需要链接到该论文的词组；日期会自动排序。没有关联论文时，可省略 `paperId` 和 `highlight`。

### 论文

复制一条相近的现有记录，再替换实际信息。

- `id` 必须唯一，首位为小写英文字母，其他字符可用小写字母、数字和短横线。
- `category` 使用 `vision` 或 `embodied`；世界模型相关工作还可设置 `"world": true`。
- `venue`、`venueShort`、`year`、`authors` 按实际发表信息填写；预印本设置 `venueShort` 为 `Preprint` 并填写 `arxiv`。
- `paper` 为主论文链接；`preprint`、`project`、`code` 为可选按钮。
- `role` 可填写 `First author` 或 `Co-first author`；`lead: true` 标记项目负责人。
- 图片先上传到 `assets/`，然后在 `image` 中填写 `assets/文件名.webp` 等相对路径，并填写 `imageAlt`。没有图片可将 `image` 设为 `""`，页面会自动生成该论文的文字封面。
- 会议论文填写 `"bibtexType": "inproceedings"`；`pages`、`volume`、`number`、`doi` 等字段可按实际情况补充。

论文自动按年份分组，同一年内遵循 JSON 中的顺序。论文数量、筛选数量、BibTeX、更新日期和站点地图都会在构建时自动生成。

## 本地预览（可选）

使用 Python 3.9 或更高版本，无需安装第三方包：

```bash
python build.py
python -m http.server --directory dist 8000
```

在你自己的浏览器访问 `http://localhost:8000`。`dist/` 是生成结果，不需要提交到仓库；GitHub Actions 会重新生成它。

## 自定义域名和回退

- 域名在仓库 **Settings → Pages → Custom domain** 配置，按 GitHub 官方说明设置 DNS。在线构建的 canonical、分享地址和站点地图会使用 Pages 返回的实际地址。若在本地构建，可更新 `profile.json` 的 `siteUrl`，或使用 `SITE_URL` 环境变量指定地址。
- 回退内容时，可恢复或撤销相应 Git 提交，然后提交到 `main`；自动部署会重新发布该版本。
- 配图来源保存在 `asset-sources.json`。

官方说明：[创建 GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)、[配置发布来源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)、[使用 Actions 发布](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。
