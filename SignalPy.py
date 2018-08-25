from enum import Enum
import json
import re


class _LangCodes:
    """LangCodes Class"""

    def load(self, filename):
        """ loads lang codes from json file """
        data = json.loads(open(filename, 'r').read())
        for key, info in data.items():
            setattr(self, info['name'], key)
        return self


# load language codes from json file
LangCodes = _LangCodes().load('lang_codes.json')


class Relation(Enum):
    GreaterThan = '>'
    LowerThan = '<'
    Equal = '='
    NotEqual = '!='
    Exists = 'exists'
    NotExists = 'not_exists'


class Filter:

    def __init__(self):
        """ initiate a new Filter """
        self._values = []

    @staticmethod
    def accepts(relations: [Relation], provided: Relation):
        """
        check to see whether a provided relation is acceptable
        :param relations: list of accepted relations
        :param provided: the provided relation
        """
        if not any([provided == relation for relation in relations]):
            raise Exception('Invalid relation was provided')
        return True

    def _base_filter(self, field, relation: Relation, value, key=None):
        """
        base filter generator
        :param field: field name
        :param relation: filter's relation
        :param value: filter's value
        :param key: optional filter key
        """
        json_data = {'field': field, 'relation': relation.value, 'value': value}
        if key:
            json['key'] = key
        self._values.append(json_data)
        return self

    def last_session(self, relation: Relation, hours_ago: float):
        """
        :param relation: ">" or "<"
        :param hours_ago: number of hours before or after the users last session.
        """
        Filter.accepts([Relation.GreaterThan, Relation.LowerThan], relation)
        return self._base_filter('last_session', relation, hours_ago)

    def first_session(self, relation: Relation, hours_ago: float):
        """
        :param relation: ">" or "<"
        :param hours_ago: number of hours before or after the users first session.
        """
        Filter.accepts([Relation.GreaterThan, Relation.LowerThan], relation)
        return self._base_filter('first_session', relation, hours_ago)

    def session_count(self, relation: Relation, count: int):
        """
        :param relation: ">", "<", "=" or "!="
        :param count: number of sessions
        """
        Filter.accepts([Relation.GreaterThan, Relation.LowerThan,
                        Relation.Equal, Relation.NotEqual], relation)
        return self._base_filter('session_count', relation, count)

    def session_time(self, relation: Relation, seconds: int):
        """
        :param relation: ">", "<"
        :param seconds: time in seconds the user has been in your app
        """
        Filter.accepts([Relation.GreaterThan, Relation.LowerThan], relation)
        return self._base_filter('session_time', relation, seconds)

    def amount_spent(self, relation: Relation, amount: float):
        """
        :param relation: ">", "<" or "="
        :param amount: Amount in USD a user has spent on IAP
        """
        Filter.accepts([Relation.GreaterThan, Relation.LowerThan,
                        Relation.Equal], relation)
        return self._base_filter('amount_spent', relation, amount)

    def bought_sku(self, key: str, relation: Relation, amount: float):
        """
        :param key: SKU purchased in your app as IAP
        :param relation: ">", "<", "="
        :param amount: value of SKU to compare to
        """
        Filter.accepts([Relation.GreaterThan, Relation.LowerThan,
                        Relation.Equal], relation)
        self._base_filter(key, relation, amount)

    def tag(self, key: str, relation: Relation, value: str):
        """
        Note: value is not required for "exists or "not_exists"
        :param key: tag key to compare to
        :param relation: ">", "<", "=", "!=", "exists", "not_exists"
        :param value: Tag value to compare to
        """
        self._base_filter('tag', relation, value, key=key)

    def language(self, relation: Relation, lang: str):
        """
        :param relation: "=", "!="
        :param lang: 2 character lang code
        """
        Filter.accepts([Relation.Equal, Relation.NotEqual], relation)
        self._base_filter('language', relation, lang)

    def app_version(self, relation: Relation, version: str):
        """
        :param relation: ">", "<", "=", "!="
        :param version:  app version
        """
        Filter.accepts([Relation.GreaterThan, Relation.LowerThan,
                        Relation.Equal, Relation.NotEqual], relation)
        self._base_filter('app_version', relation, version)

    def location(self, radius: float, lat: float, long: float):
        """
        :param radius: radius in meters
        :param lat: latitude
        :param long: longitude
        """
        self._values.append({'radius': radius, 'lat': lat, 'long': long})
        return self

    def country(self, country_code: str):
        """
        Relation is always '='
        :param country_code: 2-digit country code
        """
        return self._base_filter('country', Relation.Equal, country_code)

    @property
    def and_(self):
        """ appends And between the previous and next entries """
        self._values.append({'operator': 'AND'})
        return self

    @property
    def or_(self):
        """ appends Or between the previous and next entries """
        self._values.append({'operator': 'OR'})
        return self

    def to_json(self):
        """ :return: json formatter filter """
        return json.dumps(self._values)


class TargetDevice:

    def __init__(self):
        self._values = {}

    def include_player_ids(self, tokens: [str]):
        """
        Set specific players to send your notification to
        :param tokens: specific player ids
        """

        if len(tokens) > 2000:
            raise Exception('Exceeded the limit of 2000 per api call')
        self._values['include_player_ids'] = tokens
        return self

    def include_ios_tokens(self, tokens: [str]):
        """
        Please consider using include_player_ids instead
        Target using iOS device tokens. Warning: Only works with Production tokens.
        :param tokens: iOS device tokens
        """

        if len(tokens) > 2000:
            raise Exception('Exceeded the limit of 2000 per api call')
        # removing all non alphanumerical characters
        tokens = map(lambda x: re.sub(r'\W+', '', x), tokens)
        self._values['include_ios_tokens'] = tokens
        return self

    def include_wp_wns_uris(self, tokens: [str]):
        """
        Please consider using include_player_ids instead
        Target using Windows URIs.
        If a token does not correspond to an existing user, a new user will be created
        :param tokens: Windows URIs
        """
        if len(tokens) > 2000:
            raise Exception('Exceeded the limit of 2000 per api call')
        self._values['include_wp_wns_uris'] = tokens
        return self

    def include_amazon_reg_ids(self, tokens: [str]):
        """
        Please consider using include_player_ids instead
        Target using Amazon ADM registration IDs.
        If a token does not correspond to an existing user, a new user will be created.
        :param tokens: Amazon ADM registration IDs
        """
        if len(tokens) > 2000:
            raise Exception('Exceeded the limit of 2000 per api call')
        self._values['include_amazon_reg_ids'] = tokens
        return self

    def include_chrome_reg_ids(self, tokens: [str]):
        """
        Please consider using include_player_ids instead
        Target using Chrome App registration IDs.
        If a token does not correspond to an existing user, a new user will be created
        :param tokens:
        """
        if len(tokens) > 2000:
            raise Exception('Exceeded the limit of 2000 per api call')
        self._values['include_chrome_reg_ids'] = tokens
        return self

    def include_chrome_web_reg_ids(self, tokens: [str]):
        """
        Please consider using include_player_ids instead
        Target using Chrome Web Push registration IDs.
        If a token does not correspond to an existing user, a new user will be created.
        :param tokens: Chrome Web Push registration IDs
        """
        if len(tokens) > 2000:
            raise Exception('Exceeded the limit of 2000 per api call')
        self._values['include_chrome_web_reg_ids'] = tokens
        return self

    def include_android_reg_ids(self, tokens: [str]):
        """
        Please consider using include_player_ids instead
        Target using Android device registration IDs.
        If a token does not correspond to an existing user, a new user will be created.
        :param tokens: Android device registration IDs
        """
        if len(tokens) > 2000:
            raise Exception('Exceeded the limit of 2000 per api call')
        self._values['include_android_reg_ids'] = tokens
        return self

    def to_json(self):
        """ :return: json formatted TargetDevice """
        return json.dumps(self._values)


class Notification:

    def __init__(self):
        self._data = {}

    def add_filters(self, filters: Filter):
        """
        add user targeting filters
        :param filters: filter instance
        """
        self._data['filters'] = filters.to_json()
        return self

    def add_segments(self, segments: [str]):
        """
        add target segments
        :param segments: list of segments
        """
        self._data['included_segments'] = segments
        return self

    def add_content(self, lang_code: str, message: str):
        """
        The notification's content (excluding the title),
        a map of language codes to text for each language.
        :param lang_code: language code string
        :param message: localized text
        """
        if not hasattr(self._data, 'contents'):
            self._data['contents'] = {}

        self._data['contents'][lang_code] = message
        return self

    def add_contents(self, json_content: dict):
        """
        The notification's content (excluding the title),
        a map of language codes to text for each language.
        :param json_content: add bulk json content
        Example: {"en": "English Message", "es": "Spanish Message"}
        """
        if not hasattr(self._data, 'contents'):
            self._data['contents'] = {}

        data = self._data['contents'].items() + json_content.items()
        self._data['contents'] = dict(data)
        return self

    def add_heading(self, lang_code: str, heading: str):
        """
        The notification's title, a map of language codes to text for each language
        :param lang_code: language code string
        :param heading: localized text
        """
        if not hasattr(self._data, 'headings'):
            self._data['headings'] = {}

        self._data['headings'][lang_code] = heading
        return self

    def add_headings(self, json_heading: dict):
        """
        The notification's title, a map of language codes to text for each language
        :param json_heading: add bulk json heading
        Example: {"en": "English Title", "es": "Spanish Title"}
        """
        if not hasattr(self._data, 'headings'):
            self._data['headings'] = {}

        data = self._data['headings'].items() + json_heading.items()
        self._data['headings'] = dict(data)
        return self

    def add_subtitle(self, lang_code: str, subtitle: str):
        """
        The notification's subtitle, a map of language codes to text for each language.
        :param lang_code: language code string
        :param subtitle: localized text
        """
        if not hasattr(self._data, 'subtitle'):
            self._data['subtitle'] = {}

        self._data['subtitle'][lang_code] = subtitle
        return self

    def add_subtitles(self, json_subtitles: dict):
        """
        The notification's subtitle, a map of language codes to text for each language.
        :param json_subtitles: add bulk json heading
        Example: {"en": "English Subtitle", "es": "Spanish Subtitle"}
        """
        if not hasattr(self._data, 'subtitle'):
            self._data['subtitle'] = {}

        data = self._data['subtitle'].items() + json_subtitles.items()
        self._data['subtitle'] = dict(data)
        return self

    def set_content_available(self, value: bool):
        """ Sending true wakes your app from background to run custom native code """
        self._data['content_available'] = value
        return self

    def set_mutable_content(self, value: bool):
        """ Sending true allows you to change the notification
        content in your app before it is displayed. """
        self._data['mutable_content'] = value
        return self

    def add_data(self, data: dict):
        """
        :param data: A custom map of data that is passed back to your app
        Example: {"abc": "123", "foo": "bar"}
        """
        self._data['data'] = data
        return self

    def add_url(self, url: str):
        """
        :param url: The URL to open in the browser when a user clicks on the notification.
        """
        self._data['url'] = url
        return self

    def set_ios_attachments(self, attachments: dict):
        """
        Adds media attachments to notifications. Set as JSON object,
        key as a media id of your choice and the value as a valid
        local filename or URL. User must press and hold on the notification to view.
        :param attachments: attachments for your ios client
        Example: {"id1": "https://domain.com/image.jpg"}
        """
        self._data['ios_attachemtns'] = attachments
        return self

    def set_bit_picture(self, picture: str):
        """
        Picture to display in the expanded view.
        :param picture: Picture to display in the expanded view.
        """
        self._data['bit_picture'] = picture
        return self

    def set_adm_big_picture(self, picture: str):
        """
        Picture to display in the expanded view.
        :param picture: Picture to display in the expanded view.
        """
        self._data['adm_big_picture'] = picture
        return self

    def set_chrome_big_picture(self, picture: str):
        """
        Large picture to display below the notification text.
        :param picture: Must be a local URL.
        """
        self._data['chrome_big_picture'] = picture
        return self


class NotificationCenter:

    _url = 'https://onesignal.com/api/v1/notifications'

    def __init__(self, app_id: str, api_key: str):
        """
        Initiate a new notification center
        For app_id and api_key refer to: https://goo.gl/NzpytH
        :param app_id: onesignal's app id
        :param api_key: onesignal's rest api key
        """
        self._app_id = app_id
        self._api_key = api_key

    def post(self, notification: Notification):
        """
        submit a notification to the api
        :param notification: notification instance
        :return: (not decided yet)
        """
        pass

    def cancel(self, notification_id: str):
        """
        cancel a notification using its notification id
        :param notification_id: notification's id
        :return: (not decided yet)
        """
        pass