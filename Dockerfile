FROM stefanfoulis/timelapse-manager:base-0.4

# add full sourcecode
# -------------------
COPY . /app

# static compilation with gulp (e.g sass)
# ---------------------------------------
#ENV GULP_MODE=production
#RUN gulp build; exit 0

# collectstatic
# -------------
RUN DJANGO_MODE=build python manage.py collectstatic --noinput --link
