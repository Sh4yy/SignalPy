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


class Notification:
    pass


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

    def _base_filter(self, key, relation: Relation, value):
        """
        base filter generator
        :param key: filter key
        :param relation: filter's relation
        :param value: filter's value
        """
        self._values.append({'key': key, 'relation': relation.value, 'value': value})
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
        self._base_filter(key, relation, value)

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
