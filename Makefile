# Dùng được trên macOS/Linux/WSL. Trên Windows thuần: chạy các lệnh python tương ứng trong README.
PY ?= python

.PHONY: setup fake data pipeline test dashboard clean

setup:            ## cài môi trường
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e .

fake:             ## sinh dữ liệu GIẢ để thử pipeline (không dùng cho báo cáo)
	$(PY) scripts/make_fake_oulad.py --out data/raw

pipeline:         ## chạy toàn bộ pipeline
	$(PY) -m eduearlyalert.pipeline all

test:             ## chạy test (dùng dữ liệu giả, không đụng data/raw)
	$(PY) -m pytest

dashboard:        ## mở dashboard demo
	streamlit run app/dashboard.py

clean:            ## xoá output sinh ra (giữ data/raw)
	rm -rf data/interim/* data/processed/* reports/*.md reports/*.csv reports/*.json reports/*.jsonl reports/figures/*.png
	touch data/interim/.gitkeep data/processed/.gitkeep reports/figures/.gitkeep
