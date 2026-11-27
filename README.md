# SyncMagazine の画像を更新する

1. [固定の画像更新ページ](https://github.com/Sinamoon/magsync-pages-test/releases/edit/SyncMagazine)を開きます。
2. 表紙から順に `1.png`、`2.png`、`3.png`、`4.png` を添付します。同じ名前の古い画像は先に添付欄から外します。JPGやWebPも使えます。4枚を確認して保存します。
3. [公開画面](https://github.com/Sinamoon/magsync-pages-test/actions/workflows/publish-magazine.yml)で **Run workflow** を押し、`main` のままもう一度 **Run workflow** を押します。
4. 緑のチェックが付いたら、誌面の **Reload images** を押します。

画像は1枚20 MBまでです。推奨サイズは横512 × 縦768ピクセルです。縦横比が異なる画像は中央で切り抜かれます。更新にはリポジトリの書き込み権限が必要です。
