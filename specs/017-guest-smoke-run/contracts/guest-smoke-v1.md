# Contract: guest smoke v1

- `POST /web/v1/guest/window/start` — start window if under daily limit; attach news or accept fact.
- `POST /web/v1/guest/window/message` — body: text + captcha token; returns agent reply or gate flag after 3rd.
- `POST /web/v1/guest/window/clear` — client clear UI marker.
