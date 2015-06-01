# hover-client

Python client for the undocumented, unofficial [Hover.com](http://hover.com)  API.

Based on Dan Krause's excellent [gist](https://gist.github.com/dankrause/5585907).

## Usage

Import and then instantiate the client as follows:

    import hover.client
    hc = hover.client.HoverClient(username, password, domain)

Add a new DNS record with:

    hc.add_record(type, name, content)

Remove an existing DNS record with:

    hc.remove_record(type, name)

