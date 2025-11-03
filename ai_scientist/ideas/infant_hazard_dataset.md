# Title: Tapoカメラを用いた乳児危険検知AIのための高忠実度合成データセット生成手法の研究 (Research on High-Fidelity Synthetic Dataset Generation for Tapo Camera-Based Infant Hazard Detection AI)

## Keywords
synthetic data, generative AI, infant safety, baby monitoring, Tapo camera, object detection, pose estimation, data-centric AI

## TL;DR
Tapoカメラで乳児の危険（例：階段への侵入）を検知するAIモデルを開発したい。しかし、危険なシーンの実データは倫理的に収集困難である。本研究は、Stable Diffusionなどの生成AIを用い、Tapoカメラ（`baby_monitor`プロジェクト）の視点や歪みに最適化された合成乳児データセットを生成する最適な手法を研究する。

## Abstract
家庭用ネットワークカメラ（Tapoカメラ）とAIを用いた乳児の安全監視システムは、危険エリアへの侵入を未然に防ぐために重要である。これらのAIモデル（例：MobileNet SSD）の学習には、多様な状況下での乳児のデータセット、特に「危険エリア（カーテンや階段）への侵入」といった特定の危険シナリオのデータが不可欠である。しかし、こうした危険なシーンの実データを収集することは、プライバシー保護と倫理的な観点から極めて困難である。

このデータ不足を補うため、生成AI（Generative AI）を用いた合成データが注目されている。しかし、単純に生成された画像（例：「a baby crawling」）は、`baby_monitor`プロジェクトで実際に使用するTapoカメラ特有の視点、レンズ歪み（`calibration_data.npz` で補正されるもの）、家庭内の照明環境と大きく異なる。そのため、こうした単純な合成データでは、AIモデルの検知精度が期待通りに向上しない可能性が高い (ICBINB)。

本研究は、この「Tapoカメラの現実環境と合成データのギャップ」という課題に着目し、乳児の安全監視AIの精度を最大化するための最適な合成データセット生成手法を研究する。

実験では、以下の手法で生成したデータセットで物体検出モデルを学習させ、現実のTapoカメラの視点（俯瞰や特定の角度）を模したテストデータに対する危険検知精度を比較する。

1.  **単純な画像生成 (Baseline):** Stable Diffusion等で生成した一般的な乳児の画像。
2.  **姿勢誘導生成 (Pose-Conditioned):** OpenPoseなどの骨格情報で「つかまり立ち」や「転倒寸前」などの危険な姿勢を指定して生成した画像。
3.  **環境・視点適応型生成 (Viewpoint-Adapted):** `baby_monitor`プロジェクトのように、カメラのキャリブレーション情報やArUcoマーカー の3D空間情報を考慮し、Tapoカメラ特有の俯瞰視点や歪みに合わせて生成した画像。

本研究の目的は、プライバシーを保護しつつ、Tapoカメラを用いた乳児監視システムの危険検知精度を最大化する「最適な合成データセット生成のベストプラクティス」を確立することである。