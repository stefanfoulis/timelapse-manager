# <DOCKER_FROM>  # Warning: text inside the DOCKER_FROM tags is auto-generated. Manual changes will be overwritten.
FROM aldryn/base-project:3.1.0
# </DOCKER_FROM>

ENV PYTHONPATH /app/src:$PYTHONPATH

COPY stack/imageopt /stack/imageopt
RUN /stack/imageopt/install.sh

# <DOCKER_BUILD>  # Warning: text inside the DOCKER_BUILD tags is auto-generated. Manual changes will be overwritten.

# node modules
# ------------
# package.json is put into / so that mounting /app for local development
# does not require re-running npm install
ENV PATH=/node_modules/.bin:$PATH
RUN npm install -g npm-install-retry
COPY package.json /
RUN (cd / && npm-install-retry -- --production)

# bower requirements
# ------------------
COPY bower.json /app/
COPY .bowerrc /app/
RUN bower install --verbose --allow-root --config.interactive=false

# python requirements
# -------------------
RUN mkdir -p ~/.pip && printf "[global]\nindex-url = https://wheels.aldryn.net/d/pypi/aldryn-baseproject/\nfind-links=\n    file:///root/.cache/pip-tools/wheels\n    file:///root/.cache/pip-tools/pkgs\nextra-index-url=\n    https://devpi.divio.ch/aldryn/extras/+simple/\nretries = 11\n" > ~/.pip/pip.conf
COPY requirements.in /app/
COPY addons-dev /app/addons-dev/
RUN pip-compile -v
RUN pip install --no-deps -r requirements.txt

# add full sourcecode
# -------------------
COPY . /app

# static compilation with gulp (e.g sass)
# ---------------------------------------
ENV GULP_MODE=production
RUN gulp build; exit 0

# collectstatic
# -------------
RUN DJANGO_MODE=build python manage.py collectstatic --noinput --link

# </DOCKER_BUILD>
