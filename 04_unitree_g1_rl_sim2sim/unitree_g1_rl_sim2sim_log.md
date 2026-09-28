# 技術実装・運用検証記録：Unitree G1 強化学習環境構築および MuJoCo Sim2Sim パイプライン統合

**文書種別:** 実装・運用検証記録（Technical Implementation & Operational Log）  
**対象ロボット:** 宇樹科技（Unitree Robotics）人型ロボット「G1（29自由度モデル）」  
**検証機材・GPU:** NVIDIA GeForce RTX 5060 Ti (VRAM 16GB)  
**主要スタック:** Ubuntu 22.04 LTS, NVIDIA Driver 580.178.04, Isaac Sim 5.1.0, Isaac Lab v2.3.2, MuJoCo 3.x, Unitree SDK2  

---

## 1. 概要および検証目的

本記録は、次世代人型ロボット「Unitree G1（29-DoF）」の歩行・全身運動制御アルゴリズム開発を目的として、最新の物理シミュレーション環境（NVIDIA Isaac Sim / Isaac Lab）および物理エンジン（MuJoCo）を用いた **Sim2Sim（シミュレータ間動作検証）パイプラインの構築と実動作確認** を行った実装ログである。

手元の実機開発環境（**NVIDIA GeForce RTX 5060 Ti 16GB**）において、Isaac Lab 上での強化学習（RL）の並行実行、ポリシー推論の可視化再生、ならびに MuJoCo 物理環境へのポリシー転送（Sim2Sim）までの一連のパイプラインが完全に稼働することを確認した。

本稿では、実機環境で実施した具体的な実装手順、発生した技術課題、講じたパラメータ調整値、および実際の実行画面キャプチャを記録する。

---

## 2. 開発環境およびハードウェア構成

| 項目 | 採用スペック / バージョン | 備考・選定理由 |
| :--- | :--- | :--- |
| **GPU** | **NVIDIA GeForce RTX 5060 Ti (VRAM 16GB)** | 大容量VRAMにより並行環境数（`num_envs`）の大規模化を担保 |
| **OS** | **Ubuntu 22.04.5 LTS** (Kernel 6.8.0-138-generic) | 開発標準OS環境 |
| **NVIDIA Driver** | **580系 (580.178.04)** | 最新アーキテクチャ対応および CUDA 12.8 互換 |
| **シミュレータ** | **NVIDIA Isaac Sim 5.1.0** (Standalone Binary) | 安定性とバージョン固定のためバイナリ方式を採用 |
| **RLフレームワーク** | **Isaac Lab v2.3.2** | 指定バージョンへ固定チェックアウト |
| **Python環境** | **Python 3.11** (Miniconda: `env_isaaclab`) | Isaac Sim 5.x 公式推奨バージョン |
| **深層学習ライブラリ** | **PyTorch 2.7.0 (CUDA 12.8 ビルド)** | Lab 2.3.2 仕様に準拠 |
| **対象ロボット** | **Unitree G1 (29-DoF)** | USD形式 / URDF形式の両面で検証 |
| **Sim2Sim 環境** | **MuJoCo 3.x + Unitree SDK2 + g1_ctrl** | C++ ベースのローカルコントローラ |

---

## 3. 実装・検証フェーズの構成

```
[Phase 1: Isaac Sim 基盤配備] 
   └── 5.1.0 バイナリ展開、シェーダー初回コンパイル、環境変数永続化
[Phase 2: Isaac Lab 連携・依存解決] 
   └── Conda 仮想環境構築、`_isaac_sim` リンク、RLフレームワーク組込み
[Phase 3: Unitree G1 モデル統合] 
   └── Git LFS による高精度 USD アセット取得、絶対パス参照の構成
[Phase 4: 強化学習 (RL) 及びポリシー推論] 
   └── Headless モードでの並行学習実行、チェックポイント生成、Play 検証
[Phase 5: Sim2Sim (MuJoCo) 展開] 
   └── Unitree SDK2 導入、C++ コントローラビルド、仮想ジョイスティック連携
```

---

## 4. 発生課題とパラメータ調整・解決策

### 課題 1：最新GPU（RTX 5060 Ti）と旧ドライバの不整合
- **事象:** レガシーな環境ガイドにある旧ドライバ（525〜535系）は、RTX 5060 Ti および Linux Kernel 6.8 系でビルドエラーとなる。
- **対策:** 最新の **NVIDIA Driver 580（580.178.04）** および **PyTorch 2.7.0（CUDA 12.8 ビルド）** を採用。

### 課題 2：Isaac Lab 初期化時の PhysX エラー停止
- **事象:** 大量並行環境（`num_envs = 4096`）および急峻な崎岖地形において、初期ステップで PhysX 物理エンジンの過負荷停止（`PhysX has reported too many errors`）が発生。
- **対策:** 初期立ち上げ時の環境数を調整し、物理ソルバーの反復回数（`solver_position_iteration_count: 4 -> 8`）および接触オフセットを最適化して物理破綻を解消。

### 課題 3：Git LFS 未適用による USD アセット破損
- **事象:** Unitree モデル読み込み時にシミュレータがクラッシュ。
- **対策:** `git-lfs` を導入して完全な USD メッシュバイナリを再取得し、絶対パス（`/home/andre/projects/unitree_model`）でパス指定を正規化。

### 課題 4：MuJoCo 設定ファイルの構文不整合
- **事象:** Sim2Sim 実行時に仮想ジョイスティックおよび DDS 通信が正しく連動しない。
- **対策:** `config.yaml` のタイポ修正（`use_joystick: 1`）および通信ドメイン（`domain_id: 0`）を C++ `g1_ctrl` と完全整合。

---

## 5. 動作検証ログおよび実行画面記録

### 5.1 Isaac Lab 基盤検証（ANYmal-C 四足モデル）

初期検証として、Isaac Lab の四足歩行タスク（`Isaac-Velocity-Rough-Anymal-C-v0`）を起動し、物理演算および描画パイプラインの健全性を確認した。

#### 崎岖地形での環境初期化
![Isaac Lab 崎岖地形初期化](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/isaaclab_anymal_c_rough_terrain_init.png)

#### 物理エラー発生と関節構造の切り分け
初期の急激な接触判定により PhysX エラーが発生した際、Stage ツリーから各リンク・関節（`LF_HFE`, `LF_THIGH`, `LF_SHANK` 等）の拘束条件と衝突判定を調査・切り分けた。

![PhysX エラー停止の発生](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/isaaclab_anymal_c_physx_error.png)

![Stage 関節ツリー構造の確認](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/isaaclab_anymal_c_stage_joints_physx_error.png)

#### 速度目標ベクトル可視化と安定走行
パラメータ調整後、目標速度（`velocity_goal`）ベクトルへの追従動作が安定して継続することを確認。

![目標速度ベクトル可視化](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/isaaclab_anymal_c_velocity_goal_visualization.png)

![速度追従動作の安定化](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/isaaclab_anymal_c_velocity_tracking_success.png)

---

### 5.2 Unitree G1 モデルの Isaac Sim / Isaac Lab 統合

G1（29-DoF）の USD アセットを Isaac Sim および Isaac Lab に統合し、関節階層、マテリアル、環境光を構成した。

#### G1 モデルの USD Stage ツリー・衝突判定構成
![Isaac Sim G1 関節構造と衝突判定](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/isaacsim_g1_humanoid_usd_stage_tree.png)

#### G1 3D メッシュ描画の確認
![Isaac Sim G1 メッシュレンダリング](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/isaacsim_g1_humanoid_mesh_viewport.png)

#### Isaac Lab 学習用グラウンドおよび照明配置
![Isaac Lab 地面・環境光構成](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/isaaclab_g1_ground_terrain_setup.png)

#### 強化学習環境（`env_0`）での G1 ロボット階層
![Isaac Lab env_0 ロボット構成](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/isaaclab_g1_env0_robot_hierarchy.png)

---

### 5.3 G1 強化学習（RL）メトリクスモニタリング

`rsl_rl` を用いて G1 の速度追従タスク（`Unitree-G1-29dof-Velocity`）を学習させ、TensorBoard にてリアルタイムに報酬遷移をモニタリングした。

#### カリキュラム学習進行度および基本報酬
![TensorBoard カリキュラムと基本報酬](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/tensorboard_g1_curriculum_and_rewards.png)

#### 詳細報酬項（ベース高度・関節リミット・足部接地/スライド）
ベース高さ維持（`base_height`）、線形速度（`base_linear_velocity`）、足部クリアランス（`feet_clearance`）、足部スライド抑制（`feet_slide`）の各指標が健全に収束していることを確認。

![TensorBoard 詳細報酬指標](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/tensorboard_g1_detailed_reward_metrics.png)

---

### 5.4 MuJoCo への Sim2Sim 展開・動作確認

学習済みポリシー（`.pt`）を C++ コントローラ `g1_ctrl` にロードし、`unitree_mujoco` 上で Sim2Sim 動作を検証した。

![MuJoCo G1 Sim2Sim 動作画面](file:///root/bra/PhysicalAiLab/04_unitree_g1_rl_sim2sim/imgs/mujoco_g1_29dof_sim2sim_scene.png)

- **検証結果:** 
  - MuJoCo 物理環境内において、G1 29自由度モデルが起立状態を維持し、仮想ジョイスティックからの速度入力指令に対してリアルタイムに歩行動作が連動することを確認。
  - Isaac Lab（大規模並行学習）$\rightarrow$ MuJoCo（高忠実度物理検証）の Sim2Sim パイプラインが完全開通した。

---

## 6. まとめおよび今後の開発計画

1. **実証完了事項:**
   - RTX 5060 Ti (16GB) 上での Isaac Sim 5.1.0 / Isaac Lab 2.3.2 安定運用環境の確立。
   - Unitree G1（29-DoF）の強化学習およびチェックポイント生成の成功。
   - MuJoCo 物理エンジンを用いた C++ Sim2Sim コントローラとのリアルタイム連動の成立。
2. **次期実装項目:**
   - 階段・段差等の不整地走行に向けた報酬関数のカスタマイズ（Reward Shaping）。
   - 実機転送（Sim2Real）を見据えたドメインランダマイゼーション（摩擦・質量・通信遅延）の強化。
