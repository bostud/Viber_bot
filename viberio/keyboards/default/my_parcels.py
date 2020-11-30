my_parcels_kb = {
    # "DefaultHeight": True,
    # "BgColor": "#FFFFFF",
    "Type": "keyboard",
    "Buttons": [
        {
            "Columns": 3,
            "Rows":1,
            "BgColor": "#e6f5ff",
            # "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "parcels_in",
            "ReplyType": "message",
            "TextSize": "large",
            "Text": "До мене"
        },
        {
            "Columns": 3,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            # "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "parcels_out",
            "ReplyType": "message",
            "TextSize": "large",
            "Text": "Від мене"
        },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            # "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "parcels_archive",
            "ReplyType": "message",
            "TextSize": "large",
            "Text": "Архів"
        },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": "#e6f5ff",
            # "BgLoop": True,
            "ActionType": "reply",
            "ActionBody": "main_menu",
            "ReplyType": "message",
            "TextSize": "large",
            "Text": "До головного меню"
        }
    ]
}
