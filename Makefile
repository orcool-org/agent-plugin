DIST_DIR := dist
STAGE_DIR := $(DIST_DIR)/stage
PLUGIN := $(DIST_DIR)/orcool.plugin

SOURCES := .claude-plugin skills .mcp.json LICENSE

.PHONY: build clean

build: clean
	@mkdir -p $(STAGE_DIR)
	@cp -R $(SOURCES) $(STAGE_DIR)/
	@find $(STAGE_DIR) -name '.DS_Store' -delete
	@cd $(STAGE_DIR) && zip -qr ../orcool.zip .
	@mv $(DIST_DIR)/orcool.zip $(PLUGIN)
	@rm -rf $(STAGE_DIR)
	@echo "Built plugin at $(PLUGIN)"

clean:
	@rm -rf $(DIST_DIR)
