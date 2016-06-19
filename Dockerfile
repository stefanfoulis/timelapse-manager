FROM stefanfoulis/timelapse-manager:base-py3-1.2

COPY . /app

RUN DJANGO_MODE=build python manage.py graphql_schema
RUN npm run build-production
RUN DJANGO_MODE=build python manage.py collectstatic --noinput --link
