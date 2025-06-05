### 現状

- NVIDIA GPU 等は必要ではない
  - `mujoco` , `tensorflow` ( , `tensorboard` in venv )
  - ( EC2 インスタンスを借りるとかではなく ) 環境を整えれば自分の PC で動かるはず

- これだとファイルが足りない
  - 少なくとも `Q-LEARNING-DOUBLE_PENDULUM` フォルダまるごと必要
  - zip 圧縮 → USB メモリ経由で手元に持ってくる ( → 共有 ) → unzip

- [`tensorflow`](https://pypi.org/project/tensorflow/) による問題
  - Python **3.12 まで**しか対応してないので `uv init --python 3.12` などで 3.12 を使う
  - `numpy` の最新は `2.2.6` だが `tensorflow 2.19.0` の依存関係により `2.1.3` を使う ( 先に `uv add tensorflow` するとよい )

`Q-LEARNING-DOUBLE_PENDULUM` フォルダの他のファイルの依存関係でもっと古いバージョンが必要なら適宜対応する

### 細かい tips

- ( VSCode ) `uv` 環境での Pylance の interpreter 設定: https://code.visualstudio.com/docs/python/environments#_manually-specify-an-interpreter
