# Resolving problems with Web-Store Code 

Now that we have seen some of the problems with our code it is time to resolve those problems 

Up frist let's stop the application 

`cd ~/docker/ecommerce-workshop/deploy`

`docker-compose -f docker-compose-int.yml down` 

Now let's tackle the code 

`cd ~/docker/ecommerce-workshop/store-frontend/src/store-front/app/views/spree/layouts`

We need to edit this file `spree_application.html.erb` and remove the following line 

```<br /><center><a href="<%= @ads['url'] %>"><img src="data:image/png;base64,<%= @ads['base64'] %>" /></a></center>```

[Example](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/main/docker/store-frontend/src/store-front/app/views/spree/layouts/spree_application.html.erb)

Now let's continue fixing our code 

`cd ~/docker/ecommerce-workshop/store-frontend/src/store-front/app/views/spree/home`

edit the `index.html.erb` file and add the following line at line 10 

```
  <br /><center><a href="<%= @ads['url'] %>"><img src="data:image/png;base64,<%= @ads['base64'] %>" /></a></center>
```
[Example](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/364d5b5f71dc9a72e4301aa0e73cecae1ba9f05c/docker/store-frontend/src/store-front/app/views/spree/home/index.html.erb.fixed#L11) 

# Build new image for the store frontend
Now we need to build new docker images for our app 

`~/docker/ecommerce-workshop/store-frontend`

Please note the tag version update 

`docker build . -t store-frontend:1.2`

Update the env file in the deploy directory 

`cd ~/docker/ecommerce-workshop/deploy` 

Edit `.env` so that we see the following `STORE_VER=1.2`

Now we can redploy and confirm that we have resolved the problem

`docker-compose -f docker-compose-int.yml up -d`

Now let's go back to the our dd accounts and confirm we've fixed the app.

# Resolving high latency and db problem 

During our review we found latency to be high within the ads service let's resolve that and redeploy.

`cd ~/docker/ecommerce-workshop/deploy` 

Take the app down 

`docker-compose -f docker-compose-int.yml down`

Let's edit the ads service app 

`cd ~/docker/ecommerce-workshop/ads-service`

The file having trouble is `ads.py` lets edit that 

Remove the following 

```
# adding function delay from 3s to 5s
def sleep(t):
    time.sleep(t)
```

And 

```
# adding delay from 3s to 5s
            num = random.randint(3,5)
            sleep(num)
```

[Example](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/main/docker/ads-service/ads.py)

down that we have resolved the ads service problem let's create a new docker image

# Build new image for ads service 

`docker build . -t ads:1.2` 

Before we relaunch let's resolve problems with the db service

`cd ~/docker/ecommerce-workshop/discounts-service`

And edit the `discounts.py` file to replace the following 

```
discounts = Discount.query.all()
```

with 

```
discounts = Discount.query.options(joinedload('*')).all()
```

[Example](https://github.com/ScottMabeDDHQ/tps-bootcamp/blob/dd820030ed838118be266ed04315a12dde950c0a/docker/discounts-service/discounts.py#L46)

# Build Docker image for Discounts service 

`docker build . -t discounts:1.2`

Now we need to update the env file to reflect the new versions of the images 

`cd ~/docker/ecommerce-workshop/deploy`

Edit the `.env` file to include discounts version 1.2 let's relaunch the application.

`docker-compose -f docker-compose-int.yml up -d`

# Now we need to make edits in the Datadog console.

To make sure logs are being paresed correctly we will clone the python pipeline and edit our newly created pipeline 
