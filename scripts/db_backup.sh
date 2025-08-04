# 설정
source /home/deploy/fast-api-iot/.env

DATE=$(date +%Y-%m-%d-%H%M)
BACKUP_DIR="/home/deploy/db_backups"
FILENAME="backup-$DATE.sql"

# 백업 실행
docker exec -t $DB_CONTAINER_NAME pg_dump -U $POSTGRES_USER $POSTGRES_DB --clean > $BACKUP_DIR/$FILENAME

# 이전 백업 자동 삭제 (최근 7개만 보관)
cd $BACKUP_DIR
ls -tp *.sql 2>/dev/null | tail -n +8 | xargs -I {} rm -- {}