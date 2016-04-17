#!/bin/bash
mkdir -p ./tmp/dbdumps
docker-compose up -d db
docker exec timelapsemanager_db_1 pg_dump -U postgres -d db > ./tmp/dbdumps/db.sql
