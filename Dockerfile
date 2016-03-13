# <DOCKER_FROM>  # Warning: text inside the DOCKER_FROM tags is auto-generated. Manual changes will be overwritten.
FROM aldryn/base-project:3.1.0
# </DOCKER_FROM>

# <DOCKER_BUILD>  # Warning: text inside the DOCKER_BUILD tags is auto-generated. Manual changes will be overwritten.

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

# collectstatic
# -------------
RUN DJANGO_MODE=build python manage.py collectstatic --noinput --link

# </DOCKER_BUILD>

