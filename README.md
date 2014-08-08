### Local set-up:

Install requirements, create heroku app
```
$ sudo pip install -r requirements.txt
$ heroku create --stack cedar
$ heroku apps:rename APPNAME
```

Create .env file with your twitter app keys:
```
TWITTER_CONSUMER_KEY=replace_this
TWITTER_CONSUMER_KEY=replace_this
TWITTER_CONSUMER_KEY=replace_this
TWITTER_CONSUMER_KEY=replace_this
```

Now tell heroku they're in .env
```
$ heroku plugins:install git://github.com/ddollar/heroku-config.git
$ heroku config:push
```

Add a database to your heroku app.
```
$ heroku addons:add heroku-postgresql:dev
    Added heroku-postgresql:dev to thu-jehosafet (Free).
    Attached as HEROKU_POSTGRESQL_AQUA_URL Database has been created and is available !
    This database is empty.
    If upgrading, you can transfer ! data from another database with pgbackups:restore.
```

Make sure to replace `HEROKU_POSTGRESQL_AQUA_URL` in case it's different in your case.

```
$ heroku config | grep HEROKU_POSTGRESQL
$ heroku pg:promote HEROKU_POSTGRESQL_AQUA_URL
```

Now, create a local database.
```
$ psql

># CREATE DATABASE test;
># \q

$ foreman start
```
