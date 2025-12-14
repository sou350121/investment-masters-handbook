# Investment Masters Handbook - Makefile

.PHONY: help validate generate query clean install

help:
	@echo "常用命令:"
	@echo "  make validate   运行所有校验"
	@echo "  make generate   生成派生文件"
	@echo "  make query      查询规则"
	@echo "  make clean      清理缓存"
	@echo "  make install    安装依赖"

validate:
	python scripts/check_links.py
	python scripts/validate_front_matter.py
	python scripts/check_router_config.py
	python scripts/scan_sensitive.py

generate:
	python scripts/generate_artifacts.py

query:
	python tools/rule_query.py $(ARGS)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

install:
	pip install -r requirements.txt
