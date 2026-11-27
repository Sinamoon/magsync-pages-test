# 雑誌の画像を更新する

最初にリポジトリ管理者から届く招待を承認し、GitHubにログインします。

1. [画像を登録する画面](https://github.com/Sinamoon/magsync-pages-test/releases/new?target=main) を開きます。
2. **Choose a tag** に、前回と違う名前を入力し、**Create new tag** を選びます。例は `mag-20261127-1` です。先頭は毎回 `mag-` にします。**Release title** にも同じ名前を入力します。
3. 下の添付欄で画像を選びます。普通の画像なら、表紙から順にファイル名を `1`、`2`、`3`、`4` にして4枚を添付します（例は `1.jpg`、`2.png`、`3.jpg`、`4.webp`）。すでに4ページをまとめた画像がある場合は、1024 × 1536ピクセルの `atlas.png` 1枚で更新できます。
4. 添付が終わったら **Publish release** を押します。[公開状況](https://github.com/Sinamoon/magsync-pages-test/actions/workflows/publish-magazine.yml) の一番上が緑のチェックになったら、雑誌の **Reload images** を押します。

4枚の画像は縦横比2:3に中央で切り抜かれます。画像は1枚20 MBまでです。公開される画像を添付してください。

公開処理に失敗した場合は、Actionsの該当実行に原因が表示されます。添付を直した場合は、新しいタグ名で公開し直してください。

## 管理者の初回設定

- リポジトリの **Settings → Pages → Build and deployment → Source** で **GitHub Actions** を選択します。
- **Settings → Environments → github-pages → Deployment branches and tags** を **Selected branches and tags** にし、Branch に `main`、Tag に `mag-*` を許可します。
- **Actions → Publish magazine images → Run workflow** で、既存の `atlas.png` が新しい配信方法でも公開できることを確認します。この手動実行はリポジトリの初期画像を公開するため、通常の画像更新には使いません。
- **Settings → Collaborators** でフレンドのGitHubアカウントを招待します。
