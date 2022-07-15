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

`docker-compose -f docker-compose-int.yml down`