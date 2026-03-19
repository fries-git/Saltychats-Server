# Saltychats

A new very simplistic python chat client meant to work on nearly anything that can run python 3.10.

To start, copy the example.env, and rename it .env. Set the webhook to any webhook you want messages to be posted to, port to the port you wish to use, and servername to what you want the server name to be.
Next, simply run main.py, and connect to it via client.py. Its on localhost:defined port. You can use port forwarding, tunneling, or any number of things to get it public.

> [!WARNING]
> The webhook system is currently highly unreccomended, as the text coloring and formatting leads to very messy messages. Be patient, it'll be implemented soon along with Discord integration (from discord to your server as webhooks can send to discord,) Fluxer integration, (Fluxer to your server as webhooks can already send to Fluxer,) and IRC implementation (to and from.) 

## TO-DO
- [ ] Move away from Rotur, make this entirely independent.
- [ ] Use JSON for messages and remove the message encoded coloring.
- [ ] Make the coloring on text purely client-sided.
- [ ] Add message storage and fetching.
- [ ] Update client to support these changes.
- [ ] Remove anything that I ai-generated to test or just do a quick patch before I left and then didn't work on this for a half a month.
- [ ] Add channels.
- [ ] Add user icons.
- [ ] Store data in a nice human-readable DB.
- [ ] Implement plugins system with easy to use functions for reading and sending messages.
- [ ] Add Fluxer plugin.
- [ ] Add discord plugin.
- [ ] Add IRC plugin (easiest.)
