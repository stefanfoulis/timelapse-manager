FROM stefanfoulis/timelapse-manager:1.5.0

COPY . /app

RUN DJANGO_MODE=build python manage.py graphql_schema
RUN npm run build-production
RUN DJANGO_MODE=build python manage.py collectstatic --noinput
