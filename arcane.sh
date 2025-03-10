# Check if a file is provided as an argument
if [ $# -eq 0 ]; then
    echo "Usage: arcane <file.arc>"
    exit 1
fi



filename="${1%}"
source ~/random_projects/arcane/.venv/bin/activate
python ~/random_projects/arcane/src/arcane/main.py $filename

