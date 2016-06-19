FROM stefanfoulis/timelapse-manager:base-py3-1.0

#RUN npm install -g npm-install-retry
ENV PATH=/app/node_modules/.bin:$PATH
#COPY package.json /package.json
#RUN (cd / && npm install)
##RUN (ln -s /app/package.json /package.json && cd / && npm-install-retry)
#RUN (ln -s /app/package.json /package.json && cd / && npm install)

# add full sourcecode
# -------------------
COPY . /app

# static compilation with gulp (e.g sass)
# ---------------------------------------
RUN webpack --config webpack.prod.config.js --progress --colors

# collectstatic
# -------------
RUN DJANGO_MODE=build python manage.py collectstatic --noinput --link
