# notebooks/

Dùng để **khám phá**, không phải nguồn sự thật. Quy ước:

* Đặt tên `NN_ten-nguoi_chu-de.ipynb`, ví dụ `01_huyen_aq2-heatmap.ipynb`.
* Đọc dữ liệu đã xử lý qua package, không đọc lại CSV gốc:

```python
from eduearlyalert.config import load_config
from eduearlyalert import features
cfg = load_config()
df, feature_cols = features.load(cfg)
```

* Biểu đồ/phân tích dùng được → chuyển vào `src/eduearlyalert/eda.py` (hàm `aqX_...`) rồi mở PR.
* Clear output trước khi commit (tránh lộ dữ liệu cá nhân trong output cell).
