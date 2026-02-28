# Saltychats

A new very simplistic python chat client meant to work on nearly anything that can run python 3.10.

To start, copy the example.env, and rename it .env. Set the webhook to any webhook you want messages to be posted to, port to the port you wish to use, and servername to what you want the server name to be.
Next, simply run main.py, and connect to it via client.py. Its on localhost:defined port. You can use port forwarding, tunneling, or any number of things to get it public.

> [!WARNING]
> The webhook system is currently highly unreccomended, as the text coloring and formatting leads to very messy messages. Be patient, it'll be implemented soon along with Discord integration (from discord to your server as webhooks can send to discord,) Fluxer integration, (Fluxer to your server as webhooks can already send to Fluxer,) and IRC implementation (to and from.) 