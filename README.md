

https://lvarayut.github.io/relay-fullstack/
http://owaislone.org/blog/webpack-plus-reactjs-and-django/

to run, run the container with mapped ports:

docker-compose run --rm --service-ports web bash
python manage.py runserver 0.0.0.0:80

and:
``docker exec -it the_run_image_from_above bash``
``node server.js``


hostname to contact is in webpack.base.config.js.


update schema.json for relay: ``python manage.py graphql_schema``

build prod assets: webpack --config webpack.prod.config.js --progress --colors




switch from react-mdl to http://www.material-ui.com/ ?
