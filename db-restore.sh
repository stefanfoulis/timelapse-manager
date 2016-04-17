#!/bin/bash
set -x
set -e

docker-compose up -d db
echo "Waiting 15s for dbs to start up..."
sleep 15
docker exec -i timelapsemanager_db_1 psql -U postgres -d db < ./tmp/dbdumps/db.sql
# echo "  Resetting pk sequences"
# docker exec -i timelapsemanager_db_1 psql -U postgres -d db -Atq < ./tmp/dbdumps/reset.sql | docker exec -i timelapsemanager_db_1 psql -U postgres -d db
