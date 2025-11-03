# Powertools for AWS Lambda (Python) サンプル集

Powertools for AWS Lambda (Python) の機能を活用したサンプルコード集です。

各機能の実装前後の比較を通じて、Powertools の利点を実演します。

## プロジェクト構成

### 01_typing
Typing 機能のサンプル
- **function_before.py**: 型定義なしの従来実装
- **function_after.py**: LambdaContext 型を使用した実装 (IDE の自動補完・型チェック対応)

### 02_jmespath
JMESPath Functions 機能のサンプル
- **function_before.py**: 手動でのループ処理とデータ抽出
- **function_after.py**: JMESPath クエリによる簡潔なデータ処理 (Base64 デコード, JSON 解析, フィルタリング)

### 03_validation
Validation 機能のサンプル
- **function_before.py**: 手動でのデータ検証とエラーハンドリング
- **function_after.py**: @validator デコレータによる自動バリデーション (入力/出力スキーマ検証)

### 04_parser
Parser 機能のサンプル
- **function_before.py**: 手動での JSON パースと型変換処理
- **function_after.py**: @event_parser デコレータによる自動パース (Pydantic モデル使用、型安全性向上)

### 05_parameters
Parameters 機能のサンプル
- **function.py**: parameters によるパラメータ取得処理

### 06_logger
Logger 機能のサンプル
- **function.py**: logger によるロギング処理

### 07_tracer
Tracer 機能のサンプル
- **function.py**: tracer によるトレース処理

## 技術スタック
- AWS Lambda
- AWS CDK
- Python
- AWS Lambda Powertools for Python
