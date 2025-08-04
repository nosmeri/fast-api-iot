source /home/deploy/fast-api-iot/.env

BACKUP_DIR="/home/deploy/db_backups"
CONTAINER_NAME="iot_db"
FILENAME="$1"

if [ -z "$FILENAME" ]; then
  echo "[ERROR] 복원할 파일 이름을 인자로 입력하세요."
  echo "예: ./rollback.sh backup-2025-08-01-0300.sql"
  exit 1
fi

if [ ! -f "$BACKUP_DIR/$FILENAME" ]; then
  echo "[ERROR] 파일이 존재하지 않습니다: $FILENAME"
  exit 1
fi

echo "[INFO] 복원 시작: $FILENAME"
docker exec -i $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB < "$BACKUP_DIR/$FILENAME"
echo "[INFO] 복원 완료"