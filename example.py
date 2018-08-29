from SignalPy import *

app_id = "YOUR-APP-ID"
api_key = "YOUR-API-KEY"

client = OneSignal(app_id, api_key)

buttons = Buttons().add_button('b1', 'Delete')\
                   .add_button('b2', 'View')\
                   .add_web_buttons('w1', 'Open Page', 'icon', 'http://google.com')

filters = Filter().session_count(Relation.GreaterThan, 10)\
                  .session_time(Relation.LowerThan, 2000)\
                  .location(radius=10, long=45.754, lat=54.324)

delivery = Delivery().send_after(datetime.now() + timedelta(days=10))\
                     .delivery_time_of_day("10:00AM")\
                     .priority(10)\
                     .delayed_option(DelayedOption.LastActive)

notification = Notification().add_buttons(buttons)\
                             .add_filters(filters)\
                             .set_delivery(delivery)\
                             .add_content(LangCodes.English, 'Hey There!')

client.post(notification)
