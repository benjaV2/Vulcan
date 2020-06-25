
First you need to setup a mongo db (ubuntu server instructions):

## MONGO INSTALLATION
    ```
    sudo apt install docker.io
    sudo docker pull mongo
    sudo docker run -it --name mongodb -p 27017:27017 -d mongo
    ```


Then you can install the app:

## APPLICATION INSTALLATION:
    ```
    clone the repo into your application server
    cd into API_SERVER
    pip install -r requirments.txt
    set MONGO_URL env var to the mongo server IP
    python manage runserver 0.0.0.0:port
    on the first run the app will init the mongo db and populate it with data
    ```


## API EXPLANATION:
    ```
    you can now use the api.
    the API consist of 3 get methods:
    ```

    GET APP_SERVER_IP:port/plugins/id/<plugin_id>
        searches for the plugin with the specific id

    GET APP_SERVER_IP:port/plugins/cve/<cve name>
        searches for ALL the plugins with this cve

    GET APP_SERVER_IP:port/plugins/list_all/[optional order]
        fetches all available plugins. if order is passed it orders the plugin
        by a specific order
        available orders : ['pluginID', 'score', 'published']
        if a different order is passed an error will return




