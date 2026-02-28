#!/bin/bash
# 同步主分支并提示冲突文件
# 用法：
#   bash sync-main.sh                # 默认 origin/main
#   bash sync-main.sh upstream main  # 指定远端与分支

set -euo pipefail

REMOTE="${1:-origin}"
TARGET_BRANCH="${2:-main}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ 当前目录不是 Git 仓库"
  exit 1
fi

if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  echo "❌ 远端 '$REMOTE' 不存在，请先配置 remote（如 git remote add origin <repo-url>）"
  exit 1
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

echo "📥 Fetch ${REMOTE}..."
git fetch "$REMOTE"

echo "🔀 Merge ${REMOTE}/${TARGET_BRANCH} -> ${CURRENT_BRANCH}"
set +e
git merge --no-edit "${REMOTE}/${TARGET_BRANCH}"
MERGE_CODE=$?
set -e

if [ $MERGE_CODE -eq 0 ]; then
  echo "✅ 合并完成，无冲突"
  exit 0
fi

echo "⚠️ 检测到冲突，请按下面列表逐个解决："
git diff --name-only --diff-filter=U || true

echo ""
echo "解决流程："
echo "1) 编辑冲突文件，清理 <<<<<<< ======= >>>>>>> 标记"
echo "2) git add <file1> <file2> ..."
echo "3) git commit -m 'Resolve merge conflicts from ${REMOTE}/${TARGET_BRANCH}'"
