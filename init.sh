#!/usr/bin/env bash

# Check and create directories if they do not exist
for dir in "configs" "data" "logs" "notebooks" "scripts" "src" "tests" "docker"
do
  if [ ! -d "$dir" ]; then
    mkdir "$dir"
  fi
done

# Check and create files if they do not exist
# Only create files if needed
for file in ".env" ".env.prod" ".gitignore" ".project-root" "Makefile" "requirements.txt"
do
  if [ ! -f "$file" ]; then
    touch "$file"
  fi
done

# Check and create src/__init__.py if it does not exist
# Only create file if needed
if [ ! -f "src/__init__.py" ]; then
  touch "src/__init__.py"
fi

if [ ! -f "docker/Dockerfile" ]; then
  touch "docker/Dockerfile"
fi

if [ ! -f "docker/prod.Dockerfile" ]; then
  touch "docker/prod.Dockerfile"
fi

# Store the tree structure (after creating needed files and dirs)
TREE=$(tree -a --dirsfirst -I "__pycache__|\.ipynb_checkpoints|\.idea|\.git|\.venv")

# Write the .clinerules file at the end
cat <<EOF > .clinerules
Each answer always starts with "Dear Lord Voldemort" and ends with "Your loyal Death Eater".

# Project Introduction
Backend built with fastapi.

# Architecture
The main code of the core architecture is as follows

$TREE

# Technology Stack
FastAPI
Hydra
rootutils

# Requirements
- All comments in the code and the answer must be written in English.
- Comments should be added only when necessary, and unnecessary comments will be deducted.
- When introducing packages or files in this project, use the following code in the import part. For files in the project, use ROOT_DIR / <relative path in the project> to introduce them.
- Each modification should follow the principle of minimum modification. If it is not necessary, do not add entities, and if it is not necessary, do not increase complexity.

\`\`\`python
import rootutils

ROOT_DIR = rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
\`\`\`
EOF
