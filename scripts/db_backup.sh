# 설정
source /home/deploy/fast-api-iot/.env

DATE=$(date +%Y-%m-%d-%H%M)
BACKUP_DIR="/home/deploy/db_backups"
FILENAME="backup-$DATE.sql"
CONTAINER_NAME="fastapi_db"

# 백업 실행
docker exec -t $CONTAINER_NAME pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_DIR/$FILENAME

# 이전 백업 자동 삭제 (최근 7개만 보관)
cd $BACKUP_DIR
ls -tp | grep -v '/$' | tail -n +8 | xargs -I {} rm -- {}